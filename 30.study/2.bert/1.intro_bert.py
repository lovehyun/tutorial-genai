# pip install transformers torch
from transformers import BertTokenizer, BertForSequenceClassification
import torch

# 1. 모델과 토크나이저 불러오기 (감정 분석용 BERT)
# model_name = "bert-base-uncased" # 영어 전용, 파인튜잉 용도 (분류 등)
model_name = "nlptown/bert-base-multilingual-uncased-sentiment" # 다국어 지원, 감정점수 (1~5점 예측)
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)

# 2. 입력 문장
# text = "이 영화 정말 재미있었어요!"
texts = ["이 식당 너무 별로였어요", "여기 서비스 정말 최고예요!"]

# 3. 토크나이징
# inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
inputs = tokenizer(texts, return_tensors="pt", truncation=True, padding=True)

# 4. 예측
with torch.no_grad():
    outputs = model(**inputs)
    logits = outputs.logits
    # predicted_class = logits.argmax().item() # 문장 1개만 분석
    # 문장 여러개 (batch 처리)
    predictions = torch.argmax(logits, dim=1)  # [0~4] → [1~5점]으로 해석

# 5. 결과 출력 (1~5점 중 하나)
# print(f"예측된 감정 점수: {predicted_class + 1}점")

for text, pred in zip(texts, predictions):
    print(f"문장: \"{text}\" → 감정 점수: {pred.item() + 1}점")
