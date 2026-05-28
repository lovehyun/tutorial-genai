"""
다중 컬렉션 — 서로 다른 주제의 문서를 별도 컬렉션에 보관하고 골라서 검색.
이 예제: nvme.txt, ssd.txt 를 각각 다른 컬렉션에 저장하고, 타겟 지정 / 통합 검색을 모두 보여줍니다.

언제 쓰나:
  - 주제별 분리 (저장소 / 운영서버 / 네트워크 등)
  - 사용자별 분리 (각 사용자가 업로드한 문서를 격리)
"""

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

PERSIST_DIR = "./chroma_db"
embeddings  = OpenAIEmbeddings(model="text-embedding-3-small")
splitter    = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)


def build_if_missing(file_path: str, collection: str):
    """이미 있으면 로드만, 없으면 만들어서 저장"""
    store = Chroma(collection_name=collection, embedding_function=embeddings, persist_directory=PERSIST_DIR)
    if store._collection.count() > 0:
        return store

    docs   = TextLoader(file_path, encoding="utf-8").load()
    chunks = splitter.split_documents(docs)
    for c in chunks:
        c.metadata["source"] = os.path.basename(file_path)

    return Chroma.from_documents(
        chunks, embeddings,
        collection_name=collection,
        persist_directory=PERSIST_DIR,
    )


# 1) 컬렉션 두 개 준비
collections = {
    "nvme": build_if_missing("../DATA/nvme.txt", "nvme"),
    "ssd":  build_if_missing("../DATA/ssd.txt",  "ssd"),
}
for name, store in collections.items():
    print(f"  '{name}' 컬렉션: {store._collection.count()} 청크")


# 2) 특정 컬렉션만 검색
def search_in(name: str, query: str, k=2):
    return collections[name].similarity_search(query, k=k)


# 3) 모든 컬렉션에 같은 질문 던지고 통합
def search_all(query: str, k_per=2):
    results = []
    for name, store in collections.items():
        for doc in store.similarity_search(query, k=k_per):
            doc.metadata["collection"] = name   # 어디서 왔는지 기록
            results.append(doc)
    return results


query = "PCIe 인터페이스 속도"

print("\n=== 'nvme' 컬렉션에서만 ===")
for d in search_in("nvme", query):
    print(f"  → {d.page_content[:70]}...")

print("\n=== 모든 컬렉션 통합 ===")
for d in search_all(query):
    print(f"  [{d.metadata['collection']}] {d.page_content[:60]}...")
