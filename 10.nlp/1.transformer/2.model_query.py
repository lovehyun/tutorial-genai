from sentence_transformers import SentenceTransformer, util

# 1. 모델 로드
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. 데이터 준비
corpus = [
    "I love programming in Python.",
    "Machine learning is fascinating.",
    "Natural Language Processing helps computers understand human language.",
    "Sentence Transformers provide a way to compute sentence embeddings.",
    "I enjoy exploring AI and its applications.",
]

# 3. 코퍼스 임베딩 생성
corpus_embeddings = model.encode(corpus, convert_to_tensor=True)

# 4. 검색 쿼리
query = "Tell me about NLP and AI."
query_embedding = model.encode(query, convert_to_tensor=True)

# 5. 유사도 계산
cosine_scores = util.cos_sim(query_embedding, corpus_embeddings)

# 6. 결과 정렬 및 출력
top_k = 3  # 상위 3개 결과 출력
top_results = cosine_scores.topk(k=top_k, dim=1)  # dim=1은 열 기준으로 top-k 계산

print(f"Query: {query}\n")
print("Top results:")

# top_results.indices와 top_results.values를 처리
for score, idx in zip(top_results.values[0], top_results.indices[0]):
    print(f" - {corpus[idx]} (Score: {score:.4f})")
