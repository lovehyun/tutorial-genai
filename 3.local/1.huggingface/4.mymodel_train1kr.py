import os
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
from datasets import Dataset

# 1️. 데이터 준비 (간단한 감성 분석 데이터셋)
data = {
    "text": ["이 영화 정말 좋아요!", "완전 최악이에요.", "기분이 너무 좋다.", "정말 슬퍼요."],
    # "text": ["이 영화 정말 좋아요!", "완전 최악이에요.", "기분이 너무 좋다.", "정말 슬퍼요.", "기분이 안 좋아요."],
    "label": [1, 0, 1, 0]  # 긍정 (1), 부정 (0)
    # "label": [1, 0, 1, 0, 0]  # 긍정 (1), 부정 (0)
}

dataset = Dataset.from_dict(data)

# 2️. 사전 학습된 모델과 토크나이저 불러오기
# 1) 일반적인 NLP 작업 (감성 분석, 문서 분류 등)
# 추천 모델:
# - bert-base-uncased (BERT 기반, 일반적인 영어 NLP)
# - distilbert-base-uncased (경량화된 BERT, 속도 빠름)
# - roberta-base (BERT보다 강력한 모델)
# 2) 한국어 NLP 작업
# 추천 모델:
# - klue/bert-base (한국어 BERT)
# - beomi/KcBERT-base (한국어 BERT, 감성 분석 특화)
# - snunlp/KR-FinBERT (한국어 금융 뉴스 분석)
# 3) 텍스트 생성 (Chatbot, 요약, 번역 등)
# 추천 모델:
# - gpt2 (기본적인 텍스트 생성)
# - facebook/bart-large (요약, 번역 등에 강함)
# - bigscience/bloom (GPT 대체 모델, 대규모)
# 4) 코드 생성 (프로그래밍 관련)
# 추천 모델:
# - Salesforce/codegen-350M-multi (다양한 프로그래밍 언어 지원)
# - codellama/CodeLlama-7b (Llama 기반 코드 생성)

# model_name = "distilbert-base-uncased"
model_name = "beomi/KcBERT-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 3️. 데이터셋을 토큰화
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True)

tokenized_datasets = dataset.map(tokenize_function, batched=True)

# 4️. 감성 분석 모델 생성
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

# 5️. 훈련 설정
training_args = TrainingArguments(
    output_dir="./my_model",  # 모델이 저장될 폴더
    evaluation_strategy="no",  # 평가를 하지 않도록 설정
    per_device_train_batch_size=2,
    num_train_epochs=1,
    save_strategy="epoch"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets
)

# 6️. 모델 학습
trainer.train()

# 7️. 모델 저장
save_path = "./my_local_model"
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)

print(f"✅ 모델이 {save_path}에 저장되었습니다!")
