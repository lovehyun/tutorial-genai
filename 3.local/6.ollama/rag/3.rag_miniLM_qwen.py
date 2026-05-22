# pip install sentence-transformers faiss-cpu requests python-dotenv

import numpy as np
import faiss
import requests
from sentence_transformers import SentenceTransformer

# -----------------------------
# 로컬 임베딩 모델
# -----------------------------
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# 문서 데이터
# -----------------------------
documents = [
    "Python은 강력한 프로그래밍 언어입니다.",
    "OpenAI는 AI 연구를 선도하는 기업입니다.",
    "FAISS는 벡터 검색을 위한 라이브러리입니다.",
]

# -----------------------------
# 문서 임베딩 생성
# -----------------------------
doc_embeddings = np.array(
    embedding_model.encode(documents),
    dtype=np.float32
)

# -----------------------------
# 코사인 유사도용 정규화
# -----------------------------
faiss.normalize_L2(doc_embeddings)

# -----------------------------
# FAISS 인덱스 생성
# Inner Product = cosine similarity
# -----------------------------
embedding_dim = doc_embeddings.shape[1]

index = faiss.IndexFlatIP(embedding_dim)  # Inner Product(내적)

# cos(θ)=       A⋅B​   
#       ∣∣A∣∣∣∣B∣∣

# 값	의미
# 1     거의 동일
# 0     관련 없음
# -1    반대 의미

index.add(doc_embeddings)

# -----------------------------
# RAG 질의 함수
# -----------------------------
def rag_query(user_query):

    # 질문 임베딩 생성
    query_embedding = np.array(
        [embedding_model.encode(user_query)],
        dtype=np.float32
    )

    # 코사인 유사도용 정규화
    faiss.normalize_L2(query_embedding)

    # 검색
    similarities, indices = index.search(query_embedding, k=1)

    retrieved_doc = documents[indices[0][0]]

    similarity_score = similarities[0][0]

    print("\n🔍 FAISS 검색 결과:")
    print(f"📄 검색 문서: {retrieved_doc}")
    print(f"🎯 코사인 유사도: {similarity_score:.4f}")

    # 프롬프트 생성
    prompt = f"""
다음 정보만 사용해서 답변하세요.

[참고 정보]
{retrieved_doc}

[질문]
{user_query}

[답변]
"""

    print("\n📝 Qwen에게 전달되는 프롬프트:")
    print(prompt)

    # -----------------------------
    # Ollama 로컬 API 호출
    # -----------------------------
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:1.5b",
            "prompt": prompt,
            "stream": False
        }
    )

    result = response.json()["response"]

    return result

# -----------------------------
# 테스트
# -----------------------------
query = "OpenAI는 어떤 기업인가요?"

answer = rag_query(query)

print("\n💬 최종 응답:")
print(answer)
