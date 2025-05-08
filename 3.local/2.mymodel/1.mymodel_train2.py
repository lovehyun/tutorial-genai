import os
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
from datasets import Dataset, DatasetDict

# 1. 학습 데이터 확장 (긍정 4개, 부정 4개)
train_data = {
    "text": [
        "I love this!", "This is terrible!", "I am happy.", "I am sad.",
        "This product is amazing!", "Worst experience ever.", "Absolutely fantastic!", "I hate it."
    ],
    "label": [1, 0, 1, 0, 1, 0, 1, 0]  # 긍정(1), 부정(0)
}

# 2. 평가 데이터 확장 (긍정 2개, 부정 2개)
eval_data = {
    "text": [
        "I feel great today!", "The service was awful.", 
        "I'm super excited about this!", "Not what I expected."
    ],
    "label": [1, 0, 1, 0]  # 긍정(1), 부정(0)
}

# 3. Hugging Face `datasets` 변환
train_dataset = Dataset.from_dict(train_data)
eval_dataset = Dataset.from_dict(eval_data)

# 4. 사전 학습된 모델과 토크나이저 불러오기
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 5. 데이터셋을 토큰화
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True)

tokenized_train_dataset = train_dataset.map(tokenize_function, batched=True)
tokenized_eval_dataset = eval_dataset.map(tokenize_function, batched=True)

# 6. Hugging Face `DatasetDict`로 변환
split_dataset = DatasetDict({
    "train": tokenized_train_dataset,
    "eval": tokenized_eval_dataset
})

# 7. 감성 분석 모델 생성
# model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

# 7. 감성 분석 모델 생성 (id2label 추가)
# id2label (숫자->라벨): 모델이 예측한 숫자 ID를 사람이 이해할 수 있는 라벨로 변환
# label2id (라벨 → 숫자): 훈련 데이터에서 사람이 정의한 라벨을 숫자로 변환
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=2,
    id2label={0: "NEGATIVE", 1: "POSITIVE"},  # 라벨 이름 지정
    label2id={"NEGATIVE": 0, "POSITIVE": 1}
)

# 8. 훈련 설정 (FutureWarning 해결: `eval_strategy` 사용)
output_dir = "./my_model"  # 중간 파일과 최종 모델 저장 폴더 통일
training_args = TrainingArguments(
    output_dir=output_dir,
    eval_strategy="epoch",
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    num_train_epochs=3,  # 🔥 학습 성능 향상을 위해 3 에포크 수행
    save_strategy="epoch"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=split_dataset["train"],
    eval_dataset=split_dataset["eval"]
)

# 9. 모델 학습
trainer.train()

# 10. 학습이 끝난 모델을 저장
save_path = "./my_local_model"
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)

print(f"✅ 모델이 {save_path} 에 저장되었습니다!")
