# pip install google-genai python-dotenv numpy
#
# 임베딩(Embeddings) — 텍스트를 의미를 담은 숫자 벡터로 바꾼다. RAG의 첫 단계다.
# OpenAI(`text-embedding-*`)에는 있고 Anthropic에는 없는 기능인데, Gemini도 자체 임베딩
# 모델을 제공한다(`gemini-embedding-001`). `1.openai/8.rag/1.rag_basic.py`와 같은 개념 —
# 그 예제를 Gemini 임베딩으로 바꾸면 이 파일이 된다.

import os
import numpy as np
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# [관전 포인트 1] embed_content — 문장 하나를 벡터로 변환.
sentences = [
    "Python은 강력한 프로그래밍 언어입니다.",
    "오늘 서울 날씨는 맑고 무덥습니다.",
    "파이썬은 배우기 쉬운 프로그래밍 언어입니다.",
]

response = client.models.embed_content(model="gemini-embedding-001", contents=sentences)
vectors = [np.array(e.values) for e in response.embeddings]

print(f"문장 {len(vectors)}개, 벡터 차원: {len(vectors[0])}")

# [관전 포인트 2] 코사인 유사도로 "의미가 비슷한 문장"을 확인한다.
#   1번(Python)과 3번(파이썬)이 같은 내용을 다른 단어로 썼는데도 벡터가 가까워야 정상이다.
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print(f"\n[1] vs [3] (같은 의미, 다른 표현): {cosine_similarity(vectors[0], vectors[2]):.4f}")
print(f"[1] vs [2] (다른 주제):           {cosine_similarity(vectors[0], vectors[1]):.4f}")
