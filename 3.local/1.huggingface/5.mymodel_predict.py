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
    "I love using my own AI model!",
    "This is the worst experience ever.",
    "I am extremely happy today!",
    "I feel so bad..."
]

for text in test_sentences:
    result = classifier(text)[0]
    print(f"📢 Input: {text} → 🎯 Prediction: {result}")
