import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

# 캐시에 저장된 모델을 로드 (이미 다운로드된 모델 사용)
model_name = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"  # 여기에 원하는 모델명을 입력

tokenizer = DistilBertTokenizer.from_pretrained(model_name, local_files_only=True)
model = DistilBertForSequenceClassification.from_pretrained(model_name, local_files_only=True)

print("로컬 모델 로드 완료!")


# 입력 문장
text = "I love this product! It's amazing."

# 토큰화 (PyTorch 텐서 변환)
inputs = tokenizer(text, return_tensors="pt")

# 모델 추론 (GPU 사용 가능)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device) # gpu (또는 cpu) 로 이동

with torch.no_grad():
    outputs = model(**{k: v.to(device) for k, v in inputs.items()})
    
# 결과 해석
logits = outputs.logits

predicted_class_id = logits.argmax().item()
predicted_label = model.config.id2label[predicted_class_id]  # 모델에서 직접 라벨 매핑 가져오기

# 감성 라벨 매핑
print(f"📢 입력: {text} → 🎯 예측: {predicted_label}")
