# pip install transformers
# ~/.cache/huggingface 디렉토리 안에 모델 다운로드 됨

# GPT2 모델 크기: 약 0.5GB

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

# Hugging Face 모델과 토크나이저 로드
model_name = "gpt2"  # Hugging Face에서 지원되는 모델
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")  # GPU 자동 활용

# Transformers 텍스트 생성 파이프라인 설정
text_generation_pipeline = pipeline(
    "text-generation", 
    model=model, 
    tokenizer=tokenizer, 
    max_new_tokens=128, 
    temperature=0.7,
    # pad_token_id=tokenizer.eos_token_id  # EOS 토큰 설정 (중간 끊김 방지)
)

# LangChain을 사용하여 HuggingFace 파이프라인 래핑
llm = HuggingFacePipeline(pipeline=text_generation_pipeline)

# 프롬프트 템플릿 정의
prompt_template = PromptTemplate(
    input_variables=["prompt"],
    template="{prompt}"
)

 # RunnableSequence를 사용한 최신 방식 적용
qa_chain = prompt_template | llm | RunnableLambda(lambda x: {"response": x})

# 질의응답 수행 함수
def answer_question(prompt):
    result = qa_chain.invoke({"prompt": prompt})  # 최신 버전에서 invoke 사용
    return result["response"]

# 예제 질문 실행
prompt = "What are good fitness tips?"
answer = answer_question(prompt)

print(f"Prompt: {prompt}")
print(f"Answer: {answer}")
