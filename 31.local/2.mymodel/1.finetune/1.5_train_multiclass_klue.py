# (1단계·실전) 다중 분류(multi-class) — KLUE-YNAT 한국어 뉴스 토픽 7종
# pip install transformers torch datasets
#
# 1.4 는 2클래스(부정/긍정)였다. 여기서는 '여러 클래스' 를 분류한다.
#   KLUE-YNAT = 연합뉴스 기사 제목 → 7개 토픽(IT과학/경제/사회/생활문화/세계/스포츠/정치).
#   바뀌는 건 num_labels 와 id2label 뿐 — 파인튜닝 흐름은 1.4 와 동일하다.

# load_dataset("klue", "ynat")도 똑같이 KLUE(Korean Language Understanding Evaluation, 한국어 벤치마크)를 Hub에서 받는 것 — 역시 한국어입니다.

import numpy as np
from datasets import load_dataset
from transformers import (
    AutoModelForSequenceClassification, AutoTokenizer,
    Trainer, TrainingArguments,
)

MODEL = "klue/bert-base"   # 격식체/뉴스 한국어에 강한 표준 한국어 BERT
tokenizer = AutoTokenizer.from_pretrained(MODEL)


# 1) 데이터셋 로드 — KLUE-YNAT: title(기사 제목) + label(0~6)
ds = load_dataset("klue", "ynat", trust_remote_code=True)
LABELS = ds["train"].features["label"].names   # 7개 토픽 이름 (한국어)
print("토픽:", LABELS)

train_ds = ds["train"].shuffle(seed=42).select(range(2000))
eval_ds  = ds["validation"].shuffle(seed=42).select(range(500))


# 2) 토큰화 (입력은 기사 '제목')
def tokenize(batch):
    return tokenizer(batch["title"], padding="max_length", truncation=True, max_length=64)

train_ds = train_ds.map(tokenize, batched=True)
eval_ds  = eval_ds.map(tokenize, batched=True)


# 3) 모델 — ★ num_labels=7, id2label 에 토픽 이름 매핑 (이게 1.4 와의 차이)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL, num_labels=len(LABELS),
    id2label={i: name for i, name in enumerate(LABELS)},
    label2id={name: i for i, name in enumerate(LABELS)},
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {"accuracy": float((preds == labels).mean())}


# 4) 학습
args = TrainingArguments(
    output_dir="./results_ynat",
    eval_strategy="epoch", save_strategy="no",
    per_device_train_batch_size=16, per_device_eval_batch_size=32,
    num_train_epochs=1, logging_steps=25,
)
trainer = Trainer(model=model, args=args,
                  train_dataset=train_ds, eval_dataset=eval_ds,
                  compute_metrics=compute_metrics)
trainer.train()
print("\n평가:", trainer.evaluate())


# 5) 저장 + 예측 테스트 (제목 → 토픽)
save_path = "./my_ynat_model"
model.save_pretrained(save_path); 
tokenizer.save_pretrained(save_path)


from transformers import pipeline
clf = pipeline("text-classification", model=save_path, tokenizer=save_path)
for t in ["삼성전자, 차세대 AI 반도체 공개", "손흥민 시즌 15호골 폭발", "코스피 3% 급등 2800선 돌파"]:
    r = clf(t)[0]
    print(f"  {t} → {r['label']} ({r['score']:.2f})")

# 정리:
#   - 2클래스 → N클래스 전환은 num_labels + id2label 만 바꾸면 끝 (헤드가 자동으로 N개 출력)
#   - 다국어가 아니라 한국어 전용 모델(klue/bert-base)이라 한국어 분류 품질이 좋다
