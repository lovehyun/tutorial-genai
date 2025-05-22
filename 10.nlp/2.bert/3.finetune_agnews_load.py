from transformers import BertTokenizer, BertForSequenceClassification

# 모델 불러오기
model = BertForSequenceClassification.from_pretrained("./saved_model/agnews_bert")
tokenizer = BertTokenizer.from_pretrained("./saved_model/agnews_bert")

# 예측
text = "Google stock hits record high"
inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
outputs = model(**inputs)
pred = outputs.logits.argmax(dim=1).item()

print(f"예측 클래스: {pred}")
