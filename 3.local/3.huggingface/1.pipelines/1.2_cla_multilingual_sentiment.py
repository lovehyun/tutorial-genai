# pip install transformers torch
from transformers import BertTokenizer, BertForSequenceClassification
import torch

# BERT는 Bidirectional Encoder Representations from Transformers의 약자이며, 
# 2018년에 Google에서 발표한 자연어 처리(NLP) 모델입니다.

# 1. 모델과 토크나이저 불러오기 (감정 분석용 BERT)
# model_name = "bert-base-uncased" # 영어 전용, 파인튜잉 용도 (분류 등)
model_name = "nlptown/bert-base-multilingual-uncased-sentiment" # 다국어 지원, 감정점수 (1~5점 예측)
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)

# 2. 입력 문장
text = "이 영화 정말 재미있었어요!"
# texts = ["이 식당 너무 별로였어요", "여기 서비스 정말 최고예요!"]

# 3. 토크나이징
inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
# inputs = tokenizer(texts, return_tensors="pt", truncation=True, padding=True)

# 4. 예측
with torch.no_grad():
    outputs = model(**inputs)
    logits = outputs.logits
    predicted_class = logits.argmax().item() # 문장 1개만 분석
    # 문장 여러개 (batch 처리)
    # predictions = torch.argmax(logits, dim=1)  # [0~4] → [1~5점]으로 해석

# 5. 결과 출력 (1~5점 중 하나)
print(f"예측된 감정 점수: {predicted_class + 1}점")

# for text, pred in zip(texts, predictions):
#    print(f"문장: \"{text}\" → 감정 점수: {pred.item() + 1}점")



# Transformer
#  ├─ Encoder  ← BERT 사용 (이해(Understanding) 목적)
#  └─ Decoder  ← GPT  사용 (생성(Generation) 목적)

# BERT의 주요 파생 모델
#  - RoBERTa
#    BERT 개선판
#    NSP 제거 (Next Sentence Prediction)
#    데이터 증가
#  - DistilBERT
#    경량화 버전
#    속도 빠름
#  - ALBERT
#    파라미터 감소
#    메모리 절약
#  - KoBERT
#    한국어 특화

# | 구분     | BERT              | GPT            |
# | ------ | ----------------- | -------------- |
# | 핵심 목적  | 이해(Understanding) | 생성(Generation) |
# | 구조     | Encoder           | Decoder        |
# | 입력     | 문장 전체             | 앞부분 토큰         |
# | 출력     | 분류, 벡터            | 다음 토큰          |
# | 대표 작업  | 분류, 검색, NER       | 챗봇, 번역, 요약, 코딩 |
# | 문서 임베딩 | 강함                | 가능하지만 비효율적     |
# | 텍스트 생성 | 약함                | 매우 강함          |
