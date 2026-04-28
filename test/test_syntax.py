"""모든 .py 파일의 문법(syntax) 검증."""

import ast

import pytest

from conftest import get_all_files

_files = get_all_files()


@pytest.mark.syntax
@pytest.mark.parametrize(
    "file_info",
    _files,
    ids=[f.relative_path for f in _files],
)
def test_syntax(file_info):
    """ast.parse로 Python 문법 오류를 검출."""
    source = file_info.path.read_text(encoding="utf-8", errors="replace")
    try:
        ast.parse(source, filename=str(file_info.path))
    except SyntaxError as e:
        pytest.fail(
            f"SyntaxError in {file_info.relative_path}\n"
            f"  Line {e.lineno}: {e.msg}"
        )
