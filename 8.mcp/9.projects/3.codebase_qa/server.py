"""
프로젝트: codebase-QA — 레포의 RAG 를 'MCP 서버' 로 노출한다.
이 서버는 data/ 폴더의 문서를 인덱싱하고, 두 개의 도구를 제공한다:
  - search(query, k)   : 의미적으로 가까운 청크 k개를 출처와 함께 반환 (검색만)
  - answer(question)   : 검색 + LLM 으로 문서 근거 답변 생성 (완전한 RAG)

핵심 아이디어:
  RAG 를 한 번 'MCP 서버' 로 만들어 두면, GPT(2.openai) · Claude(3.anthropic) ·
  LangChain(4.langchain) · VSCode(5.vscode) 어디서든 같은 "문서 QA" 능력을 재사용할 수 있다.
  → 이 폴더의 1.client_raw.py / 2.client_langchain.py 가 그 예시.

준비:
  pip install mcp langchain-openai langchain-community langchain-text-splitters python-dotenv
  .env 에 OPENAI_API_KEY  (서버 시작 시 임베딩을 만든다)

단독 점검:
  pip install "mcp[cli]"
  mcp dev server.py        # Inspector 에서 search / answer 호출
"""

import os
import glob
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")

mcp = FastMCP("codebase-qa")


# ─── 인덱싱 (서버 시작 시 1회) ──────────────────────────────
def _build_index():
    docs = []
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "*.md"))):
        loaded = TextLoader(path, encoding="utf-8").load()
        for d in loaded:
            d.metadata["source"] = os.path.basename(path)
        docs += loaded
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=100
    ).split_documents(docs)
    store = InMemoryVectorStore.from_documents(
        chunks, OpenAIEmbeddings(model="text-embedding-3-small")
    )
    return store, chunks


store, _chunks = _build_index()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def _format(results):
    return "\n\n".join(
        f"[{d.metadata.get('source', '?')}] {d.page_content}" for d in results
    )


# ─── 도구 ──────────────────────────────────────────────────
@mcp.tool()
def search(query: str, k: int = 3) -> str:
    """문서 코퍼스에서 query 와 의미적으로 가장 가까운 청크 k개를 출처와 함께 반환한다 (검색만, 생성 없음)."""
    results = store.similarity_search(query, k=k)
    return _format(results) if results else "검색 결과가 없습니다."


@mcp.tool()
def answer(question: str) -> str:
    """코퍼스를 근거로 question 에 답한다 (RAG: 검색 + 생성). 문서에 근거가 없으면 '문서에 없습니다'라고 답한다."""
    context = _format(store.similarity_search(question, k=3))
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "아래 문서만 근거로 답하세요. 문서에 없으면 '문서에 없습니다'라고 답하세요.\n\n문서:\n{context}"),
        ("user", "{question}"),
    ])
    return (prompt | llm).invoke({"context": context, "question": question}).content


# ─── 리소스 — 무엇이 인덱싱됐는지 ──────────────────────────
@mcp.resource("corpus://info")
def corpus_info() -> str:
    """인덱싱된 문서 목록과 청크 수."""
    files = sorted({d.metadata.get("source", "?") for d in _chunks})
    listing = "\n".join(f"- {f}" for f in files)
    return f"문서 {len(files)}개, 청크 {len(_chunks)}개\n{listing}"


if __name__ == "__main__":
    mcp.run()   # stdio — 어떤 MCP 클라이언트든 이 서버에 붙을 수 있다
