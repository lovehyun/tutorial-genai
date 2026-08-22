# curl -X POST http://localhost:5000/predict \
#     -H "Content-Type: application/json" \
#     -d '{"texts": [
#         "Apple unveils new AI chip for next-gen iPhones",
#         "Global markets fall amid economic uncertainty",
#         "NASA discovers new Earth-like planet",
#         "Brazil wins World Cup after thrilling match"
#     ]}'

from flask import Flask, request, jsonify
from transformers import BertTokenizer, BertForSequenceClassification
import torch

app = Flask(__name__)

# 1. 모델 및 토크나이저 로드
model_path = "./saved_model/agnews_bert"
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForSequenceClassification.from_pretrained(model_path)
model.eval()

# 2. 클래스 매핑
label_map = {
    0: "World",
    1: "Sports",
    2: "Business",
    3: "Science/Technology"
}

# 3. 예측 API
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    texts = data.get("texts", [])
    if not texts:
        return jsonify({"error": "texts 필드가 필요합니다."}), 400

    # 토크나이징
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=128)

    # 모델 추론
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.argmax(outputs.logits, dim=1)

    # 결과 반환
    results = [
        {"text": text, "category": label_map[pred.item()]}
        for text, pred in zip(texts, predictions)
    ]
    return jsonify(results)

# 4. 서버 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
