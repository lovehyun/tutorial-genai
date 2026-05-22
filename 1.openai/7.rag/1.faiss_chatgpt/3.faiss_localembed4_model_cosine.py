import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

# .env 파일 로드 (OpenAI API 키)
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 경고 제거 (OpenMP 충돌 해결)
# os.environ["USE_SIMPLE_THREADED_LEVEL3"] = "1"
# os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# 더 좋은 임베딩 모델 사용
embedding_model = SentenceTransformer("all-mpnet-base-v2")

# 문서 데이터 (FAISS에 저장할 데이터)
documents = [
    "Python은 강력한 프로그래밍 언어입니다.",
    "OpenAI는 AI 연구를 선도하는 기업입니다.",
    "FAISS는 벡터 검색을 위한 라이브러리입니다.",
]

# 벡터 정규화 함수 (코사인 유사도 적용)
def normalize_vector(vec):
    return vec / np.linalg.norm(vec, axis=1, keepdims=True)  # 벡터 정규화

# 문서 임베딩 생성 (정규화 추가)
doc_embeddings = embedding_model.encode(documents)
doc_embeddings = normalize_vector(doc_embeddings)  # 코사인 유사도 적용

# FAISS 인덱스 생성 (내적 기반, 코사인 유사도 적용)
embedding_dim = doc_embeddings.shape[1]
index = faiss.IndexFlatIP(embedding_dim)  # **L2 대신 IndexFlatIP 사용**
index.add(doc_embeddings)

# 검색 + OpenAI API 활용한 응답 생성 함수
def rag_query(user_query):
    # 로컬에서 임베딩 변환 (정규화 적용)
    query_embedding = embedding_model.encode([user_query])
    query_embedding = normalize_vector(query_embedding)  # 정규화 필수
    
    # FAISS 검색 (가장 가까운 문서 찾기)
    distances, indices = index.search(query_embedding, k=1)
    retrieved_doc = documents[indices[0][0]]
    
    # Inner Product 기반 FAISS 점수를 보정하여 코사인 유사도로 변환
    similarity_score = (distances[0][0] + 1) / 2  # 보정 후 0~1 범위로 정규화

    print("\n🔍 FAISS 검색 결과:")
    print(f"   📄 검색된 문서: {retrieved_doc}")
    print(f"   🎯 검색 정확도(유사도 점수): {similarity_score:.4f}")  # 0~1 사이 값으로 보정

    # OpenAI API를 활용한 최종 응답 생성
    prompt = f"""
    다음 정보를 바탕으로만 질문에 답하세요.
    추가적인 지식을 사용하지 말고, 제공된 정보 내에서만 답변하세요.

    참고 정보:
    {retrieved_doc}

    사용자의 질문: {user_query}
    답변:
    """

    print("\n📝 OpenAI API에게 전달된 프롬프트:")
    print(prompt)

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "당신은 제공된 정보만을 바탕으로 답변해야 합니다."},
            {"role": "user", "content": prompt},
        ]
    )

    return response.choices[0].message.content

# 테스트 실행
query = "OpenAI는 어떤 기업인가요?"
print("\n💬 GPT 응답:\n", rag_query(query))
