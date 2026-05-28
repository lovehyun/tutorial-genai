"""
임베딩이란? — 텍스트를 벡터(숫자 배열)로 변환하는 함수.
이 예제: OpenAIEmbeddings 로 문장을 벡터화하고, 코사인 유사도로 의미적 거리를 비교합니다.

RAG 의 모든 검색은 결국 "내 질문 벡터" 와 "문서 벡터들" 사이의 거리 계산입니다.
의미가 가까운 문장 = 벡터 공간에서 가까운 점.


─── 더 자세한 개념 정리 ────────────────────────────────────────

[Q1] 임베딩 공간은 빈 공간인가?
  아니요. 이미 OpenAI / BAAI 등이 거대한 코퍼스(웹/책 수십억 단어)로
  사전 훈련해놓은 "학습된 공간" 입니다. 학습 단계에서:
    - 비슷한 의미는 가까이
    - 다른 의미는 멀리
  를 무수히 반복해서, 1536 차원 공간 안에 의미가 이미 정렬돼 있습니다.
  (그래서 "왕 - 남자 + 여자 ≈ 여왕" 같은 의미 연산도 가능)
  우리가 .embed_query() 호출할 때는 그 학습된 매핑을 적용해
  "이 문장은 이 좌표" 라고 알려줄 뿐.

[Q2] 한 문장이 한 벡터를 갖나?
  네. 문장 길이가 길든 짧든 항상 같은 차원의 벡터 1개.
    "NVMe 는 SSD 인터페이스다." → [0.013, -0.221, ..., 0.087]  (1536개 숫자)

[Q3] Transformer 가 단어 간 유사도/관계 계산을 하는가?
  네. embed() 한 줄 호출 뒤에서 transformer 가 다 돌아갑니다:

    입력: "고양이가 소파에 앉아있다."
            ↓
    [1] 토큰화           "고양이/가/소파/에/앉아/있다"
            ↓
    [2] 토큰별 임베딩    각 토큰 → 벡터 1개씩
            ↓
    [3] Self-Attention   ★ 토큰 간 관계 계산
                           "고양이" ↔ "앉아" 강하게 연결
                           "소파"   ↔ "앉아" 강하게 연결
                           여러 layer 거치며 문맥 반영
            ↓
    [4] Pooling          토큰 벡터들 → 문장 벡터 1개
                          (평균 / CLS 토큰 등)
            ↓
    출력: [0.013, -0.221, ..., 0.087]   ← 한 문장 = 한 벡터

  단어 간 유사도/관계는 [3] self-attention 안에서 이미 다 일어남.
  우리는 그 결과를 한 벡터로 받을 뿐.

[Q4] 단어 임베딩 (옛날) vs 문장 임베딩 (지금)
  옛날 (Word2Vec, GloVe) : 단어 1개 = 벡터 1개. 문맥 무시 ("bank" = 강둑/은행 같음)
  지금 (text-embedding-3, bge-m3 등) : 문장 1개 = 벡터 1개. Transformer + attention
  현대 RAG 는 후자만 씁니다.

[Q5] 그래서 RAG 가 실제로 하는 일
  학습 단계  : 우리가 하지 않음 (OpenAI 등이 끝냄). 의미가 모두 좌표 공간에 녹아 있음.
  RAG 실행  :
    1. 문서들 → embed → 벡터들 저장
    2. 질문   → embed → 벡터 하나
    3. 코사인 유사도로 가장 가까운 N개 찾기   ← 사실상 단순 산수
    4. 그 문서들을 LLM 프롬프트에 끼움

  우리가 직접 짜는 건 4단계 뿐. 의미 이해는 학습된 모델에 위임.
"""

import numpy as np
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 1) 단일 문장 → 벡터
text = "고양이가 소파 위에서 잔다."
vec = embeddings.embed_query(text)
print(f"'{text}' → 벡터 차원: {len(vec)}")
print(f"  앞 5개 값: {vec[:5]}")
print(f"  (총 1536 차원 중 5개만)\n")


# 2) 여러 문장을 벡터화하고 의미 거리 비교
sentences = [
    "고양이가 소파 위에서 잔다.",
    "강아지가 침대에서 자고 있어요.",       # 위와 의미 가까움
    "파이썬은 인기 있는 프로그래밍 언어다.", # 완전히 다른 주제
]
vectors = embeddings.embed_documents(sentences)


def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


print("=== 문장 간 의미적 유사도 (1.0 = 동일) ===")
for i, s1 in enumerate(sentences):
    for j, s2 in enumerate(sentences):
        if i < j:
            sim = cosine_similarity(vectors[i], vectors[j])
            print(f"  {sim:.3f}   '{s1[:20]}' ↔ '{s2[:20]}'")

# 출력에서 동물 문장 둘은 유사도가 높고, 프로그래밍 문장과는 낮은 걸 확인.
# 검색 = "내 질문 벡터" 와 가장 가까운 "문서 벡터" 찾기. (1.2 부터 본격 시작)
