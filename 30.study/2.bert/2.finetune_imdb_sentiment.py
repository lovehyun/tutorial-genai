# pip install transformers datasets scikit-learn
# 소요 시간 (대략)
# 조건	                            소요 시간
# 데이터 5,000개 + 3 epoch	        약 10~20분 (GPU 사용 시)
# CPU만 사용할 경우	                1~2시간 이상
# 전체 IMDB 데이터셋 (25,000개)	    GPU 기준 30분~1시간 이상

from datasets import load_dataset
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
import numpy as np
from sklearn.metrics import accuracy_score

# 1. 데이터 불러오기 (IMDB 리뷰)
dataset = load_dataset("imdb")
train_data = dataset["train"].shuffle(seed=42).select(range(5000))  # 빠른 실습용
test_data = dataset["test"].shuffle(seed=42).select(range(1000))

# 2. 토크나이저
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

def tokenize(batch):
    return tokenizer(batch["text"], padding="max_length", truncation=True, max_length=256)

train_data = train_data.map(tokenize, batched=True)
test_data = test_data.map(tokenize, batched=True)

train_data.set_format("torch", columns=["input_ids", "attention_mask", "label"])
test_data.set_format("torch", columns=["input_ids", "attention_mask", "label"])

# 3. 모델 선언 (2-class classification)
model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)

# 4. 평가 지표 함수
def compute_metrics(p):
    preds = np.argmax(p.predictions, axis=1)
    return {"accuracy": accuracy_score(p.label_ids, preds)}

# 5. 학습 파라미터
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    load_best_model_at_end=True
)

# 6. Trainer 객체
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_data,
    eval_dataset=test_data,
    compute_metrics=compute_metrics,
)

# 7. 학습 시작
trainer.train()

# 8. 모델 + 토크나이저 저장
save_path = "./fine_tuned_bert_imdb"
trainer.save_model(save_path)
tokenizer.save_pretrained(save_path)
