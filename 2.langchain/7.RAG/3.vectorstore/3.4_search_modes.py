"""
검색 모드 비교 — similarity / with_score / MMR.
이 예제: 같은 질문에 세 검색 모드를 적용해 결과를 비교합니다.

  - similarity_search           : 가장 가까운 N 개. 점수 안 보여줌
  - similarity_search_with_score: 점수도 함께 (Chroma 는 거리 — 작을수록 가까움)
  - MMR (Maximal Marginal Relevance) : 관련성 + 다양성. 비슷한 청크 중복 방지
"""

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

store = Chroma(
    collection_name="storage_demo",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
    persist_directory="./chroma_db",
)

query = "NVMe 의 속도와 인터페이스"

# 1) similarity_search — 가장 단순 / 기본
print("=" * 60)
print("(1) similarity_search — 점수 없음")
print("=" * 60)
for d in store.similarity_search(query, k=3):
    print(f"  → {d.page_content[:80]}...")

# 2) similarity_search_with_score — 점수 포함 (Chroma 는 거리, 작을수록 유사)
print("\n" + "=" * 60)
print("(2) similarity_search_with_score — 점수(거리) 포함")
print("=" * 60)
for d, score in store.similarity_search_with_score(query, k=3):
    # 거리 → 대략적 유사도(%) 변환 (참고용, 정확한 공식은 아님)
    sim_pct = 100 / (1 + max(score, 0))
    print(f"  거리 {score:.3f} (유사도 ≈ {sim_pct}%)  {d.page_content[:60]}...")

# 3) MMR — 다양성 보장
# 같은 의미의 비슷한 청크들이 top-k 를 다 차지하지 않게,
# 첫 결과는 가장 관련성 높은 것, 그 다음부터는 이전 결과들과 다른 것 우선.
print("\n" + "=" * 60)
print("(3) MMR — 관련성 + 다양성")
print("=" * 60)
for d in store.max_marginal_relevance_search(query, k=3, fetch_k=10, lambda_mult=0.5):
    print(f"  → {d.page_content[:80]}...")

# 어떤 걸 쓸까?
#   - 일반:        similarity_search (기본)
#   - 점수 필요:   with_score (임계값으로 필터링 가능)
#   - 긴 문서:     MMR (중복 청크 회피로 컨텍스트 다양성 ↑)
