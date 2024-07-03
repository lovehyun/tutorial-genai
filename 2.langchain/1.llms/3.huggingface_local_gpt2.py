# pip install transformers
# ~/.cache/huggingface 디렉토리 안에 모델 다운로드 됨

# GPT2 모델 크기: 약 0.5GB

from transformers import AutoModelForCausalLM, AutoTokenizer
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def main():
    # 공개 Hugging Face 모델과 토크나이저를 로드합니다.
    model_name = "gpt2"  # 접근 가능한 모델로 변경
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
        return result['text']

    # 예제 질문과 문맥
    prompt = "What are good fitness tips?"

    # 질의응답 수행
    answer = answer_question(prompt)
    print(f"Prompt: {prompt}")
    print(f"Answer: {answer}")

if __name__ == '__main__':
    main()
