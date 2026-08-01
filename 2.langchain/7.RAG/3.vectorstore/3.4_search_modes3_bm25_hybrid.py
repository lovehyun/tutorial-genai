"""
검색 방식 비교 — 벡터(의미) vs BM25(키워드) vs 하이브리드.
이 예제: 같은 문서·질문에 세 방식을 적용해 '어디서 이기고 어디서 지는지' 를 본다.

  (3.4 는 벡터 검색 '안에서' 의 모드(similarity/MMR), 여기 3.4-3 은 벡터 '밖' 의 방식까지)

  - 벡터(dense)   : 의미가 비슷하면 단어가 달라도 찾음. 동의어·말바꿈에 강함.
                    약점 → 모델명·약어·숫자 같은 '정확한 토큰' 은 임베딩이 뭉개기 쉬움.
  - BM25(sparse)  : 단어가 실제로 겹쳐야 점수. 키워드·전문용어·모델명에 강함.
                    약점 → 단어가 안 겹치면(동의어·말바꿈) 0점. 의미를 모름.
  - 하이브리드     : 둘을 합쳐(RRF) 각자의 약점을 메움. 실무 검색의 기본형.
"""

from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever  # langchain 1.x 위치

load_dotenv()

# [관전 포인트 1] 일부러 '정확한 토큰' 과 '말바꿈' 을 섞어둔 문서들
#   - 모델명/약어(990 PRO, TBW) → BM25 가 잘 잡는 미끼
#   - 'SSD' 라는 단어 없이 의미만 같은 문장 → 벡터가 잘 잡는 미끼
docs = [
    Document(page_content="삼성 990 PRO 는 PCIe 4.0 NVMe SSD 다.",          metadata={"id": "990pro"}),
    Document(page_content="WD Black SN850X 는 고성능 게이밍용 저장장치다.",   metadata={"id": "sn850x"}),
    Document(page_content="TBW 는 SSD 의 총 쓰기 수명을 나타내는 지표다.",     metadata={"id": "tbw"}),
    Document(page_content="이 드라이브는 데이터를 아주 오래 안전하게 보관한다.", metadata={"id": "durable"}),
    Document(page_content="NVMe 는 PCIe 레인을 통해 직접 연결된다.",          metadata={"id": "pcie"}),
    Document(page_content="SATA 방식은 구형 인터페이스라 대역폭이 좁다.",      metadata={"id": "sata"}),
]

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = Chroma.from_documents(docs, embeddings, collection_name="hybrid_demo")

# 벡터 retriever (Chroma)
dense = store.as_retriever(search_kwargs={"k": 3})

# BM25 retriever — 벡터 DB 가 아니라 '문서 리스트' 에서 직접 만든다(임베딩 X)
#   [주의] 기본 토크나이저는 '공백 분리'. 한국어 조사("속도는" vs "속도")까지는 못 가른다.
#   실무 한국어는 preprocess_func 에 형태소 분석기(kiwi/konlpy)를 끼우면 적중률 ↑.
bm25 = BM25Retriever.from_documents(docs)
bm25.k = 3

# 하이브리드 — 두 retriever 를 RRF(순위 기반 융합)로 합침. weights 로 비중 조절.
hybrid = EnsembleRetriever(retrievers=[dense, bm25], weights=[0.5, 0.5])


def show(title, results):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    for d in results:
        print(f"  [{d.metadata['id']:8}] {d.page_content}")


# ── 질문 A: 정확한 모델명 '990 PRO' (키워드형) ──────────────────────
#   BM25 가 토큰 그대로 매칭 → 1등. 벡터는 숫자·모델명을 뭉개 밀릴 수 있다.
qA = "990 PRO 스펙 알려줘"
print("\n" + "#" * 60)
print(f"질문 A (키워드형): {qA!r}")
print("#" * 60)
show("(A-1) 벡터 — 의미 위주, 모델명은 약할 수 있음", dense.invoke(qA))
show("(A-2) BM25 — '990' '990 PRO' 토큰 정확 매칭", bm25.invoke(qA))
show("(A-3) 하이브리드 — 둘을 합쳐 안정적", hybrid.invoke(qA))

# ── 질문 B: 단어가 안 겹치는 말바꿈 (의미형) ─────────────────────────
#   '수명/TBW' 라는 단어를 안 쓰고 물어본다 → BM25 는 겹치는 단어가 없어 헛다리.
#   벡터는 의미로 'TBW=수명' 문서를 끌어온다.
qB = "오래 써도 데이터가 안 망가지는 제품"
print("\n" + "#" * 60)
print(f"질문 B (의미형, 단어 안 겹침): {qB!r}")
print("#" * 60)
show("(B-1) 벡터 — 말이 달라도 의미로 매칭(수명/durable)", dense.invoke(qB))
show("(B-2) BM25 — 겹치는 단어 적어 엉뚱할 수 있음", bm25.invoke(qB))
show("(B-3) 하이브리드 — 의미+키워드 보완", hybrid.invoke(qB))

store.delete_collection()


# 정리 — 언제 무엇을?
#   - 모델명/에러코드/사번/전문용어 등 '정확히 그 단어' 가 중요   → BM25(또는 하이브리드)
#   - 동의어·말바꿈·개념 검색                                    → 벡터
#   - 둘 다 섞인 실제 질의(대부분)                               → 하이브리드 (EnsembleRetriever)
#   손잡이: weights(벡터:BM25 비중), 각 retriever 의 k, BM25 의 preprocess_func(한국어 토크나이저)
#
#   ▷ 체인에 끼우려면? 4.rag_chain 의 retriever 자리에 dense/bm25/hybrid 아무거나 그대로 넣으면 된다.


# ─────────────────────────────────────────────────────────────────────
# 실제 실행 결과 (text-embedding-3-small 기준 — 순서는 조금씩 다를 수 있음)
#
#   질문 A (키워드형): '990 PRO 스펙 알려줘'
#     (A-1) 벡터  → [990pro] [sn850x] [pcie]   (요즘 임베딩은 모델명도 꽤 잘 잡음)
#     (A-2) BM25  → [990pro] [sata]   [pcie]   ('990 PRO' 정확 매칭으로 1등은 확실,
#                                               단 2등에 관련 없는 [sata] 가 끼어듦)
#     (A-3) 하이브리드 → [990pro] 를 1등으로 안정화
#
#   질문 B (의미형, 단어 안 겹침): '오래 써도 데이터가 안 망가지는 제품'
#     (B-1) 벡터  → [durable] [sn850x] [tbw]   ← 단어 안 겹쳐도 '수명' 의미로 [tbw] 잡음 ★
#     (B-2) BM25  → [durable] [sata]   [pcie]  ← [tbw] 를 놓치고 무관한 문서가 채움 ✗
#     (B-3) 하이브리드 → 벡터가 찾은 [tbw] 를 살려 보완
#
#   ▷ 핵심: A 는 둘 다 1등을 맞히지만 BM25 는 2등부터 흔들리고,
#           B 는 벡터만 핵심 문서([tbw])를 맞히고 BM25 는 통째로 놓친다.
#     "한 방식만으로는 모든 질의를 못 이긴다" → 그래서 실무는 하이브리드.
#     (단, 한국어 키워드 적중을 더 끌어올리려면 BM25 에 형태소 토크나이저 필요)
# ─────────────────────────────────────────────────────────────────────
