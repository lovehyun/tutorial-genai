"""
codebase-QA 변형: 실제 레포 문서(0.docs/)를 코퍼스로 쓰는 RAG MCP 서버.
server.py(자체 포함 data/, InMemory)와 차이:
  - 코퍼스가 큼 → Chroma 로 '영속화'해서 재시작 시 재임베딩 비용 0
  - CORPUS_DIR 환경변수로 어떤 문서 폴더든 지정 가능 (기본: 레포의 0.docs)
  - 하위 폴더까지 재귀적으로 *.md 수집 (.venv / site-packages / __pycache__ 등은 제외)

도구는 server.py 와 동일: search(query,k) / answer(question) + resource corpus://info

준비:
  pip install mcp langchain-openai langchain-community langchain-text-splitters langchain-chroma chromadb python-dotenv
  .env 에 OPENAI_API_KEY
  ※ 첫 실행은 0.docs 전체를 임베딩하므로 시간이 걸립니다(이후는 캐시).

다른 폴더로 바꾸려면:
  CORPUS_DIR=/path/to/docs python server_docs.py
  (코퍼스를 바꾸면 chroma_db 를 지우고 재인덱싱하세요.)
"""

import os
import glob
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document       # (구) langchain_community.TextLoader 대신 — sunset 의존성 제거
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
# 기본 코퍼스 = 레포 루트의 0.docs  (HERE 에서 세 단계 위가 레포 루트)
DEFAULT_CORPUS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "0.docs"))
CORPUS_DIR = os.getenv("CORPUS_DIR", DEFAULT_CORPUS)

PERSIST_DIR = os.path.join(HERE, "chroma_db")
COLLECTION = "repo_docs"

# 코퍼스에서 제외할 디렉토리 (가상환경/패키지/캐시의 .md 가 섞이지 않게)
SKIP = {".venv", "venv", "node_modules", "__pycache__", "site-packages", ".git", "pdf_output"}

mcp = FastMCP("codebase-qa-docs")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = Chroma(
    collection_name=COLLECTION,
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR,
)


def _index_corpus():
    docs = []
    for path in sorted(glob.glob(os.path.join(CORPUS_DIR, "**", "*.md"), recursive=True)):
        parts = set(os.path.normpath(path).split(os.sep))
        if parts & SKIP:
            continue
        text = open(path, encoding="utf-8").read()
        docs.append(Document(page_content=text, metadata={"source": os.path.relpath(path, CORPUS_DIR)}))
    chunks = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120).split_documents(docs)
    store.add_documents(chunks)
    return len(docs), len(chunks)


# 비어 있으면 1회 인덱싱 (영속화돼 있으면 건너뜀)
if store._collection.count() == 0:
    n_docs, n_chunks = _index_corpus()
else:
    n_docs, n_chunks = None, store._collection.count()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def _format(results):
    return "\n\n".join(
        f"[{d.metadata.get('source', '?')}] {d.page_content}" for d in results
    )


@mcp.tool()
def search(query: str, k: int = 4) -> str:
    """레포 문서(0.docs)에서 query 와 의미적으로 가까운 청크 k개를 출처(상대경로)와 함께 반환한다."""
    results = store.similarity_search(query, k=k)
    return _format(results) if results else "검색 결과가 없습니다."


@mcp.tool()
def answer(question: str) -> str:
    """레포 문서를 근거로 question 에 답한다 (RAG). 문서에 근거가 없으면 '문서에 없습니다'라고 답한다."""
    context = _format(store.similarity_search(question, k=4))
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "당신은 이 교육 레포 문서 기반 QA 도우미입니다. 아래 문서만 근거로 답하고, "
         "근거가 없으면 '문서에 없습니다'라고 답하세요. 답 끝에 참고한 [출처]를 적으세요.\n\n문서:\n{context}"),
        ("user", "{question}"),
    ])
    return (prompt | llm).invoke({"context": context, "question": question}).content


@mcp.resource("corpus://info")
def corpus_info() -> str:
    """코퍼스 위치와 청크 수."""
    return f"코퍼스: {CORPUS_DIR}\n청크 {store._collection.count()}개 (영속: {PERSIST_DIR})"


if __name__ == "__main__":
    mcp.run()
