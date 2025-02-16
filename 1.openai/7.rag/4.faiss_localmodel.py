import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 1. 로컬 임베딩 모델 로드 (Hugging Face 모델)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # 경량 모델

# 2. 문서 데이터
documents = [
    "Python은 강력한 프로그래밍 언어입니다.",
    "OpenAI는 AI 연구를 선도하는 기업입니다.",
    "FAISS는 벡터 검색을 위한 라이브러리입니다.",
]

# 3. 문서 임베딩 생성
doc_embeddings = np.array(embedding_model.encode(documents))

# 4. FAISS 인덱스 생성
embedding_dim = doc_embeddings.shape[1]
index = faiss.IndexFlatL2(embedding_dim)
index.add(doc_embeddings)

# 5. 검색 함수 정의
def rag_query(user_query):
    query_embedding = np.array([embedding_model.encode(user_query)])  # 사용자 입력 임베딩 변환
    
    distances, indices = index.search(query_embedding, k=1)  # 가장 가까운 문서 검색
    retrieved_doc = documents[indices[0][0]]
    similarity_score = 1 / (1 + distances[0][0])  # 유사도 계산 (0~1)

    print("\n🔍 FAISS 검색 결과:")
    print(f"   📄 검색된 문서: {retrieved_doc}")
    print(f"   🎯 검색 정확도(유사도 점수): {similarity_score:.4f}")

# 6. 테스트 실행
query = "OpenAI는 어떤 회사인가요?"
rag_query(query)
