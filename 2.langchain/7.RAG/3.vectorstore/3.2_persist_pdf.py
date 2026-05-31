"""
Chroma 영속화 (PDF 버전) — PDF 도 똑같이 디스크에 저장해 재실행 시 재임베딩 안 함.
이 예제: 3.1 과 같은 흐름인데 로더만 TextLoader → PyPDFLoader 로 교체합니다.

3.1(txt) 과의 차이는 딱 두 줄:
  - 로더:   TextLoader → PyPDFLoader
  - 단위:   PDF 는 "1 페이지 = Document 1개" 로 먼저 쪼개진 뒤 청킹됨

  ※ pip install langchain-chroma chromadb pypdf
"""

import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from langchain_chroma import Chroma

load_dotenv()

PDF_PATH        = "../DATA/하계학술대회(CISC-S'24) CFP v2.pdf"
PERSIST_DIR     = "./chroma_db"
COLLECTION_NAME = "pdf_demo"

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def build_store():
    """PDF 로드 → 청킹 → 임베딩 → Chroma 에 저장"""
    docs   = PyPDFLoader(PDF_PATH).load()          # ★ 페이지별 Document 리스트
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_documents(docs)

    store = Chroma.from_documents(
        chunks, embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIR,
    )
    print(f"새 DB 생성 — PDF {len(docs)} 페이지 → {len(chunks)} 청크 임베딩 저장")
    return store


def load_store():
    """디스크에서 기존 DB 로드 (임베딩 재계산 없음)"""
    store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR,
    )
    print(f"기존 DB 로드 — {store._collection.count()} 청크 있음")
    return store


# 같은 컬렉션이 이미 디스크에 있으면 로드, 없으면 새로 생성
existing = Chroma(collection_name=COLLECTION_NAME, embedding_function=embeddings, persist_directory=PERSIST_DIR)
store = existing if existing._collection.count() > 0 else build_store()

# 검색 동작 확인 — PDF 청크에는 page 메타데이터가 붙어있음
results = store.similarity_search("논문 제출 일정?", k=2)
for d in results:
    page = d.metadata.get("page", "?")
    print(f"  [p.{page}] {d.page_content[:60]}...")

# 이 스크립트를 두 번 연속 실행해보세요.
# 첫 실행: "새 DB 생성"  /  두 번째: "기존 DB 로드" — 임베딩 API 호출 없음
