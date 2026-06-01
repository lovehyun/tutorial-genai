"""
벡터 스토어 서비스 — #4(4.with_score) 의 도메인 로직을 그대로 재사용.
REST API 버전이라 화면 로직은 없지만, 서비스 계층(add/list/delete/search)은 동일.

  ※ app.py(1단계)        : add_pdf / list_documents
    app2_delete.py(2단계) : + delete_document
    app3_select.py(3단계) : + search_with_score(sources=...) 로 문서 선택 검색
"""

import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

DATA_DIR        = "../DATA"         # 1~5 공유 (= 8.web_app/DATA)
PERSIST_DIR     = "../chroma_db"    # 벡터 DB 도 8.web_app 안에서 공유
COLLECTION_NAME = "rag_api"        # 같은 chroma_db 안에서 컬렉션만 분리(rag_web 과 별개)

os.makedirs(DATA_DIR, exist_ok=True)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR,
)


def _distinct_sources() -> dict:
    """벡터 DB 안의 문서별 청크 수를 {파일명: 청크수} 로 집계."""
    data = store._collection.get(include=["metadatas"])
    counts: dict[str, int] = {}
    for m in data.get("metadatas", []):
        src = (m or {}).get("source", "(unknown)")
        counts[src] = counts.get(src, 0) + 1
    return counts


def list_documents() -> list[dict]:
    """벡터 DB 에 들어있는 문서 목록 (파일명 + 청크 수)."""
    return [{"source": s, "chunks": c}
            for s, c in sorted(_distinct_sources().items())]


def add_pdf(file_path: str) -> dict:
    """PDF 를 청킹해서 벡터 DB 에 추가. 이미 있는 문서면 건너뜀."""
    source = os.path.basename(file_path)
    if source in _distinct_sources():
        return {"source": source, "added": False}

    docs = PyPDFLoader(file_path).load()
    for d in docs:
        d.metadata["source"] = source
    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_documents(docs)
    store.add_documents(chunks)
    return {"source": source, "added": True}


def delete_document(source: str) -> bool:
    """문서 1건 삭제 — 해당 source 의 벡터 청크 제거 (원본 PDF 는 보존).

    원본까지 지우려면 아래 주석 해제.
    """
    existed = source in _distinct_sources()
    store._collection.delete(where={"source": source})

    # path = os.path.join(DATA_DIR, source)
    # if os.path.exists(path):
    #     os.remove(path)

    return existed


def is_empty() -> bool:
    return store._collection.count() == 0


def search_with_score(question: str, k: int = 5, sources: list[str] | None = None):
    """sources 가 주어지면 그 파일들 안에서만 검색 (metadata.source 필터).
    None/빈 리스트면 전체 문서 대상. → app3_select.py(3단계) 에서 사용."""
    where = {"source": {"$in": sources}} if sources else None
    return store.similarity_search_with_score(question, k=k, filter=where)
