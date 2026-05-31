"""
벡터 스토어 서비스 — 3.file_manage 와 동일 (add / list / delete).
REST API 버전이라 화면 로직은 없지만, 도메인 로직(서비스 계층)은 그대로 재사용.

  ※ app.py(1단계) 는 add_pdf / list_files 만 쓰고,
    app2_delete.py(2단계) 가 delete_file 까지 씁니다.
"""

import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

DATA_DIR        = "./DATA"
PERSIST_DIR     = "./chroma_db"
COLLECTION_NAME = "rag_api"        # 템플릿 버전(rag_web) 과 DB 분리

os.makedirs(DATA_DIR, exist_ok=True)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR,
)


def add_pdf(file_path: str):
    docs = PyPDFLoader(file_path).load()
    for d in docs:
        d.metadata["source"] = os.path.basename(file_path)
    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_documents(docs)
    store.add_documents(chunks)


def is_empty() -> bool:
    return store._collection.count() == 0


def search_with_score(question: str, k: int = 5, sources: list[str] | None = None):
    """sources 가 주어지면 그 파일들 안에서만 검색 (metadata.source 필터).
    None/빈 리스트면 전체 문서 대상. → app3_select.py(3단계) 에서 사용."""
    where = {"source": {"$in": sources}} if sources else None
    return store.similarity_search_with_score(question, k=k, filter=where)


def list_files() -> list[str]:
    """DATA_DIR 의 파일 목록"""
    if not os.path.isdir(DATA_DIR):
        return []
    return sorted([f for f in os.listdir(DATA_DIR)
                   if os.path.isfile(os.path.join(DATA_DIR, f))])


def delete_file(filename: str):
    """벡터 + 원본 파일 함께 삭제 — app2_delete.py(2단계) 에서 사용"""
    # 1) 벡터 삭제 — metadata.source 가 일치하는 청크들
    store._collection.delete(where={"source": filename})

    # 2) 원본 파일 삭제
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
