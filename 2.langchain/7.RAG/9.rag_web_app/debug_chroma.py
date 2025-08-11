# pip install langchain-openai langchain-chroma chromadb python-dotenv

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

VECTOR_DB = "./chroma_db"
COLLECTION_NAME = "my-data"

load_dotenv()

def open_store() -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=VECTOR_DB,
        embedding_function=OpenAIEmbeddings(),  # 기본: text-embedding-3-small
    )

def seed_if_empty(store: Chroma):
    if store._collection.count() > 0:
        return
    docs = [
        Document(page_content="스마트카 보안은 차량 내 통신과 OTA 업데이트 보안이 핵심입니다.",
                 metadata={"source": "seed", "page": 0}),
        Document(page_content="ISMS는 조직의 보안 정책과 절차를 표준화합니다.",
                 metadata={"source": "seed", "page": 1}),
    ]
    store.add_documents(docs)
    store.persist()
    print("[INFO] 샘플 문서를 추가했습니다.")

def peek_embeddings(store: Chroma, limit: int = 5):
    """ids는 자동 반환되므로 include에 넣지 않습니다."""
    coll = store._collection
    out = coll.get(limit=limit, include=["embeddings", "documents", "metadatas"])

    ids   = out.get("ids", [])
    embs  = out.get("embeddings", [])
    docs  = out.get("documents", [])
    metas = out.get("metadatas", [])

    n = min(len(ids), len(embs))
    
    print(f"\n[EMBED PREVIEW] rows={len(ids)}")
    
    for i in range(n):
        id_ = ids[i]
        emb = embs[i]
        # NumPy/리스트 모두 대응
        emb_list = emb.tolist() if hasattr(emb, "tolist") else list(emb)
        dim  = len(emb_list)
        head = emb_list[:8]
        print(f"  {i+1}. id={id_} | dim={dim} | head={head}")
        if i < len(docs) and docs[i]:
            print(f"     doc: {docs[i][:70].replace('\\n',' ')}")
        if i < len(metas):
            print(f"     meta: {metas[i]}")

def search(store: Chroma, query: str, k: int = 3):
    print(f"\n[SEARCH] {query!r}")
    
    results = store.similarity_search_with_score(query, k=k)
    if not results:
        print("  결과 없음")
        return
    
    for i, (doc, dist) in enumerate(results, 1):
        sim_pct = max(0.0, min(1.0, 1.0 - float(dist))) * 100.0  # distance→유사도(%)
        prev = doc.page_content[:60].replace("\n", " ")
        print(f"  {i}. dist={dist:.4f} | sim={sim_pct:.2f}% | {prev}...")

if __name__ == "__main__":
    store = open_store()
    seed_if_empty(store)

    peek_embeddings(store, limit=5)          # ← 문서 peek

    search(store, "스마트카 보안")
    search(store, "ISMS 정책")
