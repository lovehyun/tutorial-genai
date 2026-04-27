# pip install openai faiss-cpu python-dotenv

import os
import numpy as np
import faiss
from openai import OpenAI
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# OpenAI API 키 설정
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 예제 문서 데이터 (RAG를 위한 검색 대상)
documents = [
    "Python은 강력한 프로그래밍 언어입니다.",
    "OpenAI는 AI 연구를 선도하는 기업입니다.",
    "FAISS는 벡터 검색을 위한 라이브러리입니다.",
]

# 문서 인덱싱 (벡터 생성 및 저장)
def get_embedding(text):
    response = client.embeddings.create(input=text,
    model="text-embedding-ada-002")
    return np.array(response.data[0].embedding)

# 문서 임베딩 생성 및 벡터DB(Faiss) 구축
index = faiss.IndexFlatL2(1536)  # OpenAI 임베딩 차원(1536)
doc_embeddings = np.array([get_embedding(doc) for doc in documents])
index.add(doc_embeddings)

# 검색 및 RAG 기반 응답 생성
def rag_query(user_query):
    query_embedding = get_embedding(user_query)
    _, indices = index.search(np.array([query_embedding]), k=1)  # 가장 가까운 문서 검색
    retrieved_doc = documents[indices[0][0]]  # 검색된 문서
    
    # print(f"\n🔍 FAISS 검색된 문서:\n{retrieved_doc}\n")  # 검색된 문서 출력

    prompt = f"""
    {retrieved_doc}
    
    사용자의 질문: {user_query}
    답변:
    """

    response = client.chat.completions.create(model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "당신은 친절한 AI 도우미입니다."},
        # {"role": "system", "content": "당신은 제공된 정보만을 바탕으로 답변해야 합니다."},
        {"role": "user", "content": prompt}
    ])

    return response.choices[0].message.content

# 테스트 실행
query = "OpenAI는 어떤 기업인가요?"
print(rag_query(query))
