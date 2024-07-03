# GPT-Neo-2.7B 모델 크기: 약 10GB
# GPT-Neo-2.7B는 27억 개의 매개변수를 갖고 있습니다. 이는 매우 큰 모델로, 다양한 언어 이해 및 생성 작업에서 뛰어난 성능을 발휘할 수 있습니다.
# 이 모델은 다양한 웹 텍스트 데이터로 훈련되었습니다. 여기에는 Wikipedia, Common Crawl, Reddit 및 기타 대규모 데이터셋이 포함됩니다.

from transformers import AutoModelForCausalLM, AutoTokenizer
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def main():
    # 더 큰 모델과 토크나이저를 로드합니다.
    model_name = "EleutherAI/gpt-neo-2.7B"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Transformers 파이프라인을 사용하여 텍스트 생성 파이프라인을 설정합니다.
    from transformers import pipeline
    text_generation_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)

    # LangChain을 사용하여 파이프라인 래핑
    llm = HuggingFacePipeline(pipeline=text_generation_pipeline)

    # 프롬프트 템플릿 정의
    prompt_template = PromptTemplate(
        input_variables=["prompt"],
        template="{prompt}"
        # template = "You are a fitness expert. Provide detailed and actionable fitness tips in response to the following question:\n\n{prompt}\n\nFitness Tips:"
    )

    # LangChain 질의응답 체인 설정
    qa_chain = LLMChain(
        llm=llm,
        prompt=prompt_template
    )

    # 질의응답 함수 정의
    def answer_question(prompt):
        inputs = {
            'prompt': prompt
        }
        result = qa_chain.invoke(inputs)
        # LangChain의 invoke 메서드 결과가 적절히 처리되었는지 확인
        if isinstance(result, str):
            return result
        elif isinstance(result, dict) and 'text' in result:
            return result['text']
        else:
            return "Unexpected response format from the model"

    # 예제 질문과 문맥
    prompt = "What are good fitness tips?"

    # 질의응답 수행
    answer = answer_question(prompt)
    print(f"Prompt: {prompt}")
    print(f"Answer: {answer}")

if __name__ == '__main__':
    main()
