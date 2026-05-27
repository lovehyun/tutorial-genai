# curl -X POST http://localhost:5000/predict \
#     -H "Content-Type: application/json" \
#     -d '{"texts": [
#         "I really loved this movie!",
#         "It was a waste of time. Terrible acting."
#     ]}'

from flask import Flask, request, jsonify
from transformers import BertTokenizer, BertForSequenceClassification
import torch

app = Flask(__name__)

# 1. 모델과 토크나이저 불러오기
model_path = "./fine_tuned_bert_imdb"
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForSequenceClassification.from_pretrained(model_path)
model.eval()

# 2. 예측 라벨 매핑
label_map = {0: "부정", 1: "긍정"}

# 3. 예측 API
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    texts = data.get("texts", [])
    if not texts:
        return jsonify({"error": "texts 항목이 필요합니다."}), 400

    # 토크나이징
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=256)

    # 모델 예측
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.argmax(outputs.logits, dim=1)

    # 결과 매핑
    results = [
        {"text": text, "prediction": label_map[pred.item()]}
        for text, pred in zip(texts, predictions)
    ]
    return jsonify(results)

# 4. 서버 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
