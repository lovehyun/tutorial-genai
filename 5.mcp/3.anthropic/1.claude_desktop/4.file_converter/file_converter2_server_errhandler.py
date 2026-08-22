# -*- coding: utf-8 -*-
"""
file_converter_server.py — Minimal MCP server (FastMCP)
- 지원 포맷: .pdf / .txt / .docx
- DOCX는 옵션(convert_docx=True)일 때만 PDF로 변환 → 원문 폴더 내 CONVERTED/ 저장
- 검색 결과 + 요약(summary) + 오류 샘플(errors) 반환
- stdout에는 JSON-RPC만 흘러야 하므로, MuPDF 콘솔 출력은 비활성화
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import os

from mcp.server.fastmcp import FastMCP

# ----- 콘솔 오염 방지: MuPDF 자체 에러 출력 비활성화 (환경변수 + 런타임) -----
os.environ["MUPDF_DISPLAY_ERRORS"] = "0"
try:
    import fitz  # PyMuPDF
    fitz.TOOLS.mupdf_display_errors(False)
except Exception:
    # PyMuPDF가 없거나 초기화 실패해도 서버 구동엔 영향 없음(필요시 함수 내부에서 import)
    pass
# ---------------------------------------------------------------------------

mcp = FastMCP("file-converter")

# === 지원 포맷 정의 ===
SUPPORTED_EXTS = {".pdf", ".txt", ".docx"}  # "문서"로 간주하는 확장자
READABLE_EXTS  = {".pdf", ".txt"}           # 변환 없이 바로 읽을 수 있는 포맷

# === 유틸 함수들 ===
def downloads() -> Path:
    """기본 루트 경로: 사용자 Downloads 폴더"""
    return Path.home() / "Downloads"

def converted_dir(src: Path) -> Path:
    """원본 문서와 같은 폴더 밑에 CONVERTED/ 폴더를 보장"""
    out = src.parent / "CONVERTED"
    out.mkdir(exist_ok=True)
    return out

def read_pdf(path: Path) -> str:
    """PDF 텍스트 추출 (암호/손상/특수 페이지는 조용히 처리)"""
    try:
        import fitz
        try:
            # 방어적: 함수 호출 시에도 재차 비활성화
            fitz.TOOLS.mupdf_display_errors(False)
        except Exception:
            pass
        with fitz.open(str(path)) as doc:
            # 암호/보호 문서는 건너뜀
            if bool(getattr(doc, "needs_pass", False)) or bool(getattr(doc, "is_encrypted", False)):
                raise RuntimeError("encrypted_or_password_required")
            texts: List[str] = []
            for page in doc:
                try:
                    texts.append(page.get_text("text") or "")
                except Exception:
                    # 일부 페이지 추출 실패는 무시
                    continue
            return "\n".join(texts)
    except Exception as e:
        # 원인 태그를 포함해 호출측에서 기록하게 함
        msg = getattr(e, "args", [""])[0]
        raise RuntimeError(f"pdf_read_failed:{msg}")

def read_txt(path: Path) -> str:
    """TXT 본문 읽기 (깨진 인코딩은 무시)"""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        msg = getattr(e, "args", [""])[0]
        raise RuntimeError(f"txt_read_failed:{msg}")

def try_convert_docx(path: Path) -> Optional[Path]:
    """
    DOCX → PDF 변환 시도
    - 성공 시: 같은 폴더의 CONVERTED/에 <이름>.pdf 저장하고 경로 반환
    - 실패/미설치: 예외 발생(RuntimeError) → 호출부에서 errors에 기록
    """
    if path.suffix.lower() != ".docx":
        return None
    try:
        from docx2pdf import convert  # Word 필요(Windows)
    except ImportError:
        raise RuntimeError("docx2pdf_not_installed")

    out_pdf = converted_dir(path) / (path.stem + ".pdf")
    if out_pdf.exists():
        return out_pdf

    try:
        # docx2pdf는 보통 원본 폴더에 <이름>.pdf를 생성
        convert(str(path))
        made = path.with_suffix(".pdf")
        if made.exists():
            made.replace(out_pdf)  # CONVERTED/로 이동
            return out_pdf
        raise RuntimeError("docx2pdf_output_missing")
    except Exception as e:
        msg = getattr(e, "args", [""])[0]
        raise RuntimeError(f"docx2pdf_failed:{msg}")

def snippets(text: str, keyword: str, context: int = 50) -> List[str]:
    """본문에서 keyword 주변으로 앞뒤 context 글자씩 최대 3개 발췌"""
    low, key = text.lower(), keyword.lower()
    res: List[str] = []
    i = 0
    while True:
        i = low.find(key, i)
        if i == -1:
            break
        s, e = max(0, i - context), min(len(text), i + len(keyword) + context)
        res.append(text[s:e].replace("\n", " "))
        if len(res) >= 3:
            break
        i += len(keyword)
    return res

# === MCP Tool ===
@mcp.tool()
def find(
    query: str,
    root_dir: Optional[str] = None,
    convert_docx: bool = False,
    max_results: int = 10,
    include_errors: bool = True,
    errors_limit: int = 10,
) -> Dict[str, Any]:
    """
    키워드 검색
    - query: 검색어
    - root_dir: 시작 폴더(없으면 Downloads)
    - convert_docx: True면 DOCX→PDF 변환 시도
    - max_results: 반환 결과 파일 수 제한
    - include_errors/errors_limit: 오류 샘플 제어
    """
    base = Path(root_dir or downloads())

    results: List[Dict[str, Any]] = []
    summary: Dict[str, Any] = {
        "root": str(base),
        "supported_exts": sorted(list(SUPPORTED_EXTS)),
        "eligible": {  # 트리에서 발견한 "대상 문서 파일" 개수
            "total": 0,
            "by_ext": {".pdf": 0, ".txt": 0, ".docx": 0},
        },
        "processed": {  # 본문 추출 성공 파일 수
            "total": 0,
            "by_ext": {".pdf": 0, ".txt": 0},
        },
        "converted": {"docx_to_pdf": 0},  # DOCX→PDF 성공 수
        "hits": {"total": 0, "returned": 0},
        "skipped": {
            "encrypted": 0,       # 암호/보호 PDF
            "need_conversion": 0  # DOCX인데 변환 비허용
        },
        "errors": 0
    }
    errors: List[Dict[str, str]] = []

    for p in base.rglob("*"):
        if not p.is_file():
            continue

        ext = p.suffix.lower()

        # 1) 지원 포맷 필터: 비지원은 완전히 무시
        if ext not in SUPPORTED_EXTS:
            continue

        # 대상 문서 개수 카운트
        summary["eligible"]["total"] += 1
        summary["eligible"]["by_ext"][ext] += 1

        try:
            # 2) DOCX 처리 (옵션)
            if ext == ".docx":
                if not convert_docx:
                    summary["skipped"]["need_conversion"] += 1
                    continue
                try:
                    pdf = try_convert_docx(p)
                    if pdf:
                        summary["converted"]["docx_to_pdf"] += 1
                        p, ext = pdf, ".pdf"  # 변환된 PDF로 이어서 처리
                    else:
                        summary["errors"] += 1
                        if include_errors and len(errors) < errors_limit:
                            errors.append({"path": str(p), "reason": "docx_convert_no_output"})
                        continue
                except RuntimeError as ce:
                    summary["errors"] += 1
                    if include_errors and len(errors) < errors_limit:
                        errors.append({"path": str(p), "reason": str(ce)})
                    continue

            # 3) 여기부터는 읽기 가능한 포맷(.pdf/.txt)만
            if ext not in READABLE_EXTS:
                continue

            # 4) 본문 추출
            try:
                text = read_pdf(p) if ext == ".pdf" else read_txt(p)
            except RuntimeError as re:
                reason = str(re)
                if "encrypted_or_password_required" in reason:
                    summary["skipped"]["encrypted"] += 1
                else:
                    summary["errors"] += 1
                    if include_errors and len(errors) < errors_limit:
                        errors.append({"path": str(p), "reason": reason})
                continue

            # 5) processed 집계
            summary["processed"]["total"] += 1
            summary["processed"]["by_ext"][ext] += 1

            # 6) 스니펫 추출 및 결과 수집
            hits = snippets(text, query)
            if hits:
                summary["hits"]["total"] += 1
                if len(results) < max_results:
                    results.append({"path": str(p), "snippets": hits})

        except Exception as e:
            summary["errors"] += 1
            if include_errors and len(errors) < errors_limit:
                errors.append({"path": str(p), "reason": f"unexpected:{getattr(e, 'args', [''])[0]}"})
            continue

    summary["hits"]["returned"] = len(results)

    out: Dict[str, Any] = {"ok": True, "results": results, "summary": summary}
    if include_errors:
        out["errors"] = errors
    return out

# === 서버 실행 ===
if __name__ == "__main__":
    mcp.run()
