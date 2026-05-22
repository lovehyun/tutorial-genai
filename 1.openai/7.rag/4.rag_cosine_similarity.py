# RAG with FAISS - 4단계: 거리척도를 코사인 유사도로 바꾸기
# pip install openai faiss-cpu numpy sentence-transformers python-dotenv
#
# 3단계 대비 새로 추가된 것:
#   유사도 계산을 L2 거리 → '코사인 유사도'로 바꾼다.
#   L2는 벡터의 '크기 + 방향'을 모두 보지만, 코사인은 '방향(= 의미)'만 본다.
#
# 두 척도의 값 범위와 의미:
#   L2 거리 : 0 ~ ∞   — 0이면 동일, 멀수록 큰 값 (작을수록 유사, 상한 없음)
#                       ※ FAISS IndexFlatL2는 '거리의 제곱'을 반환한다
#   코사인  : -1 ~ 1  — 1=같은 방향, 0=무관, -1=정반대 (클수록 유사)
#
# 텍스트 검색에서 코사인이 더 나은 이유:
#   ① 문서 길이에 안 휘둘림 — 같은 주제면 길이가 달라도 '유사'로 판단
#   ② 값 범위가 -1~1로 고정 → '유사도 < 0.2 = 무관' 같은 임계값이 일관되게 작동
#      (L2는 상한이 없어 '얼마면 가까운지' 절대 기준을 세우기 어렵다)
#   ③ MiniLM 등 임베딩 모델 자체가 코사인 유사도로 학습됨 → 모델의 의도와 일치
#
# 참고: OpenAI 임베딩은 이미 정규화돼 있어 L2든 코사인이든 검색 순위가 같다.
#       차이는 정규화되지 않은 로컬 모델(3단계~)에서 실제로 드러난다.

import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

documents = [
    "Python은 강력한 프로그래밍 언어입니다.",
    "OpenAI는 AI 연구를 선도하는 기업입니다.",
    "FAISS는 벡터 검색을 위한 라이브러리입니다.",
]

# [관전 포인트 1] 코사인 유사도 = '정규화된 벡터의 내적(Inner Product)'
#   ① 벡터를 길이 1로 정규화하고  ② IndexFlatL2 대신 IndexFlatIP(내적)를 쓴다.
doc_embeddings = np.array(embedding_model.encode(documents), dtype=np.float32)
faiss.normalize_L2(doc_embeddings)                  # ① 정규화
index = faiss.IndexFlatIP(doc_embeddings.shape[1])  # ② 내적 기반 인덱스
index.add(doc_embeddings)

def rag_query(user_query):
    query_embedding = np.array([embedding_model.encode(user_query)], dtype=np.float32)
    faiss.normalize_L2(query_embedding)             # 질문 벡터도 똑같이 정규화

    # [관전 포인트 2] IndexFlatIP의 검색 결과값이 곧 코사인 유사도 (1에 가까울수록 유사)
    #   L2와 달리 '거리 → 점수' 변환이 필요 없다 (결과를 그대로 읽으면 된다).
    similarities, indices = index.search(query_embedding, k=1)
    retrieved_doc = documents[indices[0][0]]
    print(f"검색된 문서: {retrieved_doc} (코사인 유사도: {similarities[0][0]:.4f})")

    prompt = f"참고 정보: {retrieved_doc}\n\n질문: {user_query}\n답변:"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 제공된 정보만을 바탕으로 답변합니다."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content

query = "OpenAI는 어떤 기업인가요?"
print("\n답변:", rag_query(query))
