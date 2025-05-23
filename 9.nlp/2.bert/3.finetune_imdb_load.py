from transformers import BertTokenizer, BertForSequenceClassification
import torch

# 1. 저장된 모델과 토크나이저 불러오기
model_path = "./fine_tuned_bert_imdb"
model = BertForSequenceClassification.from_pretrained(model_path)
tokenizer = BertTokenizer.from_pretrained(model_path)

# 2. 예측할 문장들
texts = [
    "This movie was absolutely wonderful. The story was touching and the acting was great!",
    "I hated this movie. It was boring and way too long."
]

# 3. 토크나이징 (배치 처리)
inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=256)

# 4. 모델 예측
model.eval()
with torch.no_grad():
    outputs = model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=1)

# 5. 결과 출력
label_map = {0: "부정", 1: "긍정"}
for text, pred in zip(texts, predictions):
    print(f"문장: {text}")
    print(f"→ 예측 감정: {label_map[pred.item()]}")
    print("-" * 40)
