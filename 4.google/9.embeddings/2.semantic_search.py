# pip install google-genai python-dotenv numpy
#
# 시맨틱 서치 — 1.embeddings.py는 벡터 두 개를 비교하는 데서 끝났다. 임베딩을 실제로 "쓰는"
# 지점은 여기부터다: 질문 하나를 벡터로 바꾸고, 문서 여러 개 중 의미가 가장 가까운 걸 찾는다.
# 키워드가 하나도 안 겹쳐도(예: "먹을거리" vs "요리") 의미가 비슷하면 찾아낸다 — 이게 RAG에서
# 검색 단계가 하는 일이다.
#
# FAISS 같은 벡터 인덱스는 안 쓴다 — 문서 몇 개짜리 numpy 코사인 유사도로 원리만 보여준다.
# 문서가 수만 개 이상이면 이 for문 방식은 느려지고, 그때부터 벡터DB(FAISS/Pinecone/Chroma 등)가
# 필요해진다 — 전체 RAG 파이프라인은 1.openai/8.rag/ 참고.

import os
import numpy as np
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# [관전 포인트 1] 서로 다른 주제의 문서 몇 개를 미리 임베딩해둔다("인덱싱").
documents = [
    "파이썬은 배우기 쉬운 프로그래밍 언어입니다.",
    "오늘 서울 날씨는 맑고 무덥습니다.",
    "김치찌개는 돼지고기와 김치를 넣고 끓이는 한국 음식입니다.",
    "자바스크립트는 웹 브라우저에서 실행되는 언어입니다.",
    "내일은 전국적으로 비가 내리고 기온이 떨어지겠습니다.",
    "된장찌개는 된장을 풀어 두부와 채소를 넣고 끓입니다.",
]

doc_response = client.models.embed_content(model="gemini-embedding-001", contents=documents)
doc_vectors = np.array([e.values for e in doc_response.embeddings])


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def search(query, top_k=3):
    # [관전 포인트 2] 질문도 같은 모델로 임베딩해야 같은 벡터 공간에서 비교할 수 있다.
    query_vector = client.models.embed_content(
        model="gemini-embedding-001", contents=[query]
    ).embeddings[0].values

    scores = [cosine_similarity(query_vector, doc_vec) for doc_vec in doc_vectors]
    ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)

    print(f"\n질문: {query}")
    for doc, score in ranked[:top_k]:
        print(f"  {score:.4f}  {doc}")


# [관전 포인트 3] "국물", "요리" 같은 단어는 documents 어디에도 없는데, 찌개 문서가 상위로
# 나와야 정상이다 — 키워드 매칭이 아니라 의미로 찾는다는 게 이 예제의 핵심이다.
search("맛있는 국물 요리 알려줘", top_k=2)
search("코딩 배우고 싶어", top_k=2)
search("우산 챙겨야 할까?", top_k=2)
