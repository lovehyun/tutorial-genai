from transformers import pipeline

# 이름 엔터티 인식(NER) 모델 로드
ner_pipeline = pipeline("ner", model="dbmdz/distilbert-base-german-cased")

# 테스트 문장
text = "Elon Musk is the CEO of Tesla."

# NER 실행
results = ner_pipeline(text)

# 결과 출력
for entity in results:
    print(f"엔터티: {entity['word']} → 타입: {entity['entity']} (신뢰도: {entity['score']:.4f})")
