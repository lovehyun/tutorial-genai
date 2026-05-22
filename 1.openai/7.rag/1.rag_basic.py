# RAG with FAISS - 1단계: 기본 RAG 파이프라인
# pip install openai faiss-cpu numpy python-dotenv
#
# RAG(Retrieval-Augmented Generation, 검색 증강 생성):
#   LLM에게 질문만 던지는 게 아니라, '관련 문서를 먼저 찾아서' 함께 줘서 답하게 하는 방식.
#   → 모델이 모르는 최신/사내 정보도 문서만 있으면 답할 수 있다.
#
# 파이프라인:
#   문서 → 임베딩(벡터화) → FAISS 저장 → 질문 임베딩 → 유사 문서 검색 → GPT 응답

import os
import numpy as np
import faiss
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 검색 대상 문서 (지식 베이스)
documents = [
    "Python은 강력한 프로그래밍 언어입니다.",
    "OpenAI는 AI 연구를 선도하는 기업입니다.",
    "FAISS는 벡터 검색을 위한 라이브러리입니다.",
]

# [관전 포인트 1] 텍스트 → 벡터(임베딩) 변환
#   임베딩은 텍스트의 '의미'를 숫자 배열로 바꾼 것. 의미가 비슷하면 벡터도 가깝다.
def get_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-ada-002")
    return np.array(response.data[0].embedding)

# [관전 포인트 2] FAISS 인덱스에 문서 벡터를 저장
#   IndexFlatL2 = L2(유클리드) 거리로 가까운 벡터를 찾는 인덱스. 1536 = 임베딩 차원.
index = faiss.IndexFlatL2(1536)
doc_embeddings = np.array([get_embedding(doc) for doc in documents])
index.add(doc_embeddings)

def rag_query(user_query):
    # [관전 포인트 3] 질문도 '같은 임베딩 모델'로 벡터화해야 같은 공간에서 비교된다
    query_embedding = get_embedding(user_query)

    # [관전 포인트 4] 가장 가까운 문서 k개 검색 (여기서는 k=1)
    distances, indices = index.search(np.array([query_embedding]), k=1)
    retrieved_doc = documents[indices[0][0]]

    # [관전 포인트 5] 검색된 문서를 프롬프트에 끼워넣어 GPT에게 전달 = RAG의 핵심
    prompt = f"참고 정보: {retrieved_doc}\n\n질문: {user_query}\n답변:"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 친절한 AI 도우미입니다."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content

query = "Python은 어떤 언어인가요?"
# query = "OpenAI는 어떤 기업인가요?"
print(rag_query(query))
