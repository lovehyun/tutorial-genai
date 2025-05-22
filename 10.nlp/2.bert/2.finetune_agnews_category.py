from datasets import load_dataset
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from sklearn.metrics import accuracy_score
import numpy as np
import torch

# 1. 데이터셋 로드 (4개 뉴스 카테고리)
dataset = load_dataset("ag_news")
train_data = dataset["train"].shuffle(seed=42).select(range(2000))   # 빠른 실습용
test_data = dataset["test"].shuffle(seed=42).select(range(500))

# 2. 토크나이저 불러오기 및 토큰화 함수 정의
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

def tokenize(example):
    return tokenizer(example["text"], padding="max_length", truncation=True, max_length=128)

# 3. 토큰화 적용
train_data = train_data.map(tokenize, batched=True)
test_data = test_data.map(tokenize, batched=True)

# 4. 텐서 포맷으로 설정
train_data.set_format("torch", columns=["input_ids", "attention_mask", "label"])
test_data.set_format("torch", columns=["input_ids", "attention_mask", "label"])

# 5. 모델 준비 (num_labels = 4)
model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=4)

# 6. 평가 지표 함수 정의
def compute_metrics(eval_pred):
    preds = np.argmax(eval_pred.predictions, axis=1)
    return {"accuracy": accuracy_score(eval_pred.label_ids, preds)}

# 7. 학습 파라미터 설정
training_args = TrainingArguments(
    output_dir="./results_agnews",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs_agnews",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    load_best_model_at_end=True
)

# 8. Trainer 객체 생성
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_data,
    eval_dataset=test_data,
    compute_metrics=compute_metrics,
)

# 9. 학습 시작
trainer.train()

# 10. 모델 저장 (명시적)
save_path = "./saved_model/agnews_bert"
trainer.save_model(save_path) # 모델 저장
tokenizer.save_pretrained(save_path) # 토크나이저 저장

print(f"모델이 저장되었습니다: {save_path}")
