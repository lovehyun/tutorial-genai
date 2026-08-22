# (1단계) 내 모델 사용 — 1.1 에서 저장한 모델로 예측
# pip install transformers torch
#
# 1.1_train.py 가 ./my_local_model 에 저장한 '내 모델' 을 불러와 감성분석.
#   (먼저 1.1 을 실행해 모델을 만들어 둬야 한다)

import os
from transformers import pipeline

MODEL_DIR = "./my_local_model"

if not os.path.isdir(MODEL_DIR):
    raise SystemExit(f"'{MODEL_DIR}' 가 없습니다. 먼저 1.1_train.py 를 실행해 모델을 만드세요.")

# 저장된 로컬 모델 로드 (id2label 덕분에 결과가 NEGATIVE/POSITIVE 로 나온다)
classifier = pipeline("sentiment-analysis", model=MODEL_DIR, tokenizer=MODEL_DIR)

test_sentences = [
    "I love using my own AI model!",
    "This is the worst experience ever.",
    "I am extremely happy today!",
    "I feel so bad...",
]

for text in test_sentences:
    r = classifier(text)[0]
    print(f"📢 {text}\n   → {r['label']} ({r['score']:.3f})\n")

# 정리:
#   - 학습(1.1) → 저장 → 로드(1.2) 가 '나만의 모델' 의 완결된 한 흐름
#   - 한국어 모델(1.3)을 썼다면 model=MODEL_DIR 을 그 저장 경로로 바꾸면 동일하게 동작
