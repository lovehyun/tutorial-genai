"""
FAISS vs Chroma — 같은 RAG 흐름을 FAISS 로 짜보면서 차이를 체감.
이 예제: 동일 데이터를 FAISS 에 저장/로드/검색하고, Chroma 대비 어디서 손이 더 가는지 비교.

  ※ pip install faiss-cpu


─── 왜 이 폴더 (그리고 7.RAG 전체) 는 ChromaDB 만 썼나? ─────────

| 항목 | ChromaDB | FAISS |
|---|---|---|
| 영속화 | persist_directory 한 줄 | save_local + load_local (pickle) |
| 메타데이터 필터 | where={"source": ...} 네이티브 지원 | 약함 — 직접 후처리 / 단순 dict 필터만 |
| 삭제 | collection.delete(where={...}) 한 줄 | id 매핑 관리 + 인덱스 재구축 |
| 컬렉션 분리 | collection_name 으로 여러 인덱스 | 인덱스 파일 별도 관리 |
| 설치 / 실행 | pip install (서버 불필요) | pip install (서버 불필요) |
| 속도 | 수만~수십만 벡터 충분 | 수백만~수억 벡터에서 압도적 (GPU 지원) |
| 메모리 | 디스크 기반 (SQLite + Parquet) | 기본 in-memory |

학습 / MVP / 일반 실무 RAG 의 대부분은 ChromaDB 가 더 매끄럽습니다 — RAG 의
핵심은 "메타데이터로 출처를 추적하고 삭제·필터링하는 일" 인데 그 부분이 풍부해서.
FAISS 는 **대규모 벡터 검색 / GPU 가속이 필요한 경우** 강점.

  Chroma 가 잘 맞는 곳:
    - 학습·튜토리얼·MVP
    - 출처·페이지·날짜 같은 메타 필터링이 잦은 일반 RAG
    - 파일 업로드/삭제 같은 라이프사이클 관리가 필요한 웹앱

  FAISS 가 잘 맞는 곳:
    - 수백만~수억 벡터 (예: 전사 검색, 이미지 임베딩)
    - GPU 메모리에 인덱스 띄워야 하는 초고속 응답
    - 메타데이터가 거의 없고 순수 유사도만 필요한 경우


다른 옵션들도 참고:
  Pinecone / Weaviate / Qdrant : 매니지드 / 프로덕션
  pgvector                     : 이미 PostgreSQL 쓰는 경우
  Milvus                       : 대규모 자체 호스팅
"""

import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

load_dotenv()

FAISS_DIR  = "./faiss_db"
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


# ─── 1) 인덱스 만들기 — Chroma 와 거의 같은 흐름 ──────
def build_index():
    docs = TextLoader("../DATA/nvme.txt", encoding="utf-8").load() \
         + TextLoader("../DATA/ssd.txt",  encoding="utf-8").load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_documents(docs)
    for c in chunks:
        c.metadata["source"] = os.path.basename(c.metadata.get("source", "?"))

    store = FAISS.from_documents(chunks, embeddings)

    # ★ 차이 1: 영속화는 명시적 호출. Chroma 는 persist_directory 만 주면 자동.
    store.save_local(FAISS_DIR)
    print(f"FAISS 인덱스 생성 + 저장 → {FAISS_DIR}/  ({len(chunks)} 벡터)")
    return store


# ─── 2) 인덱스 로드 ───────────────────────────────────
def load_index():
    # ★ 차이 2: pickle 역직렬화이므로 allow_dangerous_deserialization 명시 필요.
    store = FAISS.load_local(
        FAISS_DIR,
        embeddings,
        allow_dangerous_deserialization=True,
    )
    print(f"FAISS 인덱스 로드 — {store.index.ntotal} 벡터")
    return store


if os.path.exists(FAISS_DIR) and os.listdir(FAISS_DIR):
    store = load_index()
else:
    store = build_index()


# ─── 3) 기본 검색 — 인터페이스는 Chroma 와 동일 ──────
print("\n=== 기본 검색 (similarity_search) — 인터페이스 동일 ===")
for d in store.similarity_search("NVMe 와 SATA 의 차이?", k=3):
    print(f"  [{d.metadata.get('source')}] {d.page_content[:60]}...")


# ─── 4) 메타데이터 필터링 — FAISS 의 약점 ─────────────
# Chroma: store.similarity_search(q, filter={"source": "nvme.txt"})  ← 깔끔
# FAISS : 단순 dict 필터는 가능하지만 표현력이 약함 (and/or, $gt 등 본격 쿼리는 부담).
#         복잡한 필터는 보통 retriever 후 후처리로 처리.
print("\n=== 메타데이터 필터 ===")

# (A) FAISS 가 지원하는 가벼운 filter
docs_a = store.similarity_search(
    "PCIe 인터페이스",
    k=3,
    filter={"source": "nvme.txt"},   # 가벼운 단일 키 필터까지는 OK
)
print(f"[FAISS filter 인자]   {len(docs_a)} 개")
for d in docs_a:
    print(f"  [{d.metadata.get('source')}] {d.page_content[:50]}...")

# (B) 복잡한 조건은 직접 후처리
all_docs = store.similarity_search("PCIe", k=10)
docs_b = [d for d in all_docs if d.metadata.get("source") in {"nvme.txt", "ssd.txt"}][:3]
print(f"\n[직접 후처리]         {len(docs_b)} 개")
for d in docs_b:
    print(f"  [{d.metadata.get('source')}] {d.page_content[:50]}...")


# ─── 5) 결론 ──────────────────────────────────────────
print("\n" + "=" * 60)
print("같은 데이터·비슷한 인터페이스인데도 영속화·필터링·삭제 단계에서 손이 더 갑니다.")
print("그래서 이 폴더(그리고 일반 실무 RAG)는 Chroma 를 기본으로 합니다.")
print("FAISS 는 대규모/GPU 가 핵심 가치인 시나리오에서 진가를 발휘합니다.")
