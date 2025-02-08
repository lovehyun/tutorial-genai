import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# 1. 원래 모델과 동일한 구조 생성 (float32 상태)
model_name = "bert-base-uncased"
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# 2. 모델을 다시 양자화하여 동일한 구조로 변환
model = torch.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)

# 3. 양자화된 모델 가중치 로드
load_path = "./quantized_model"
checkpoint = torch.load(f"{load_path}/pytorch_model.bin")

# 4. 모델에 가중치 로드 (strict=False 추가)
model.load_state_dict(checkpoint["model_state_dict"], strict=False)

# 5. 분류기 가중치 복원 (classifier.weight & classifier.bias)
model.classifier.weight = torch.nn.Parameter(checkpoint["classifier_weight"])
model.classifier.bias = torch.nn.Parameter(checkpoint["classifier_bias"])

# 6. 모델을 평가 모드로 변경 (필수)
model.eval()

# 7. 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained(load_path)

# 8. 감성 분석 실행 (PyTorch 직접 사용)
def predict(text):
    inputs = tokenizer(text, return_tensors="pt")  # 입력을 텐서로 변환
    with torch.no_grad():  # 그래디언트 계산 비활성화 (추론용)
        outputs = model(**inputs)
    logits = outputs.logits
    predicted_class = torch.argmax(logits).item()  # 가장 높은 확률의 클래스 선택
    labels = {0: "NEGATIVE", 1: "POSITIVE"}
    return labels[predicted_class]

# 9. 예제 문장 테스트
test_sentences = [
    "I love using my own AI model!",
    "This is the worst experience ever.",
    "I am extremely happy today!",
    "I feel so bad...",
    "This app is fantastic!",
    "Not impressed at all.",
    "Absolutely love this movie!",
    "What a waste of money."
]

# 10. 결과 출력
for text in test_sentences:
    result = predict(text)
    print(f"📢 Input: {text} → 🎯 Prediction: {result}")
