"""
MMR 심화 — '다양성' 이 실제로 어떻게 작동하는지 눈으로 보기.
이 예제: 같은 사실을 말만 바꾼 '거의 중복' 청크를 잔뜩 넣고,
         similarity 와 MMR 의 결과 차이 + lambda_mult 효과를 비교합니다.

  (3.4 는 세 모드를 '소개', 여기 3.4-2 는 MMR 하나만 '깊게')

MMR(Maximal Marginal Relevance):
  - 매 단계에서 (질문과의 관련성) - λ 패널티(이미 뽑은 것과의 유사도) 가 최대인 청크 선택
  - 즉, 관련은 있되 '앞에서 뽑은 것과 다른' 청크를 우선 → 중복 회피, 컨텍스트 다양성 ↑
  - similarity 는 점수순이라 '같은 말 반복' 청크가 top-k 를 독식할 수 있다 (아래서 확인)
"""

from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# [관전 포인트 1] '속도' 한 가지를 말만 바꿔 5번 반복 + 서로 다른 사실 4개
#   질문이 '속도' 라서 similarity 는 위 5개(거의 중복)로 top-k 를 채우기 쉽다.
docs = [
    # ── 속도 클러스터 (거의 중복 — 같은 사실의 다른 표현) ──
    Document(page_content="NVMe SSD 는 매우 빠르다.",                    metadata={"topic": "speed"}),
    Document(page_content="NVMe SSD 의 읽기 속도는 굉장히 빠른 편이다.",  metadata={"topic": "speed"}),
    Document(page_content="NVMe 는 속도가 아주 빠른 저장장치다.",         metadata={"topic": "speed"}),
    Document(page_content="NVMe SSD 는 빠른 전송 속도를 자랑한다.",       metadata={"topic": "speed"}),
    Document(page_content="NVMe SSD 는 고속 데이터 전송이 가능하다.",     metadata={"topic": "speed"}),
    # ── 서로 다른 사실들 (다양성을 주는 청크) ──
    Document(page_content="NVMe 는 PCIe 인터페이스를 통해 연결된다.",      metadata={"topic": "interface"}),
    Document(page_content="NVMe SSD 의 수명은 보통 TBW 로 표기한다.",      metadata={"topic": "lifespan"}),
    Document(page_content="NVMe SSD 는 주로 M.2 폼팩터로 제공된다.",       metadata={"topic": "form"}),
    Document(page_content="SATA SSD 는 NVMe 보다 전송 속도가 느린 편이다.", metadata={"topic": "compare"}),
]

store = Chroma.from_documents(docs, embeddings, collection_name="mmr_demo")

query = "NVMe SSD 의 속도는 얼마나 빠른가?"


def show(title, results):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    for d in results:
        print(f"  [{d.metadata['topic']:9}] {d.page_content}")


# [관전 포인트 2] similarity — 점수순 top-3 → '속도' 중복 청크가 자리를 독식
show("(1) similarity_search (k=3) — 중복 청크가 top-k 독식",
     store.similarity_search(query, k=3))

# [관전 포인트 3] MMR — fetch_k 로 넉넉히 후보를 뽑은 뒤, 다양하게 k개 추림
#   fetch_k(후보 풀, 기본 20) 가 k 보다 충분히 커야 '고를 여지' 가 생긴다.
#   같은 질문인데 topic 이 speed 하나가 아니라 여러 개로 퍼지는지 보라.
show("(2) MMR (k=3, fetch_k=9, lambda_mult=0.5) — 다양성 확보",
     store.max_marginal_relevance_search(query, k=3, fetch_k=9, lambda_mult=0.5))


# [관전 포인트 4] lambda_mult — 관련성 vs 다양성의 손잡이 (0.0 ~ 1.0)
#   1.0 = 관련성만 (≈ similarity, 중복 허용) / 0.0 = 다양성만 (관련성 거의 무시)
print("\n" + "#" * 60)
print("lambda_mult 스윕 — 1.0 에서 0.0 으로 갈수록 다양해진다")
print("#" * 60)
for lm in [1.0, 0.7, 0.3, 0.0]:
    results = store.max_marginal_relevance_search(query, k=3, fetch_k=9, lambda_mult=lm)
    topics = [d.metadata["topic"] for d in results]
    print(f"  λ={lm:>3} → {topics}")


# [관전 포인트 5] 체인에서 쓰려면 retriever 로 — search_type='mmr'
#   4.rag_chain 의 retriever 자리에 그대로 끼워 넣으면 된다.
retriever = store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 3, "fetch_k": 9, "lambda_mult": 0.5},
)
show("(3) as_retriever(search_type='mmr') — 체인에 끼울 형태",
     retriever.invoke(query))


store.delete_collection()


# 정리 — 언제 MMR?
#   - 청크 overlap 이 크거나, 같은 내용이 여러 문서에 흩어져 'top-k 가 다 비슷' 할 때
#   - 통합 컬렉션에서 한 소스가 점수를 독식해 다른 소스가 밀릴 때 (3.vectorstore/README 참고)
#   손잡이: k(최종 개수) / fetch_k(후보 풀, 클수록 고를 여지 ↑) / lambda_mult(1=관련성, 0=다양성)


# ─────────────────────────────────────────────────────────────────────
# 실제 실행 결과 (예시 — 임베딩 점수에 따라 순서는 조금씩 다를 수 있음)
#
#   (1) similarity_search (k=3) — 중복 청크가 top-k 독식
#     [speed    ] NVMe SSD 는 매우 빠르다.
#     [speed    ] NVMe SSD 의 읽기 속도는 굉장히 빠른 편이다.
#     [speed    ] NVMe 는 속도가 아주 빠른 저장장치다.
#       → 세 개가 전부 'speed' = 같은 말 반복. 컨텍스트로선 비효율.
#
#   (2) MMR (k=3, fetch_k=9, lambda_mult=0.5) — 다양성 확보
#     [speed    ] NVMe SSD 는 매우 빠르다.
#     [compare  ] SATA SSD 는 NVMe 보다 전송 속도가 느린 편이다.
#     [interface] NVMe 는 PCIe 인터페이스를 통해 연결된다.
#       → 'speed' 1개 + 다른 topic 2개 = 같은 k=3 인데 정보량이 더 풍부.
#
#   lambda_mult 스윕:
#     λ=1.0 → ['speed', 'speed', 'speed']      (관련성만 → similarity 와 유사)
#     λ=0.7 → ['speed', 'compare', 'speed']
#     λ=0.3 → ['speed', 'compare', 'interface']
#     λ=0.0 → ['speed', 'form', 'lifespan']    (다양성만 → 관련성 약한 것도 들어옴)
#
#   ▷ 관전 포인트: λ 를 낮출수록 같은 'speed' 반복이 빠지고 다른 topic 이 들어온다.
#     너무 낮으면(0.0) 질문(속도)과 덜 관련된 form/lifespan 까지 올라옴 → 보통 0.5 안팎.
# ─────────────────────────────────────────────────────────────────────
