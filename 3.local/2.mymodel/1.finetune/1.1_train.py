# (1단계) 파인튜닝 — 사전학습 모델로 '나만의 감성분류기' 학습
# pip install transformers torch datasets
#
# 나만의 모델 만들기 = 사전학습 모델(distilbert) 위에 내 데이터로 분류 헤드를 학습.
# 흐름: 데이터 → 토큰화 → 학습 → 평가(정확도) → 저장.  (저장한 모델은 1.2 에서 사용)
#   ※ 데이터가 8개뿐인 '구조 학습용' 예제다. 실제로는 수백~수천 건이 필요.

import numpy as np
from transformers import (
    AutoModelForSequenceClassification, AutoTokenizer,
    Trainer, TrainingArguments,
)
from datasets import Dataset

# 1) 데이터 (긍정=1, 부정=0) — 학습/평가 분리
train_data = {
    "text": ["I love this!", "This is terrible!", "I am happy.", "I am sad.",
             "This product is amazing!", "Worst experience ever.",
             "Absolutely fantastic!", "I hate it."],
    "label": [1, 0, 1, 0, 1, 0, 1, 0],
}
eval_data = {
    "text": ["I feel great today!", "The service was awful.",
             "I'm super excited about this!", "Not what I expected."],
    "label": [1, 0, 1, 0],
}

model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 2) 토큰화 (1.transformers 에서 배운 그 토큰화)
def tokenize(batch):
    return tokenizer(batch["text"], padding="max_length", truncation=True)

train_ds = Dataset.from_dict(train_data).map(tokenize, batched=True)
eval_ds  = Dataset.from_dict(eval_data).map(tokenize, batched=True)

# 3) 모델 = 사전학습 본체 + 새 분류 헤드(2클래스)
#    id2label 로 숫자 라벨에 사람이 읽을 이름을 붙인다 (예측 결과가 NEGATIVE/POSITIVE 로 나옴)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name, num_labels=2,
    id2label={0: "NEGATIVE", 1: "POSITIVE"},
    label2id={"NEGATIVE": 0, "POSITIVE": 1},
)

# 4) 평가지표 — 정확도
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {"accuracy": float((preds == labels).mean())}

# 5) 학습 설정 — 매 에포크 평가, 3 에포크
args = TrainingArguments(
    output_dir="./results",        # 학습 중 체크포인트(중간 산출물)
    eval_strategy="epoch",         # (구버전 transformers 는 evaluation_strategy)
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

# 6) 학습 → 평가
trainer.train()
print("\n평가 결과:", trainer.evaluate())

# 7) 최종 모델 저장 (체크포인트와 별도로 '완성본' 을 따로 저장)
save_path = "./my_local_model"
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)
print(f"\n✅ 내 모델 저장 완료 → {save_path}  (다음: 1.2_predict.py 로 사용)")
