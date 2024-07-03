# GPT-Neo-2.7B 모델 크기: 약 10GB

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
    # text_generation_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)
    text_generation_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_length=150,
        temperature=0.7,
        top_k=50,
        top_p=0.95,
        repetition_penalty=1.2,
        pad_token_id=tokenizer.eos_token_id
    )
    # 텍스트 생성 파이프라인 설정:
    # max_length: 생성할 텍스트의 최대 길이를 설정합니다.
    # temperature: 생성된 텍스트의 다양성을 제어합니다. 낮은 값은 더 결정적인 출력을 생성하고, 높은 값은 더 다양한 출력을 생성합니다.
    # top_k: 다음 단어를 선택할 때 고려할 상위 K개의 후보 단어의 수를 설정합니다.
    # top_p: 누적 확률이 이 값을 넘지 않도록 후보 단어를 선택합니다.
    # repetition_penalty: 텍스트에서 반복되는 단어를 벌점으로 줄여 중복을 방지합니다.
    # pad_token_id: 패딩 토큰을 eos_token_id로 설정하여 텍스트 생성을 종료합니다.

    # LangChain을 사용하여 파이프라인 래핑
    llm = HuggingFacePipeline(pipeline=text_generation_pipeline)

    # 프롬프트 템플릿 정의
    prompt_template = PromptTemplate(
        input_variables=["prompt"],
        # template="{prompt}"
        template = "You are a fitness expert. Provide detailed and actionable fitness tips in response to the following question:\n\n{prompt}\n\nFitness Tips:"
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
