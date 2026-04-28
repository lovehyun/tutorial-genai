"""SAFE_RUNNABLE 파일의 실행(smoke) 테스트."""

import os
import subprocess

import pytest

from conftest import get_safe_runnable_files
from utils.constants import PYTHON

_files = get_safe_runnable_files()


def _make_clean_env() -> dict[str, str]:
    """API 키를 제거한 깨끗한 환경변수 생성."""
    env = os.environ.copy()
    # API 키 관련 환경변수 제거 (실수로 API 호출 방지)
    keys_to_remove = [
        k
        for k in env
        if any(
            pattern in k.upper()
            for pattern in ["API_KEY", "API_TOKEN", "SECRET", "CREDENTIAL"]
        )
    ]
    for k in keys_to_remove:
        del env[k]
    return env


@pytest.mark.smoke
@pytest.mark.parametrize(
    "file_info",
    _files,
    ids=[f.relative_path for f in _files],
)
def test_smoke(file_info):
    """SAFE_RUNNABLE 파일을 실행하여 정상 종료 확인."""
    env = _make_clean_env()

    try:
        result = subprocess.run(
            [str(PYTHON), str(file_info.path)],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
            cwd=str(file_info.path.parent),
        )
    except subprocess.TimeoutExpired:
        pytest.fail(f"Timeout (30s): {file_info.relative_path}")
        return

    if result.returncode != 0:
        stderr_snippet = result.stderr[:500] if result.stderr else "(no stderr)"
        pytest.fail(
            f"Non-zero exit ({result.returncode}): {file_info.relative_path}\n"
            f"stderr: {stderr_snippet}"
        )

    if "Traceback (most recent call last)" in result.stderr:
        stderr_snippet = result.stderr[:500]
        pytest.fail(
            f"Traceback detected: {file_info.relative_path}\n"
            f"stderr: {stderr_snippet}"
        )
