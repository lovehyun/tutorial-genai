"""예제 파일 탐색 및 분류."""

import ast
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .constants import (
    API_KEY_PATTERNS,
    HEAVY_DEPS_PATTERNS,
    INPUT_PATTERNS,
    REPO_ROOT,
    SCAN_DIRS,
    SERVICE_PATTERNS,
    SKIP_PATTERNS,
)


class Category(Enum):
    """파일 분류 카테고리."""

    SAFE_RUNNABLE = "safe_runnable"
    NEEDS_API_KEY = "needs_api_key"
    NEEDS_SERVICE = "needs_service"
    NEEDS_INPUT = "needs_input"
    NEEDS_HEAVY_DEPS = "needs_heavy_deps"


@dataclass
class FileInfo:
    """스캔된 파일 정보."""

    path: Path
    relative_path: str
    category: Category
    skip_reason: str = ""


def _should_skip(path: Path) -> bool:
    """SKIP_PATTERNS에 해당하는 경로인지 확인."""
    path_str = str(path)
    return any(pattern in path_str for pattern in SKIP_PATTERNS)


def _has_main_guard(source: str) -> bool:
    """if __name__ == '__main__' 블록이 있는지 확인."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            # if __name__ == "__main__" 패턴 탐지
            test = node.test
            if isinstance(test, ast.Compare) and len(test.comparators) == 1:
                left = test.left
                comp = test.comparators[0]
                if (
                    isinstance(left, ast.Name)
                    and left.id == "__name__"
                    and isinstance(comp, ast.Constant)
                    and comp.value == "__main__"
                ):
                    return True
    return False


def classify(path: Path) -> tuple[Category, str]:
    """파일을 카테고리로 분류. (category, skip_reason) 반환."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return Category.SAFE_RUNNABLE, f"읽기 실패: {e}"

    # 우선순위: SERVICE > INPUT > API_KEY > HEAVY_DEPS > SAFE_RUNNABLE
    for pattern in SERVICE_PATTERNS:
        if pattern in source:
            return Category.NEEDS_SERVICE, f"서비스 패턴: {pattern}"

    for pattern in INPUT_PATTERNS:
        if pattern in source:
            return Category.NEEDS_INPUT, f"입력 대기 패턴: {pattern}"

    for pattern in API_KEY_PATTERNS:
        if pattern in source:
            return Category.NEEDS_API_KEY, f"API 키 패턴: {pattern}"

    for pattern in HEAVY_DEPS_PATTERNS:
        if pattern in source:
            return Category.NEEDS_HEAVY_DEPS, f"무거운 의존성: {pattern}"

    return Category.SAFE_RUNNABLE, ""


def scan_all_files() -> list[FileInfo]:
    """SCAN_DIRS에서 모든 .py 파일을 탐색하고 분류."""
    files: list[FileInfo] = []

    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if not dir_path.is_dir():
            continue

        for py_file in sorted(dir_path.rglob("*.py")):
            if _should_skip(py_file):
                continue

            relative = str(py_file.relative_to(REPO_ROOT))
            category, skip_reason = classify(py_file)
            files.append(
                FileInfo(
                    path=py_file,
                    relative_path=relative,
                    category=category,
                    skip_reason=skip_reason,
                )
            )

    return files
