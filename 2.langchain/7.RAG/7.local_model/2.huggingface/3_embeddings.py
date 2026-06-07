"""
HuggingFaceEmbeddings — sentence-transformers 임베딩 모델 로컬 사용.
이 예제: 영어 / 다국어 / 한국어 특화 임베딩 모델을 비교합니다.

자주 쓰는 인기 임베딩 모델 (HuggingFace):
  영어 위주:
    - sentence-transformers/all-MiniLM-L6-v2        ~22MB, 빠르고 가벼움 (가장 인기)
    - sentence-transformers/all-mpnet-base-v2       ~420MB, 더 정확
  다국어 (한국어 포함):
    - BAAI/bge-m3                                   ~2.3GB, 최신 SOTA
    - intfloat/multilingual-e5-large                ~2.2GB, 다국어 강함
    - intfloat/multilingual-e5-small                ~470MB, 가벼운 다국어
  한국어 특화:
    - jhgan/ko-sroberta-multitask                   ~470MB, 가장 인기 한국어
    - snunlp/KR-SBERT-V40K-klueNLI-augSTS

준비:
  pip install langchain-huggingface sentence-transformers
  ※ 첫 사용 시 모델 다운로드.
  ※ 임베딩(sentence-transformers)은 GPU 가 있으면 자동으로 GPU 를 쓴다 (별도 설정 불필요).
    강제 지정하려면: HuggingFaceEmbeddings(model_name=..., model_kwargs={"device": "cuda"})
"""

import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings


def cosine(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# 1) 영어 — 가장 가볍고 인기
print("=" * 60)
print("(1) all-MiniLM-L6-v2 — 영어 / 작고 빠름")
print("=" * 60)
en_emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

en_pair = [
    "The cat sleeps on the sofa.",
    "A dog is sleeping on the bed.",
]
en_unrelated = "Python is a popular programming language."

vecs = en_emb.embed_documents(en_pair + [en_unrelated])
print(f"  벡터 차원: {len(vecs[0])}")
print(f"  유사 문장 간:    {cosine(vecs[0], vecs[1]):.3f}")
print(f"  무관 문장과:     {cosine(vecs[0], vecs[2]):.3f}")


# 2) 한국어 특화
print("\n" + "=" * 60)
print("(2) jhgan/ko-sroberta-multitask — 한국어 특화")
print("=" * 60)
ko_emb = HuggingFaceEmbeddings(model_name="jhgan/ko-sroberta-multitask")

ko_pair = [
    "고양이가 소파 위에서 잔다.",
    "강아지가 침대에서 자고 있어요.",
]
ko_unrelated = "파이썬은 인기 있는 프로그래밍 언어다."

vecs = ko_emb.embed_documents(ko_pair + [ko_unrelated])
print(f"  벡터 차원: {len(vecs[0])}")
print(f"  유사 문장 간:    {cosine(vecs[0], vecs[1]):.3f}")
print(f"  무관 문장과:     {cosine(vecs[0], vecs[2]):.3f}")

# 3) 모델 선택 가이드
print("\n" + "=" * 60)
print("어떤 임베딩을 쓸까?")
print("=" * 60)
print("  영어 데이터만:        all-MiniLM-L6-v2 (제일 가벼움)")
print("  한국어 데이터:        ko-sroberta-multitask 또는 bge-m3")
print("  여러 언어 섞임:       bge-m3 / multilingual-e5")
print("  GPU 없고 큰 모델 부담: e5-small 또는 all-MiniLM")
