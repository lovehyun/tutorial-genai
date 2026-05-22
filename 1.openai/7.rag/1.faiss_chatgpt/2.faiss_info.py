# pip install openai faiss-cpu tiktoken python-dotenv

import os
import numpy as np
import faiss
import tiktoken  # OpenAI의 토큰화 라이브러리
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

def count_tokens(text, model="gpt-4-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# 문서 인덱싱 (벡터 생성 및 저장)
def get_embedding(text):
    response = client.embeddings.create(input=text,
    model="text-embedding-ada-002")
    return np.array(response.data[0].embedding)

# 문서 임베딩 생성 및 벡터DB(Faiss) 구축
index = faiss.IndexFlatL2(1536)  # OpenAI 임베딩 차원(1536),  # L2거리 =  ∣∣A−B∣∣ ^ 2   유클리디언 거리
doc_embeddings = np.array([get_embedding(doc) for doc in documents])
index.add(doc_embeddings)

# 검색 및 RAG 기반 응답 생성
def rag_query(user_query):
    query_embedding = get_embedding(user_query)
    distances, indices = index.search(np.array([query_embedding]), k=1) # FAISS 검색 (k=1: 가장 가까운 문서 1개 찾기)
    
    # 검색된 문서와 정확도(거리)
    retrieved_doc = documents[indices[0][0]]
    true_distance = np.sqrt(distances[0][0])  # FAISS는 제곱된 거리값을 반환하므로, 제곱근을 취해야 함
    similarity_score = 1 / (1 + true_distance)  # 거리값을 정규화하여 유사도 점수로 변환 (가까울수록 유사도가 높음)

    print("\n🔍 FAISS 검색 결과:")
    print(f"   📄 검색된 문서: {retrieved_doc}")
    print(f"   🎯 검색 정확도(유사도 점수): {similarity_score:.4f}")

    # 너무 낮은 점수라면 경고 출력
    if similarity_score < 0.2:
        print("\n⚠️ 경고: 검색된 문서가 사용자의 질문과 크게 다를 수 있습니다!")

    # GPT에 전달할 프롬프트 생성
    prompt = f"""
    다음 정보를 바탕으로만 질문에 답하세요.
    다른 지식이나 추론을 사용하지 말고, 주어진 정보 내에서만 답을 생성하세요.

    참고 정보:
    {retrieved_doc}

    사용자의 질문: {user_query}
    답변:
    """

    print("\n📝 GPT에게 전달된 프롬프트:")
    print(prompt)

    # 토큰 수 계산
    token_count = count_tokens(prompt)
    print(f"\n📏 프롬프트 토큰 수: {token_count} 토큰")
    
    response = client.chat.completions.create(model="gpt-4o-mini",
    messages=[
        # {"role": "system", "content": "당신은 친절한 AI 도우미입니다."},
        {"role": "system", "content": "당신은 제공된 정보만을 바탕으로 답변해야 합니다."},
        # {"role": "system", "content": "당신은 제공된 정보만을 바탕으로 반대로 답변해야 합니다."},
        {"role": "user", "content": prompt}
    ])

    return response.choices[0].message.content

# 테스트 실행
query = "OpenAI는 어떤 기업인가요?"
print(rag_query(query))
