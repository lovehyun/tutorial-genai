"""
벡터 스토어 서비스 — #2 + 파일 목록 / 삭제.
이 예제: list_files / delete_file 추가. 파일 삭제 시 벡터까지 함께 정리.
"""

import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

DATA_DIR        = "./DATA"
PERSIST_DIR     = "./chroma_db"
COLLECTION_NAME = "rag_web"

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


def search_with_score(question: str, k: int = 5):
    return store.similarity_search_with_score(question, k=k)


# ─── #3 신규 ─────────────────────────────────────────
def list_files() -> list[str]:
    """DATA_DIR 의 파일 목록"""
    if not os.path.isdir(DATA_DIR):
        return []
    return sorted([f for f in os.listdir(DATA_DIR)
                   if os.path.isfile(os.path.join(DATA_DIR, f))])


def delete_file(filename: str):
    """벡터 + 원본 파일 함께 삭제"""
    # 1) 벡터 삭제 — metadata.source 가 일치하는 청크들
    store._collection.delete(where={"source": filename})

    # 2) 원본 파일 삭제
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
