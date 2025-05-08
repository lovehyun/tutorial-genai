from transformers import AutoModelForSequenceClassification

# 원본 모델 로드
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")

# 특정 레이어만 남기고 제거 (예: 상위 6개 레이어 제거)
model.bert.encoder.layer = model.bert.encoder.layer[:6]

# 모델 저장
model.save_pretrained("./reduced_model")
print("✅ 불필요한 레이어 제거 완료!")
