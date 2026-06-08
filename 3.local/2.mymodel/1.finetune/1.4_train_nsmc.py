# (1단계·실전) 진짜 한국어 데이터셋으로 파인튜닝 — NSMC 영화리뷰 감성분류
# pip install transformers torch datasets
#
# 1.3 은 8문장짜리 '토이 데이터' 였다. 여기서는 실제 공개 데이터셋(NSMC, 네이버 영화리뷰
# 15만 건)을 HuggingFace Hub 에서 받아 학습한다. → 실전 파인튜닝의 표준 흐름.
#   (학습 시간을 줄이려고 일부만 샘플링한다. 전체로 하면 정확도는 더 오른다.)


# 1) "빌트인(내장)"이 아닙니다 — 인터넷에서 다운로드
# load_dataset("nsmc")는 datasets 라이브러리에 들어있는 게 아니라, HuggingFace Hub(huggingface.co/datasets/nsmc)에서 처음 호출 때 
# 다운로드해서 로컬 캐시(~/.cache/huggingface/datasets)에 저장합니다. 라이브러리는 '받아오는 로더'만 제공합니다.
#
# 2) NSMC는 한국어 데이터입니다 (영어 아님)
# 이름 NSMC = Naver Sentiment Movie Corpus(네이버 영화리뷰)가 영어 약자라서 헷갈리신 것 같은데, 내용물은 한국어 영화 리뷰입니다. 
# NSMC는 이미 정답이 달린(labeled) 데이터셋입니다. 각 리뷰에 사람이 매긴 label(0=부정, 1=긍정)이 함께 들어 있어요. 
# 이게 있어야 지도학습(supervised) 이 가능합니다 — "이 문장의 정답은 부정"이라고 알려줘야 모델이 배우니까요.


import numpy as np
from datasets import load_dataset
from transformers import (
    AutoModelForSequenceClassification, AutoTokenizer,
    Trainer, TrainingArguments,
)

MODEL = "beomi/KcBERT-base"   # 댓글/리뷰체 한국어에 강한 BERT (1.3 과 동일 계열)
tokenizer = AutoTokenizer.from_pretrained(MODEL)

# 1) 데이터셋 로드 — NSMC: document(리뷰) + label(0=부정, 1=긍정)
#    빈 리뷰 제거 후, 데모용으로 train 2000 / test 500 샘플
ds = load_dataset("nsmc", trust_remote_code=True)

train_ds = ds["train"].filter(lambda x: bool(x["document"])).shuffle(seed=42).select(range(2000))
eval_ds  = ds["test"].filter(lambda x: bool(x["document"])).shuffle(seed=42).select(range(500))
print(f"학습 {len(train_ds)} / 평가 {len(eval_ds)} 건  (예: {train_ds[0]['document'][:30]}... → {train_ds[0]['label']})")


# 2) 토큰화 (리뷰는 짧아 max_length 64 면 충분)
def tokenize(batch):
    return tokenizer(batch["document"], padding="max_length", truncation=True, max_length=64)

train_ds = train_ds.map(tokenize, batched=True)
eval_ds  = eval_ds.map(tokenize, batched=True)


# 3) 모델 — 2클래스 분류 헤드 + 라벨 이름
# Auto - 모델 이름만 주면 그 모델의 아키텍처(BERT/RoBERTa/DistilBERT…)를 자동 판별해 맞는 클래스로 로드. (그래서 MODEL만 바꿔도 코드 그대로)
# ForSequenceClassification - "시퀀스(=문장 전체)를 분류" 하는 용도 → 사전학습 본체 위에 분류 헤드(classifier) 를 얹어준다
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL, num_labels=2,
    id2label={0: "부정", 1: "긍정"}, label2id={"부정": 0, "긍정": 1},
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {"accuracy": float((preds == labels).mean())}


# 4) 학습 — 실제 데이터라 배치를 키우고 1 에포크만으로도 의미있는 정확도가 나온다
args = TrainingArguments(
    output_dir="./results_nsmc",
    eval_strategy="epoch", save_strategy="no",
    per_device_train_batch_size=16, per_device_eval_batch_size=32,
    num_train_epochs=1, logging_steps=25,
)
trainer = Trainer(model=model, args=args,
                  train_dataset=train_ds, eval_dataset=eval_ds,
                  compute_metrics=compute_metrics)
trainer.train()
print("\n평가:", trainer.evaluate())


# 5) 저장 + 바로 예측 테스트
save_path = "./my_nsmc_model"
model.save_pretrained(save_path); 
tokenizer.save_pretrained(save_path)


from transformers import pipeline
clf = pipeline("sentiment-analysis", model=save_path, tokenizer=save_path)
for t in ["연기도 좋고 정말 감동적이었어요", "시간 아까운 최악의 영화"]:
    r = clf(t)[0]
    print(f"  {t} → {r['label']} ({r['score']:.2f})")


# 정리:
#   - 토이 데이터(1.3) → 실제 데이터셋(여기) 이 핵심 차이. 흐름은 동일(토큰화→학습→평가→저장)
#   - 더 키우려면 select(range(N)) 의 N 을 늘리거나 num_train_epochs 를 올린다
#   - 다음(1.5): 2클래스가 아니라 '여러 클래스'(뉴스 토픽 7종) 분류
