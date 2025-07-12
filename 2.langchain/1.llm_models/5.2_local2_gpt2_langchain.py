# pip install transformers accelerate torch langchain langchain-core langchain-huggingface

# GPT2 모델 크기: 약 0.5GB

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

# 1. 사용할 모델 이름 지정 (Hugging Face 모델 허브 기준)
model_name = "gpt2"

# 2. 토크나이저와 모델 로드 (처음 실행 시 ~/.cache/huggingface에 저장됨)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# 3. Hugging Face의 text-generation 파이프라인 구성
#    - max_new_tokens: 생성할 최대 토큰 수
#    - temperature: 창의성 제어 (0~1 범위)
#    - pad_token_id: GPT2는 pad token이 없으므로 eos_token으로 대체
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=128,
    temperature=0.7,
    pad_token_id=tokenizer.eos_token_id
)

# 4. LangChain의 HuggingFacePipeline 래퍼로 랭체인 형식으로 변환
llm = HuggingFacePipeline(pipeline=generator)

# 5. LangChain용 프롬프트 템플릿 정의
#    - input_variables: 외부에서 넘겨줄 프롬프트 변수 이름
#    - template: 실제로 모델에 전달할 프롬프트 구조
prompt_template = PromptTemplate(
    input_variables=["prompt"],
    template="{prompt}"
)

# 6. 체인 구성: 프롬프트 → LLM → 후처리 (response만 딕셔너리로 감쌈)
qa_chain = prompt_template | llm | RunnableLambda(lambda x: {"response": x})

# 7. 실행 함수 정의 (입력 프롬프트를 넣으면 응답 반환)
def answer_question(prompt):
    result = qa_chain.invoke({"prompt": prompt})  # invoke()로 체인 실행
    return result["response"]

# 8. 테스트 실행
prompt = "What are some good fitness tips?"
answer = answer_question(prompt)

# 9. 결과 출력
print(f"Prompt: {prompt}")
print(f"Answer: {answer}")
