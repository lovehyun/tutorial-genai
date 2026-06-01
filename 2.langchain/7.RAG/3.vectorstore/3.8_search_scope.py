"""
검색 스코프(search scope) — 같은 데이터를 통합/분리로 두고 검색이 어떻게 달라지나.
이 예제: nvme/ssd 를 ① 한 컬렉션(통합) ② 컬렉션 분리(따로) 두 방식으로 만들어,
검색 결과가 어떻게 달라지는지 (특히 top-k 가 통합인지 각각인지) 비교합니다.

핵심 한 줄:
  similarity_search 한 번이 보는 범위 = 한 컬렉션.
    같이 검색  → 한 컬렉션에 넣는다 (필요하면 filter 로 그때그때 좁힘)   ← 3.6_unified 적재 방식
    따로 검색  → 컬렉션을 나눈다 (통합하려면 각각 검색 후 합침)          ← 3.5_sep / 3.7 적재 방식

동작 원리 — 두 컬렉션을 검색하면 '통합 top-k' 인가 '각각' 인가?
  ① 한 컬렉션(통합, 아래 1): similarity_search(k=3) = 그 컬렉션의 모든 청크를 한
     후보 풀에 놓고 점수순 정렬 → 상위 3개. 이게 '진짜' 전역 top-k.
  ② 컬렉션 분리 후 단순 merge(아래 2-b): 컬렉션마다 '각자' top-k 를 뽑아 이어붙일 뿐.
     - nvme 에서 top-2, ssd 에서 top-2 → 합쳐서 4개 (k_per × 컬렉션 수).
     - 전역 재정렬이 아님! ssd 의 1등이 nvme 의 2등보다 점수가 낮아도 둘 다 포함.
     - 즉 "각 컬렉션에서 k_per 개씩" 이지, "전체에서 top-k" 가 아니다.
  ③ 분리해놓고 '진짜 전역 top-k' 가 필요하면(아래 2-c): 각 컬렉션을 with_score 로
     뽑아 → 점수로 합쳐 정렬 → 상위 k 개만 컷. (각 컬렉션에서 k 개씩 뽑으면
     전역 top-k 가 그 안에 반드시 들어오므로 정확함.)
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


def chunks_of(path: str):
    """파일 → 청크 (출처 태그 부착)"""
    part = splitter.split_documents(TextLoader(path, encoding="utf-8").load())
    for c in part:
        c.metadata["source"] = os.path.basename(path)
    return part


def get_or_build(name: str, paths: list[str]):
    """컬렉션이 비어있으면 paths 의 파일들로 채우고, 있으면 로드만"""
    store = Chroma(collection_name=name, embedding_function=embeddings, persist_directory=PERSIST_DIR)
    if store._collection.count() > 0:
        return store
    docs = []
    for p in paths:
        docs += chunks_of(p)
    return Chroma.from_documents(docs, embeddings, collection_name=name, persist_directory=PERSIST_DIR)


query = "PCIe 인터페이스 속도"
FILES = ["../DATA/nvme.txt", "../DATA/ssd.txt"]
K = 3

# ── 전략 1) 통합: 한 컬렉션에 둘 다 → '진짜' 전역 top-k ──
unified = get_or_build("scope_unified", FILES)
print("=" * 60)
print("(1) 통합 — 한 컬렉션, 모든 청크가 한 후보 풀에서 경쟁 → 전역 top-3")
print("=" * 60)
for d in unified.similarity_search(query, k=K):
    print(f"  [{d.metadata.get('source')}] {d.page_content[:55]}...")

# ── 전략 1-b) 통합인데 특정 파일만: filter ──────────────
print("\n(1-b) 같은 컬렉션이지만 filter 로 nvme.txt 만")
for d in unified.similarity_search(query, k=K, filter={"source": "nvme.txt"}):
    print(f"  [{d.metadata.get('source')}] {d.page_content[:55]}...")


# ── 전략 2) 분리: 파일마다 별도 컬렉션 ──────────────────
nvme = get_or_build("scope_nvme", ["../DATA/nvme.txt"])
ssd  = get_or_build("scope_ssd",  ["../DATA/ssd.txt"])
print("\n" + "=" * 60)
print("(2) 분리 — nvme 컬렉션만 검색 (ssd 는 후보에 아예 없음)")
print("=" * 60)
for d in nvme.similarity_search(query, k=K):
    print(f"  [{d.metadata.get('source')}] {d.page_content[:55]}...")

# ── 전략 2-b) 단순 merge — '각 컬렉션에서 k_per 개씩' (전역 top-k 아님!) ─
print("\n(2-b) 각 컬렉션 top-2 를 그냥 이어붙임 → 2+2=4개, 점수순 정렬 아님")
merged = []
for name, store in {"nvme": nvme, "ssd": ssd}.items():
    for d in store.similarity_search(query, k=2):   # 각 컬렉션이 '각자' top-2
        d.metadata["collection"] = name
        merged.append(d)
for d in merged:
    print(f"  [{d.metadata['collection']}] {d.page_content[:50]}...")

# ── 전략 2-c) 점수로 재정렬 — 분리된 컬렉션에서 '진짜 전역 top-k' ─
print("\n(2-c) with_score 로 각각 K개 뽑아 → 점수로 합쳐 정렬 → 전체 top-3")
pool = []
for name, store in {"nvme": nvme, "ssd": ssd}.items():
    for doc, score in store.similarity_search_with_score(query, k=K):
        doc.metadata["collection"] = name
        pool.append((score, doc))
pool.sort(key=lambda x: x[0])               # Chroma 점수 = 거리, 작을수록 가까움 → 오름차순
for score, doc in pool[:K]:                 # 합친 뒤 상위 K 개만
    print(f"  [{doc.metadata['collection']}] 거리 {score:.3f}  {doc.page_content[:45]}...")


# 정리:
#   같이(1)  = 한 컬렉션 → 한 번의 검색이 곧 전역 top-k. 가장 단순.
#   따로(2)  = 컬렉션 분리. 통합하려면 직접 합쳐야 하고, 이때
#     - 단순 이어붙이기(2-b)는 '각 컬렉션 k_per 개씩'  (전역 순위 아님, 주의!)
#     - 전역 top-k 를 원하면 with_score 로 점수까지 받아 재정렬(2-c)
#   → 그래서 "통합 검색이 필요하면 처음부터 한 컬렉션(3.6)" 이 제일 편하다.
