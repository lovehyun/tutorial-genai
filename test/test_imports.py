"""모든 .py 파일의 top-level import 가용성 검증."""

import ast
import subprocess

import pytest

from conftest import get_all_files
from utils.constants import PYTHON

_files = get_all_files()

# 모듈 import 결과 캐시: module_name -> (success, error_msg)
_import_cache: dict[str, tuple[bool, str]] = {}


def _extract_imports(source: str) -> list[str]:
    """AST로 top-level import 모듈명 추출."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    modules = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # 최상위 패키지명만 추출 (e.g., "os.path" → "os")
                top = alias.name.split(".")[0]
                modules.append(top)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                top = node.module.split(".")[0]
                modules.append(top)
    return sorted(set(modules))


def _check_import(module: str) -> tuple[bool, str]:
    """모듈 import 가능 여부 확인 (캐시 사용)."""
    if module in _import_cache:
        return _import_cache[module]

    try:
        result = subprocess.run(
            [str(PYTHON), "-c", f"import {module}"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        success = result.returncode == 0
        error = result.stderr.strip() if not success else ""
        _import_cache[module] = (success, error)
    except subprocess.TimeoutExpired:
        _import_cache[module] = (False, "import timeout (15s)")
    except Exception as e:
        _import_cache[module] = (False, str(e))

    return _import_cache[module]


@pytest.mark.imports
@pytest.mark.parametrize(
    "file_info",
    _files,
    ids=[f.relative_path for f in _files],
)
def test_imports(file_info):
    """파일의 top-level import가 모두 설치되어 있는지 확인."""
    source = file_info.path.read_text(encoding="utf-8", errors="replace")
    modules = _extract_imports(source)

    if not modules:
        return  # import가 없으면 통과

    failed = []
    for module in modules:
        success, error = _check_import(module)
        if not success:
            failed.append(f"  {module}: {error}")

    if failed:
        pytest.fail(
            f"Import failures in {file_info.relative_path}:\n" + "\n".join(failed)
        )
