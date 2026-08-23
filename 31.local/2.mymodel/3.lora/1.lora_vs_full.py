# pip install transformers torch datasets peft
#
# LoRA(Low-Rank Adaptation) — `1.finetune/1.1_train.py`와 똑같은 토이 감성분류 작업을 이번엔
# **전체 파라미터를 학습하지 않고** 아주 작은 어댑터만 학습해서 푼다.
#
# 왜 필요한가: distilbert(6600만 파라미터)는 전체 파인튜닝도 CPU로 감당되지만, 실전에서 쓰는
# Mistral 7B·Llama 8B 같은 모델은 전체 파인튜닝에 GPU 메모리가 수십GB 필요하다. LoRA는 원본
# 가중치는 그대로 얼려두고(freeze), 각 레이어 옆에 작은 저랭크 행렬(A, B) 두 개만 추가로 학습한다
# — 이 저장소의 `4.mistral/`·`5.llama/`처럼 큰 모델을 "내 데이터로 커스터마이즈"하려면 사실상
# 필수적인 기법이다.

import numpy as np
from transformers import (
    AutoModelForSequenceClassification, AutoTokenizer,
    Trainer, TrainingArguments,
)
from datasets import Dataset
from peft import LoraConfig, get_peft_model, TaskType

# 1) 데이터 — 1.finetune/1.1_train.py 와 동일(비교를 위해 일부러 똑같이 맞췄다)
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


def tokenize(batch):
    return tokenizer(batch["text"], padding="max_length", truncation=True)


train_ds = Dataset.from_dict(train_data).map(tokenize, batched=True)
eval_ds = Dataset.from_dict(eval_data).map(tokenize, batched=True)

base_model = AutoModelForSequenceClassification.from_pretrained(
    model_name, num_labels=2,
    id2label={0: "NEGATIVE", 1: "POSITIVE"},
    label2id={"NEGATIVE": 0, "POSITIVE": 1},
)

# [관전 포인트 1] 원본 파라미터 수 — 이 중 대부분은 이제부터 '얼린다'(freeze).
total_params = sum(p.numel() for p in base_model.parameters())

# [관전 포인트 2] LoRA 설정 — r(랭크)이 작을수록 학습 파라미터가 적어진다.
#   target_modules: distilbert의 어텐션 Q/K/V/출력 projection 레이어 이름.
#   ("이 레이어들 옆에 저랭크 어댑터를 붙여라"는 뜻 — 모델 구조마다 레이어 이름이 다르다.)
lora_config = LoraConfig(
    task_type=TaskType.SEQ_CLS,
    r=8,                     # 저랭크 행렬의 랭크(차원) — 작을수록 가볍고 표현력은 낮아진다
    lora_alpha=16,           # 스케일링 계수 (보통 r의 2배 정도로 시작)
    lora_dropout=0.1,
    target_modules=["q_lin", "k_lin", "v_lin"],  # distilbert의 attention 프로젝션 레이어
)
model = get_peft_model(base_model, lora_config)

# [관전 포인트 3] 실제로 학습되는 파라미터가 전체의 몇 %인지 — LoRA의 핵심 수치.
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"\n전체 파라미터:      {total_params:,}")
print(f"LoRA 학습 파라미터:  {trainable_params:,} ({trainable_params / total_params * 100:.3f}%)")
print("(나머지는 원본 가중치 그대로 얼려둔 상태 — 원본 모델은 전혀 훼손되지 않는다)\n")


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {"accuracy": float((preds == labels).mean())}


args = TrainingArguments(
    output_dir="./results_lora",
    eval_strategy="epoch",
    save_strategy="no",   # LoRA 어댑터는 학습 후 별도로 save_pretrained (아래 참고)
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

# [관전 포인트 4] 저장하면 원본 모델(수백MB) 전체가 아니라 '어댑터'(수백KB~수MB)만 저장된다.
save_path = "./my_lora_adapter"
model.save_pretrained(save_path)
print(f"\n✅ LoRA 어댑터 저장 완료 → {save_path}")
print("   (1.finetune/1.1_train.py 의 전체 저장본과 용량을 비교해볼 것)")
