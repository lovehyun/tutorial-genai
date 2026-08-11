"""
mini-context7 — 실제 context7(https://context7.com)의 핵심 흐름을 재현한 MCP 서버.

context7이 하는 일의 본질: "라이브러리 이름"만으로는 문서를 못 준다(모호함) →
  1) resolve_library_id(이름)      로 정확한 Context7 호환 ID(`/org/project`)를 먼저 찾고
  2) get_library_docs(그 ID)       로만 문서를 내준다
두 도구로 나눠 이 계약을 강제한다. RAG(../3.codebase_qa)와 달리 의미 검색이 아니라
"정확한 식별자로 찾기"가 핵심이라 임베딩·LLM이 필요 없다 — 이 서버는 API 키가 필요 없다.

준비:
  pip install mcp
  (API 키 불필요 — 이 서버는 LLM도 임베딩도 쓰지 않는다)

단독 점검:
  pip install "mcp[cli]"
  mcp dev server.py
"""

import difflib
import glob
import os

from mcp.server.fastmcp import FastMCP

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")

# 데모용 카탈로그 — 실제 context7은 이 자리에 수천 개 라이브러리를 지속적으로 크롤링해 채운다.
LIBRARIES = {
    "/psf/requests": {
        "name": "Requests",
        "aliases": ["requests", "python requests", "http client", "http 클라이언트"],
        "description": "Python 용 사람 친화적 HTTP 클라이언트 라이브러리",
        "doc_dir": "requests",
    },
    "/tiangolo/fastapi": {
        "name": "FastAPI",
        "aliases": ["fastapi", "fast api", "파이썬 웹 프레임워크"],
        "description": "타입 힌트 기반의 파이썬 async 웹 프레임워크, 자동 OpenAPI 문서 생성",
        "doc_dir": "fastapi",
    },
    "/modelcontextprotocol/python-sdk": {
        "name": "MCP Python SDK",
        "aliases": ["mcp", "mcp python sdk", "model context protocol sdk", "fastmcp"],
        "description": "Model Context Protocol 서버/클라이언트를 만드는 공식 파이썬 SDK",
        "doc_dir": "mcp-python-sdk",
    },
}

mcp = FastMCP("mini-context7")


def _score(query: str, lib: dict) -> float:
    q = query.lower().strip()
    candidates = [lib["name"].lower()] + [a.lower() for a in lib["aliases"]]
    best = 0.0
    for c in candidates:
        if q == c:
            return 1.0
        if q in c or c in q:
            best = max(best, 0.85)
        best = max(best, difflib.SequenceMatcher(None, q, c).ratio())
    return best


@mcp.tool()
def resolve_library_id(libraryName: str) -> str:
    """라이브러리/패키지 이름으로 Context7 호환 라이브러리 ID를 찾는다.
    get_library_docs 를 호출하기 전에 반드시 먼저 이 도구로 정확한 ID를 확인해야 한다 —
    단, 사용자가 이미 '/org/project' 형식의 정확한 ID를 제시한 경우는 예외."""
    scored = sorted(
        ((lib_id, lib, _score(libraryName, lib)) for lib_id, lib in LIBRARIES.items()),
        key=lambda t: t[2],
        reverse=True,
    )
    top = [t for t in scored if t[2] >= 0.3][:3] or scored[:1]

    lines = [f"검색어 '{libraryName}' 에 대한 매칭 결과:\n"]
    for lib_id, lib, score in top:
        n_docs = len(glob.glob(os.path.join(DATA_DIR, lib["doc_dir"], "*.md")))
        lines.append(
            f"- Context7-compatible library ID: {lib_id}\n"
            f"  이름: {lib['name']}\n"
            f"  설명: {lib['description']}\n"
            f"  문서 스니펫 수: {n_docs}\n"
            f"  매칭 점수: {score:.2f}"
        )
    lines.append("\n가장 위 결과가 가장 유력합니다. get_library_docs 호출 시 위 ID를 그대로 쓰세요.")
    return "\n".join(lines)


@mcp.tool()
def get_library_docs(context7_compatible_library_id: str, topic: str = "", tokens: int = 4000) -> str:
    """Context7 호환 라이브러리 ID로 문서를 가져온다.
    반드시 resolve_library_id 가 반환한 정확한 ID('/org/project' 형식)를 써야 한다 —
    이 값을 모르면 먼저 resolve_library_id 를 호출한다.
    topic 을 주면 관련 섹션만 좁혀서 반환하고, tokens 는 반환할 문서의 최대 길이 예산이다."""
    lib = LIBRARIES.get(context7_compatible_library_id)
    if lib is None:
        return (
            f"알 수 없는 라이브러리 ID '{context7_compatible_library_id}' 입니다.\n"
            "먼저 resolve_library_id(libraryName) 를 호출해 정확한 Context7 ID를 확인하세요."
        )

    paths = sorted(glob.glob(os.path.join(DATA_DIR, lib["doc_dir"], "*.md")))
    if topic:
        t = topic.lower()
        filtered = [p for p in paths if t in open(p, encoding="utf-8").read().lower()]
        paths = filtered or paths  # 못 찾으면 전체 문서로 폴백

    chunks = [
        f"### 출처: {lib['name']}/{os.path.basename(p)}\n{open(p, encoding='utf-8').read()}"
        for p in paths
    ]
    full = "\n\n".join(chunks) if chunks else "(문서 없음)"

    if len(full) > tokens:
        full = full[:tokens] + f"\n\n...(생략됨 — 총 {len(full)}자 중 {tokens}자만 표시. tokens 값을 늘리면 더 볼 수 있다)"

    return full


@mcp.resource("context7://libraries")
def list_libraries() -> str:
    """등록된 라이브러리 전체 목록 (실제 context7의 카탈로그에 해당)."""
    lines = ["등록된 라이브러리:\n"]
    for lib_id, lib in LIBRARIES.items():
        lines.append(f"- {lib_id}  —  {lib['name']}: {lib['description']}")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
