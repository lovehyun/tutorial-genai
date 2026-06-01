"""
혼합 소스 → 컬렉션 전략 — txt 2개 + pdf 2개를, 목적에 따라 컬렉션에 다르게 배치.
이 예제: 같은 주제의 txt 2개는 한 컬렉션에 묶고, 성격이 다른 pdf 2개는 각각 별도 컬렉션에 둡니다.

  배치:
    storage        ← nvme.txt + ssd.txt   (같은 '저장장치' 주제 → 한 컬렉션)
    secure_coding  ← 시큐어코딩 가이드 PDF  (독립 주제 → 단독 컬렉션)
    cfp            ← 학술대회 CFP PDF        (독립 주제 → 단독 컬렉션)

핵심 질문: "이렇게 나눠 담으면 검색은 어떻게 되나? 다 같은 store 로 한 번에 검색되나?"
  → 아니오. Chroma 에서 '컬렉션' = 독립된 검색 공간.
    같은 persist_directory(=같은 물리 DB 폴더) 를 공유해도, 한 번의 similarity_search 는
    '그 컬렉션 안' 만 뒤집니다. 여러 컬렉션을 한꺼번에 보려면 각각 검색해서 합쳐야 함.

  ※ pip install langchain-chroma chromadb pypdf
"""

import os
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

PERSIST_DIR = "./chroma_db"
embeddings  = OpenAIEmbeddings(model="text-embedding-3-small")
splitter    = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)


def load_any(path: str):
    """확장자로 로더 자동 선택 — .pdf 면 PyPDFLoader, 그 외엔 TextLoader"""
    if path.lower().endswith(".pdf"):
        return PyPDFLoader(path).load()
    return TextLoader(path, encoding="utf-8").load()


def build_if_missing(paths: list[str], collection: str):
    """컬렉션이 비어있으면 paths 의 파일들을 모두 로드해 적재, 있으면 로드만"""
    store = Chroma(collection_name=collection, embedding_function=embeddings, persist_directory=PERSIST_DIR)
    if store._collection.count() > 0:
        return store

    chunks = []
    for path in paths:
        docs = load_any(path)
        part = splitter.split_documents(docs)
        for c in part:
            c.metadata["source"] = os.path.basename(path)   # 출처 파일명 부착
        chunks += part

    return Chroma.from_documents(
        chunks, embeddings,
        collection_name=collection,
        persist_directory=PERSIST_DIR,
    )


# 1) 컬렉션 3개 구성 — txt 2개는 묶어서, pdf 2개는 각각 따로
collections = {
    "storage":       build_if_missing(["../DATA/nvme.txt", "../DATA/ssd.txt"], "storage"),
    "secure_coding": build_if_missing(["../DATA/Python_시큐어코딩_가이드(2023년_개정본).pdf"], "secure_coding"),
    "cfp":           build_if_missing(["../DATA/하계학술대회(CISC-S'24) CFP v2.pdf"], "cfp"),
}
for name, store in collections.items():
    print(f"  '{name}' 컬렉션: {store._collection.count()} 청크")


# 2) 한 컬렉션만 검색 — 그 컬렉션 안의 청크만 후보가 됨
def search_in(name: str, query: str, k=3):
    return collections[name].similarity_search(query, k=k)


# 3) 모든 컬렉션을 가로질러 검색 → 결과를 직접 합침
#    (Chroma 는 컬렉션 경계를 자동으로 넘지 않으므로 우리가 합쳐줘야 함)
def search_all(query: str, k_per=2):
    merged = []
    for name, store in collections.items():
        for doc in store.similarity_search(query, k=k_per):
            doc.metadata["collection"] = name
            merged.append(doc)
    return merged


print("\n" + "=" * 60)
print("(A) 'storage' 컬렉션에서만 검색 — txt 2개만 후보")
print("=" * 60)
for d in search_in("storage", "NVMe 와 SATA 의 속도 차이"):
    print(f"  [{d.metadata.get('source')}] {d.page_content[:55]}...")

print("\n" + "=" * 60)
print("(B) 'storage' 에 '시큐어코딩' 을 물어보면? — 그 컬렉션엔 그 내용이 없음")
print("=" * 60)
# 컬렉션 경계 밖이라, 관련 없는 청크가 (억지로) 끌려나옵니다 = '엉뚱한 답'의 원인
for d in search_in("storage", "안전한 패스워드 저장 방법"):
    print(f"  [{d.metadata.get('source')}] {d.page_content[:55]}...")

print("\n" + "=" * 60)
print("(C) 모든 컬렉션 통합 검색 — 각 컬렉션을 따로 친 뒤 합침")
print("=" * 60)
for d in search_all("안전한 패스워드 저장 방법"):
    print(f"  [{d.metadata['collection']:13}] {d.page_content[:50]}...")

# 정리:
#   - 컬렉션 = 독립된 검색 공간. 한 번의 검색은 한 컬렉션만 본다 (A, B).
#   - 여러 컬렉션을 같이 보려면 각각 검색 후 합친다 (C) → search_all 패턴.
#   - "주제별로 나눌까(이 파일) vs 한 컬렉션에 source 메타로 섞고 filter 로 거를까"
#     는 설계 선택. 교차 검색이 잦으면 한 컬렉션 + filter 가 단순할 때도 많음.
