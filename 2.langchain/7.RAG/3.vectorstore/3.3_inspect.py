"""
Chroma DB 검사 — 저장된 컬렉션 안에 뭐가 들어있는지 들여다보기.
이 예제: count / get 으로 문서 개수 확인, 샘플 출력 (디버깅용 유틸).

3.1 을 한 번 실행해 ./chroma_db 가 만들어진 뒤 실행하세요.
"""

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

PERSIST_DIR     = "./chroma_db"
COLLECTION_NAME = "storage_demo"

store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
    persist_directory=PERSIST_DIR,
)

# 1) 전체 문서 개수
count = store._collection.count()
print(f"컬렉션 '{COLLECTION_NAME}' 의 문서 수: {count}\n")

# 2) 일부 문서 샘플 — get(limit=N) 으로 그냥 가져오기 (검색 아님)
#    ★ embeddings 는 기본 제외라서, 벡터를 보려면 include 에 직접 넣어야 함
results = store._collection.get(include=["documents", "metadatas"], limit=3)

print("=== 샘플 3 개 ===")
for i, (doc_id, content, meta) in enumerate(
    zip(results["ids"], results["documents"], results["metadatas"]),
    start=1,
):
    print(f"[{i}] id={doc_id[:8]}...")
    print(f"    내용: {content[:80]}...")
    print(f"    메타: {meta}")



# 참고 - 백터까지 출력
results = store._collection.get(include=["documents", "metadatas", "embeddings"], limit=3)
for i, (doc_id, content, meta, vec) in enumerate(
    zip(results["ids"], results["documents"], results["metadatas"], results["embeddings"]),
    start=1,
):
    print(f"[{i}] id={doc_id[:8]}...")
    print(f"    내용: {content[:80]}...")
    print(f"    메타: {meta}")
    # 1536 차원 전부 찍으면 화면이 넘치니 앞 8 개만 — 이게 '의미의 좌표' 임
    head = ", ".join(f"{v:+.4f}" for v in vec[:8])
    print(f"    벡터: {len(vec)} 차원 [{head}, ...]\n")
