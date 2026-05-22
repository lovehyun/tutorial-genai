# RAG with FAISS - 5단계: 더 정확한 임베딩 모델로 교체
# pip install openai faiss-cpu numpy sentence-transformers python-dotenv
#
# 4단계 대비 새로 추가된 것:
#   임베딩 모델을 MiniLM → 'all-mpnet-base-v2'로 바꾼다.
#   검색 품질은 임베딩 모델 성능에 크게 좌우된다 — 모델만 바꿔 결과를 비교해 본다.

import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# [관전 포인트 1] 임베딩 모델 비교 — 한 줄만 활성화해 검색 결과를 비교해 보세요
#   all-MiniLM-L6-v2  : 384차원,  80MB, 빠름 / 품질 보통
#   all-mpnet-base-v2 : 768차원, 420MB, 느림 / 품질 우수
model_name = "all-mpnet-base-v2"
# model_name = "all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(model_name)

documents = [
    "Python은 강력한 프로그래밍 언어입니다.",
    "OpenAI는 AI 연구를 선도하는 기업입니다.",
    "FAISS는 벡터 검색을 위한 라이브러리입니다.",
]

# [관전 포인트 2] 모델을 바꾸면 임베딩 차원도 달라진다 (384 → 768).
#   shape[1]로 차원을 받으므로 코드는 그대로 동작하지만, 인덱스는 반드시 재구축해야 한다.
#   (저장된 벡터와 질문 벡터의 차원이 다르면 검색이 불가능)
doc_embeddings = np.array(embedding_model.encode(documents), dtype=np.float32)
faiss.normalize_L2(doc_embeddings)
index = faiss.IndexFlatIP(doc_embeddings.shape[1])
index.add(doc_embeddings)

def rag_query(user_query):
    query_embedding = np.array([embedding_model.encode(user_query)], dtype=np.float32)
    faiss.normalize_L2(query_embedding)
    similarities, indices = index.search(query_embedding, k=1)
    retrieved_doc = documents[indices[0][0]]
    print(f"[{model_name}] 검색된 문서: {retrieved_doc} (유사도: {similarities[0][0]:.4f})")

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
print("답변:", rag_query(query))
