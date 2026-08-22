# (1단계·확장) 한국어 파인튜닝 — 같은 흐름, 모델/데이터만 한국어로
# pip install transformers torch datasets
#
# 1.1 과 구조 동일. 바뀐 것: ① 모델 distilbert → KcBERT  ② 데이터 영어 → 한국어
#   → "사전학습 모델만 갈아끼우면 다른 언어 분류기도 똑같이 만든다" 를 보여준다.
#   저장 경로는 영어 모델과 안 겹치게 ./my_local_model_kr.

import numpy as np
from transformers import (
    AutoModelForSequenceClassification, AutoTokenizer,
    Trainer, TrainingArguments,
)
from datasets import Dataset

# 1) 한국어 데이터 (긍정=1, 부정=0)
train_data = {
    "text": ["이 영화 정말 좋아요!", "완전 최악이에요.", "기분이 너무 좋다.", "정말 슬퍼요.",
             "서비스가 훌륭합니다.", "다시는 안 살래요.", "강력 추천합니다!", "너무 실망했어요."],
    "label": [1, 0, 1, 0, 1, 0, 1, 0],
}
eval_data = {
    "text": ["오늘 기분이 최고예요!", "응대가 형편없었어요.",
             "이거 완전 마음에 들어요!", "기대 이하였습니다."],
    "label": [1, 0, 1, 0],
}

# 한국어 사전학습 모델 (감성분석에 자주 쓰임). 대안: klue/bert-base
model_name = "beomi/KcBERT-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)

def tokenize(batch):
    return tokenizer(batch["text"], padding="max_length", truncation=True, max_length=64)

train_ds = Dataset.from_dict(train_data).map(tokenize, batched=True)
eval_ds  = Dataset.from_dict(eval_data).map(tokenize, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(
    model_name, num_labels=2,
    id2label={0: "부정", 1: "긍정"},
    label2id={"부정": 0, "긍정": 1},
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {"accuracy": float((preds == labels).mean())}

args = TrainingArguments(
    output_dir="./results_kr",
    eval_strategy="epoch",
    save_strategy="epoch",
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    num_train_epochs=3,
    logging_steps=1,
)
trainer = Trainer(
    model=model, args=args,
    train_dataset=train_ds, eval_dataset=eval_ds,
    compute_metrics=compute_metrics,
)

trainer.train()
print("\n평가 결과:", trainer.evaluate())

save_path = "./my_local_model_kr"
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)
print(f"\n✅ 한국어 모델 저장 완료 → {save_path}")
print("   (1.2_predict.py 의 MODEL_DIR 을 이 경로로 바꾸면 한국어 예측 가능)")
