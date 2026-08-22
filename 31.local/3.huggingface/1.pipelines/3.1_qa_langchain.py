# 모델 크기 : 약 0.25GB
# DistilBERT 아키텍처를 사용하여 사전 훈련된 모델로, SQuAD (Stanford Question Answering Dataset) 데이터셋에서 
# 추가로 파인튜닝된 모델. 주로 질의응답 태스크를 수행하는 데 사용.

from transformers import DistilBertTokenizer, DistilBertForQuestionAnswering, pipeline
from langchain_core.runnables import RunnableLambda

# 모델과 토크나이저 로드
model_name = "distilbert-base-uncased-distilled-squad"
tokenizer = DistilBertTokenizer.from_pretrained(model_name)
model = DistilBertForQuestionAnswering.from_pretrained(model_name)

# Transformers QA 파이프라인 설정
qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

# 질의응답 체인 생성 (최신 LangChain 방식 적용)
qa_chain = RunnableLambda(lambda x: qa_pipeline(x)) | RunnableLambda(lambda x: {"answer": x["answer"]})

# 예제 질문 및 문맥
context = """
Hugging Face Inc. is a company based in New York City. Its headquarters are in DUMBO, therefore very close to the Manhattan Bridge.
"""
question = "Where is Hugging Face based?"

# 질의응답 수행 및 결과 출력
answer = qa_chain.invoke({"question": question, "context": context})["answer"]

print(f"Question: {question}")
print(f"Answer: {answer}")
