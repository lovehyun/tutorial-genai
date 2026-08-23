# RAG with FAISS - 3단계: 임베딩을 로컬 모델로 교체
# pip install openai faiss-cpu numpy sentence-transformers python-dotenv
#
# 2단계 대비 새로 추가된 것:
#   임베딩을 OpenAI API 대신 '로컬 모델'로 만든다.
#   → 임베딩 비용 0원, 인터넷·API 키 불필요. (응답 생성용 GPT는 그대로 API 사용)

import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# [관전 포인트 1] 로컬 임베딩 모델 (최초 실행 시 자동 다운로드, 약 80MB)
#   all-MiniLM-L6-v2 = 가볍고 빠른 영어 위주 모델.
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

documents = [
    "Python은 강력한 프로그래밍 언어입니다.",
    "OpenAI는 AI 연구를 선도하는 기업입니다.",
    "FAISS는 벡터 검색을 위한 라이브러리입니다.",
]

# [관전 포인트 2] 임베딩 차원은 모델마다 다르다 (OpenAI 1536 vs MiniLM 384)
#   → 차원을 하드코딩하지 말고 임베딩 결과의 shape에서 가져온다.
doc_embeddings = np.array(embedding_model.encode(documents))
index = faiss.IndexFlatL2(doc_embeddings.shape[1])
index.add(doc_embeddings)

def rag_query(user_query):
    # [관전 포인트 3] 질문도 '저장 때와 같은 로컬 모델'로 임베딩해야 한다 (필수 규칙)
    query_embedding = np.array([embedding_model.encode(user_query)])
    distances, indices = index.search(query_embedding, k=1)
    retrieved_doc = documents[indices[0][0]]
    print(f"검색된 문서: {retrieved_doc} (거리: {distances[0][0]:.4f})")

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
