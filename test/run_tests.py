"""테스트 CLI 오케스트레이터.

사용법:
    python test/run_tests.py              # 전체 테스트
    python test/run_tests.py --syntax-only
    python test/run_tests.py --imports-only
    python test/run_tests.py --smoke-only
    python test/run_tests.py --pytest      # raw pytest 출력
"""

import argparse
import ast
import os
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

# 직접 실행 시 import를 위해 test/ 디렉토리를 경로에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.constants import PYTHON, REPO_ROOT
from utils.file_scanner import Category, scan_all_files

LOG_FILE = Path(__file__).resolve().parent / "test_results.log"
LOG_MAX_KEEP = 10

# 결과 상수
PASS = "PASS"
FAIL = "FAIL"
TIMEOUT = "TIMEOUT"
SKIP = "SKIP"


# --- 개별 테스트 실행기 ---------------------------------------------------


def run_syntax_tests(files):
    """ast.parse로 문법 검증. [(status, file_info, elapsed, detail)] 반환."""
    results = []
    for f in files:
        t0 = time.time()
        try:
            source = f.path.read_text(encoding="utf-8", errors="replace")
            ast.parse(source, filename=str(f.path))
            elapsed = time.time() - t0
            results.append((PASS, f, elapsed, ""))
        except SyntaxError as e:
            elapsed = time.time() - t0
            results.append((FAIL, f, elapsed, f"Line {e.lineno}: {e.msg}"))
        except Exception as e:
            elapsed = time.time() - t0
            results.append((FAIL, f, elapsed, str(e)))
    return results


def _extract_imports(source):
    """AST로 top-level import 모듈명 추출."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    modules = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                modules.append(node.module.split(".")[0])
    return sorted(set(modules))


def run_import_tests(files):
    """import 가용성 검증. [(status, file_info, elapsed, detail)] 반환."""
    cache: dict[str, tuple[bool, str]] = {}
    results = []

    for f in files:
        t0 = time.time()
        source = f.path.read_text(encoding="utf-8", errors="replace")
        modules = _extract_imports(source)

        if not modules:
            elapsed = time.time() - t0
            results.append((PASS, f, elapsed, "no imports"))
            continue

        failed = []
        for mod in modules:
            if mod not in cache:
                try:
                    r = subprocess.run(
                        [str(PYTHON), "-c", f"import {mod}"],
                        capture_output=True, text=True, timeout=15,
                    )
                    cache[mod] = (r.returncode == 0, r.stderr.strip())
                except subprocess.TimeoutExpired:
                    cache[mod] = (False, "import timeout (15s)")
                except Exception as e:
                    cache[mod] = (False, str(e))

            ok, err = cache[mod]
            if not ok:
                failed.append(mod)

        elapsed = time.time() - t0
        if failed:
            results.append((FAIL, f, elapsed, f"missing: {', '.join(failed)}"))
        else:
            results.append((PASS, f, elapsed, ""))

    return results


def _make_clean_env():
    """API 키를 제거한 환경변수."""
    env = os.environ.copy()
    for k in list(env):
        if any(p in k.upper() for p in ["API_KEY", "API_TOKEN", "SECRET", "CREDENTIAL"]):
            del env[k]
    return env


def run_smoke_tests(files):
    """SAFE_RUNNABLE 파일 실행. [(status, file_info, elapsed, detail)] 반환."""
    env = _make_clean_env()
    results = []

    for f in files:
        if f.category != Category.SAFE_RUNNABLE:
            results.append((SKIP, f, 0.0, f"skip: {f.category.value}"))
            continue

        t0 = time.time()
        try:
            r = subprocess.run(
                [str(PYTHON), str(f.path)],
                capture_output=True, text=True, timeout=30,
                env=env, cwd=str(f.path.parent),
            )
            elapsed = time.time() - t0

            if r.returncode != 0 or "Traceback (most recent call last)" in r.stderr:
                output = (r.stderr or r.stdout)[:300]
                results.append((FAIL, f, elapsed, output))
            else:
                output = (r.stdout or "")[:200]
                results.append((PASS, f, elapsed, output))

        except subprocess.TimeoutExpired:
            elapsed = time.time() - t0
            results.append((TIMEOUT, f, elapsed, "Timeout after 30s"))

    return results


# --- 포맷팅 ---------------------------------------------------------------


def format_report(title, results, show_output=False):
    """결과를 읽기 쉬운 리포트 문자열로 변환."""
    lines = []
    counts = Counter(r[0] for r in results)
    total = len(results)

    # 헤더
    lines.append("=" * 70)
    lines.append(f" {title}")
    lines.append(f" 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)
    lines.append("")

    summary_parts = [f"총 {total}개 대상"]
    for status in [PASS, FAIL, TIMEOUT, SKIP]:
        if counts.get(status, 0) > 0:
            summary_parts.append(f"{status}: {counts[status]}")
    lines.append(", ".join(summary_parts))
    lines.append("")

    # 상세 결과
    lines.append("-" * 70)
    lines.append("상세 결과")
    lines.append("-" * 70)
    lines.append("")

    for status, f, elapsed, detail in results:
        lines.append(f"[{status}] {f.relative_path} ({elapsed:.2f}s)")
        if status == FAIL and detail:
            lines.append(f"  ERROR: {detail}")
        elif status == TIMEOUT and detail:
            lines.append(f"  ERROR: {detail}")
        elif status == SKIP and detail:
            lines.append(f"  {detail}")
        elif show_output and detail and status == PASS:
            snippet = detail.replace("\n", " ").strip()
            if snippet:
                lines.append(f"  OUTPUT: {snippet[:150]}")
        lines.append("")

    return "\n".join(lines)


# --- 로그 로테이션 --------------------------------------------------------


def rotate_log():
    """기존 로그 파일을 .1, .2, ... 로 번호를 올리고 최근 LOG_MAX_KEEP개만 유지."""
    if not LOG_FILE.exists():
        return

    # 가장 오래된 것부터 처리 (높은 번호 -> 낮은 번호)
    for i in range(LOG_MAX_KEEP, 0, -1):
        old = LOG_FILE.with_suffix(f".log.{i}")
        if old.exists():
            if i >= LOG_MAX_KEEP:
                old.unlink()
            else:
                old.rename(LOG_FILE.with_suffix(f".log.{i + 1}"))

    # 현재 로그를 .1로 이동
    LOG_FILE.rename(LOG_FILE.with_suffix(".log.1"))


# --- 메인 -----------------------------------------------------------------


def run_pytest_raw(markers, extra_args=None):
    """기존 방식: pytest 직접 호출 + raw 출력."""
    cmd = [str(PYTHON), "-m", "pytest"]
    if markers:
        cmd.extend(["-m", " or ".join(markers)])
    cmd.extend(["-v", "--tb=short"])
    if extra_args:
        cmd.extend(extra_args)

    print(f"\n실행: {' '.join(cmd)}\n")
    result = subprocess.run(
        cmd, cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    rotate_log()
    with open(LOG_FILE, "w", encoding="utf-8") as log:
        log.write(result.stdout)
    print(result.stdout)
    print(f"\n결과가 {LOG_FILE}에 저장되었습니다.")
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="예제 파일 테스트 실행기")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--syntax-only", action="store_true", help="문법 검증만 실행")
    group.add_argument("--imports-only", action="store_true", help="import 검증만 실행")
    group.add_argument("--smoke-only", action="store_true", help="smoke 테스트만 실행")
    group.add_argument("--all", action="store_true", default=True, help="전체 테스트 (기본)")
    parser.add_argument("--pytest", action="store_true", help="raw pytest 출력 모드")
    parser.add_argument("extra", nargs="*", help="pytest 모드에서 추가 인자")
    args = parser.parse_args()

    # pytest raw 모드
    if args.pytest:
        if args.syntax_only:
            return run_pytest_raw(["syntax"], args.extra)
        elif args.imports_only:
            return run_pytest_raw(["imports"], args.extra)
        elif args.smoke_only:
            return run_pytest_raw(["smoke"], args.extra)
        else:
            return run_pytest_raw([], args.extra)

    # 커스텀 포맷 모드
    files = scan_all_files()
    safe_files = [f for f in files if f.category == Category.SAFE_RUNNABLE]

    # 카테고리 요약
    counts = Counter(f.category.value for f in files)
    print("=" * 70)
    print(" 예제 파일 테스트 프레임워크")
    print("=" * 70)
    print(f" 총 파일 수: {len(files)}")
    for cat, cnt in sorted(counts.items()):
        print(f"  {cat:20s}: {cnt}")
    print("=" * 70)
    print()

    reports = []

    if args.syntax_only:
        print(">>> Syntax 검증 실행 중...")
        results = run_syntax_tests(files)
        report = format_report("Syntax 검증 결과", results)
        reports.append(report)
        print(report)
    elif args.imports_only:
        print(">>> Import 검증 실행 중...")
        results = run_import_tests(files)
        report = format_report("Import 검증 결과", results)
        reports.append(report)
        print(report)
    elif args.smoke_only:
        print(f">>> Smoke 테스트 실행 중 ({len(safe_files)}개 대상)...")
        results = run_smoke_tests(safe_files)
        report = format_report("Smoke 테스트 결과", results, show_output=True)
        reports.append(report)
        print(report)
    else:
        # 전체 실행
        print(">>> [1/3] Syntax 검증 실행 중...")
        r1 = run_syntax_tests(files)
        rpt1 = format_report("1. Syntax 검증 결과", r1)
        reports.append(rpt1)
        print(rpt1)

        print(">>> [2/3] Import 검증 실행 중...")
        r2 = run_import_tests(files)
        rpt2 = format_report("2. Import 검증 결과", r2)
        reports.append(rpt2)
        print(rpt2)

        print(f">>> [3/3] Smoke 테스트 실행 중 ({len(safe_files)}개 대상)...")
        r3 = run_smoke_tests(safe_files)
        rpt3 = format_report("3. Smoke 테스트 결과", r3, show_output=True)
        reports.append(rpt3)
        print(rpt3)

    # 로그 파일 저장 (기존 로그 로테이션 후)
    rotate_log()
    with open(LOG_FILE, "w", encoding="utf-8") as log:
        log.write("\n\n".join(reports))
    print(f"\n결과가 {LOG_FILE}에 저장되었습니다.")

    # 실패가 있으면 exit 1
    has_fail = any("FAIL:" in r for r in reports)
    return 1 if has_fail else 0


if __name__ == "__main__":
    sys.exit(main())
