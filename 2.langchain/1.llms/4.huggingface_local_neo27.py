# GPT-Neo-2.7B 모델 크기: 약 10GB
# GPT-Neo-2.7B는 27억 개의 매개변수를 갖고 있습니다. 이는 매우 큰 모델로, 다양한 언어 이해 및 생성 작업에서 뛰어난 성능을 발휘할 수 있습니다.
# 이 모델은 다양한 웹 텍스트 데이터로 훈련되었습니다. 여기에는 Wikipedia, Common Crawl, Reddit 및 기타 대규모 데이터셋이 포함됩니다.

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

# 더 큰 모델과 토크나이저 로드
model_name = "EleutherAI/gpt-neo-2.7B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")

# Transformers 텍스트 생성 파이프라인 설정
text_generation_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=256,  # 더 긴 응답 생성 가능
    temperature=0.7,  # 자연스러운 응답을 위한 설정
    do_sample=True,  # 샘플링 활성화
    pad_token_id=tokenizer.eos_token_id  # 중간 끊김 방지
)

# LangChain을 사용하여 HuggingFace 파이프라인 래핑
llm = HuggingFacePipeline(pipeline=text_generation_pipeline)

# 프롬프트 템플릿 정의 (질문 반복 방지 및 명확한 역할 부여)
prompt_template = PromptTemplate(
    input_variables=["prompt"],
    template="You are a fitness expert. Provide detailed and actionable fitness tips in response to the following question:\n\n{prompt}\n\nFitness Tips:"
)

# RunnableSequence를 사용한 최신 LangChain 방식 적용
qa_chain = prompt_template | llm | RunnableLambda(lambda x: {"response": x})

# 질의응답 수행 및 출력
prompt = "What are good fitness tips?"
answer = qa_chain.invoke({"prompt": prompt})["response"]

print(f"Prompt: {prompt}")
print(f"Answer: {answer}")
