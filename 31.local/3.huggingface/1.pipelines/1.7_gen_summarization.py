# (파이프라인) 요약(summarization) — 긴 글을 짧게 압축
# pip install transformers torch
#
# 실무 단골 태스크. 뉴스/문서/회의록 요약 등에 쓰인다.
#   요약은 seq2seq(encoder-decoder) 모델 — BART/T5 계열.
#   distilbart-cnn = BART 를 경량화한 뉴스 요약 모델 (CPU 에서도 쓸 만함).

from transformers import pipeline

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

article = """
Hugging Face is a company that has become a central hub for the machine learning
community. It is best known for its Transformers library, which gives developers
easy access to thousands of pre-trained models for tasks such as text classification,
translation, summarization, and question answering. Beyond the library, the Hugging
Face Hub hosts hundreds of thousands of models and datasets shared by researchers and
companies around the world, making state-of-the-art AI accessible to everyone.
"""

# [관전 포인트] max_length/min_length 로 요약 길이를 조절 (토큰 기준)
result = summarizer(article, max_length=60, min_length=20, do_sample=False)

print("원문 길이(문자):", len(article.strip()))
print("\n요약:")
print(result[0]["summary_text"])
