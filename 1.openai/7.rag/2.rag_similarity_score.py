# RAG with FAISS - 2단계: 검색 품질 들여다보기
# pip install openai faiss-cpu numpy tiktoken python-dotenv
#
# 1단계 대비 새로 추가된 것:
#   검색이 '얼마나 잘 맞았는지'를 눈으로 확인한다.
#   ① 거리 → 유사도 점수 변환  ② 저품질 경고  ③ 프롬프트 토큰 수 측정

import os
import numpy as np
import faiss
import tiktoken
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

documents = [
    "Python은 강력한 프로그래밍 언어입니다.",
    "OpenAI는 AI 연구를 선도하는 기업입니다.",
    "FAISS는 벡터 검색을 위한 라이브러리입니다.",
]

def get_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-ada-002")
    return np.array(response.data[0].embedding)

index = faiss.IndexFlatL2(1536)
index.add(np.array([get_embedding(doc) for doc in documents]))

def rag_query(user_query):
    query_embedding = get_embedding(user_query)
    distances, indices = index.search(np.array([query_embedding]), k=1)
    retrieved_doc = documents[indices[0][0]]

    # [관전 포인트 1] FAISS의 distance는 '제곱된 L2 거리' → 점수로 변환
    #   L2 거리 자체는 0~무한대(상한 없음)라 읽기 불편 → 1/(1+거리)로 0~1 점수화한다.
    #   거리가 작을수록(0에 가까울수록) 점수는 1에 가깝다.
    true_distance = np.sqrt(distances[0][0])
    similarity_score = 1 / (1 + true_distance)
    print(f"검색된 문서: {retrieved_doc}")
    print(f"유사도 점수: {similarity_score:.4f}")

    # [관전 포인트 2] 점수가 너무 낮으면 = 질문과 관련된 문서가 없다는 신호
    #   (RAG에서 '엉뚱한 문서'를 GPT에 넘기면 잘못된 답이 나온다 → 사전 점검)
    if similarity_score < 0.2:
        print("경고: 질문과 관련된 문서를 찾지 못했을 수 있습니다.")

    prompt = f"참고 정보: {retrieved_doc}\n\n질문: {user_query}\n답변:"

    # [관전 포인트 3] 프롬프트 토큰 수 = API 비용·컨텍스트 길이 제한과 직결
    #   o200k_base = gpt-4o 계열이 사용하는 토크나이저
    token_count = len(tiktoken.get_encoding("o200k_base").encode(prompt))
    print(f"프롬프트 토큰 수: {token_count}")

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


###############
# 참고
###############
def rag_query(user_query):
    query_embedding = get_embedding(user_query)

    # 가장 가까운 문서 3개 검색
    distances, indices = index.search(np.array([query_embedding]), k=3)

    print(f"질문: {user_query}\n") # 질문과 가까운 후보군 3개 출력
    for rank, (idx, dist) in enumerate(zip(indices[0], distances[0]), start=1):
        true_distance = np.sqrt(dist)          # 실제 L2 거리
        similarity = 1 / (1 + true_distance)   # 0~1로 변환

        print(f"[{rank}위]")
        print(f"문서 : {documents[idx]}")
        print(f"L2^2 : {dist:.4f}")
        print(f"L2   : {true_distance:.4f}")
        print(f"유사도: {similarity:.4f}")
        print("-" * 40)
