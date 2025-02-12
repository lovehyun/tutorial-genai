from transformers import pipeline

# 1️. 로컬 모델 불러오기
classifier = pipeline("sentiment-analysis", model="./my_local_model", tokenizer="./my_local_model")

# 2️. 감성 분석 실행
result = classifier("I feel amazing today!")[0]
print(result)



# 1. 로컬 모델 로드
classifier = pipeline("sentiment-analysis", model="./my_local_model", tokenizer="./my_local_model")

# 2. 감성 분석 실행
test_sentences = [
    "이 모델을 사용하니 정말 좋아요!",
    "이건 최악의 경험이었어요.",
    "오늘 너무 행복해요!",
    "기분이 너무 안 좋아..."
]

# for text in test_sentences:
#     result = classifier(text)[0]
#     print(f"📢 Input: {text} → 🎯 Prediction: {result}")


label_map = {"LABEL_0": "부정", "LABEL_1": "긍정"}

for text in test_sentences:
    result = classifier(text)[0]
    sentiment = label_map.get(result["label"], "알 수 없음")
    print(f"📢 입력: {text} → 🎯 예측: {sentiment} (신뢰도: {result['score']:.4f})")

