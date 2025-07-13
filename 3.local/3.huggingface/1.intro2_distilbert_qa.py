from transformers import pipeline

# 질문 답변 모델 로드
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# 질문과 문맥 제공
context = "Hugging Face is a company that develops open-source AI models and NLP tools."
question = "What does Hugging Face develop?"

# 질문 답변 실행
result = qa_pipeline(question=question, context=context)

# 결과 출력
print(f"질문: {question}\n답변: {result['answer']} (신뢰도: {result['score']:.4f})")
