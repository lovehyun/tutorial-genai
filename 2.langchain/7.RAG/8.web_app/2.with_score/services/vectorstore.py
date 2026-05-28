"""
벡터 스토어 서비스 — #1 의 PDF 추가 로직을 별도 모듈로 분리.
이 예제: app.py 가 비대해지지 않게 도메인 로직을 services/ 에 둠.
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
    """점수와 함께 검색 — #1 의 단순 search 와 다른 점"""
    return store.similarity_search_with_score(question, k=k)
