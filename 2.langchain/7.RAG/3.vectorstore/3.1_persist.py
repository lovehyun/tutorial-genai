"""
Chroma 영속화 — 임베딩을 디스크에 저장해서 재실행 시 다시 만들지 않게.
이 예제: 같은 파일을 두 번 실행해도, 두 번째는 기존 DB 를 로드만 합니다.

InMemoryVectorStore(1.basics) 와의 차이:
  - InMemory  : 프로세스 종료 시 사라짐. 매번 임베딩 재생성 → API 비용 ↑
  - Chroma    : persist_directory 에 저장. 재실행 시 즉시 로드 → 비용 0

  ※ pip install langchain-chroma chromadb
"""

import os
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from langchain_chroma import Chroma

load_dotenv()

PERSIST_DIR     = "./chroma_db"
COLLECTION_NAME = "storage_demo"

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def build_store():
    """문서 로드 → 청킹 → 임베딩 → Chroma 에 저장"""
    docs   = TextLoader("../DATA/nvme.txt", encoding="utf-8").load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_documents(docs)

    store = Chroma.from_documents(
        chunks, embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIR,
    )
    print(f"새 DB 생성 — {len(chunks)} 청크 임베딩 저장")
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


# 디스크에 컬렉션이 이미 있으면 로드, 없으면 새로 만들기
if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
    store = load_store()
else:
    store = build_store()

# 검색 동작 확인
results = store.similarity_search("NVMe 의 인터페이스?", k=2)
for d in results:
    print(f"  → {d.page_content[:60]}...")

# 이 스크립트를 두 번 연속 실행해보세요.
# 첫 실행: "새 DB 생성"
# 두 번째: "기존 DB 로드" — 임베딩 API 호출 없음
