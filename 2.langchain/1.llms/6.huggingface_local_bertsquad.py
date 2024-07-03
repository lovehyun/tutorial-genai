# 모델 크기 : 약 0.25GB
# DistilBERT 아키텍처를 사용하여 사전 훈련된 모델로, SQuAD (Stanford Question Answering Dataset) 데이터셋에서 
# 추가로 파인튜닝된 모델. 주로 질의응답 태스크를 수행하는 데 사용.

from transformers import DistilBertTokenizer, DistilBertForQuestionAnswering, pipeline

def main():
    # 모델과 토크나이저를 로드합니다.
    model_name = "distilbert-base-uncased-distilled-squad"
    tokenizer = DistilBertTokenizer.from_pretrained(model_name)
    model = DistilBertForQuestionAnswering.from_pretrained(model_name)

    # Transformers 파이프라인을 사용하여 QA 파이프라인을 설정합니다.
    qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

    # 질의응답 함수 정의
    def answer_question(question, context):
        inputs = {
            'question': question,
            'context': context
        }
        result = qa_pipeline(inputs)
        return result['answer']

    # 예제 질문과 문맥
    context = """
    Hugging Face Inc. is a company based in New York City. Its headquarters are in DUMBO, therefore very close to the Manhattan Bridge.
    """
    question = "Where is Hugging Face based?"

    # 질의응답 수행
    answer = answer_question(question, context)
    print(f"Question: {question}")
    print(f"Answer: {answer}")

if __name__ == '__main__':
    main()
