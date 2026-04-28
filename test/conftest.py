"""pytest 설정 및 공유 fixtures."""

import sys
from pathlib import Path

import pytest

# test/ 디렉토리를 sys.path에 추가 (stdlib test 패키지 충돌 방지)
sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.file_scanner import Category, scan_all_files  # noqa: E402


def pytest_configure(config):
    """커스텀 마커 등록."""
    config.addinivalue_line("markers", "syntax: Syntax validation via ast.parse")
    config.addinivalue_line("markers", "imports: Import availability check")
    config.addinivalue_line("markers", "smoke: Smoke test for safe-runnable files")


# 세션 레벨 캐시 (parametrize에서 사용하기 위해 모듈 레벨에서 수집)
_all_files = None
_safe_runnable_files = None


def get_all_files():
    """전체 파일 리스트 (캐시됨)."""
    global _all_files
    if _all_files is None:
        _all_files = scan_all_files()
    return _all_files


def get_safe_runnable_files():
    """SAFE_RUNNABLE 카테고리 파일만 필터 (캐시됨)."""
    global _safe_runnable_files
    if _safe_runnable_files is None:
        _safe_runnable_files = [
            f for f in get_all_files() if f.category == Category.SAFE_RUNNABLE
        ]
    return _safe_runnable_files


@pytest.fixture(scope="session")
def all_python_files():
    """전체 Python 파일 리스트."""
    return get_all_files()


@pytest.fixture(scope="session")
def safe_runnable_files():
    """안전하게 실행 가능한 파일 리스트."""
    return get_safe_runnable_files()
