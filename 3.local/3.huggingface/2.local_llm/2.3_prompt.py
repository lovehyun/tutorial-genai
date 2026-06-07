# GPT-Neo-2.7B 모델 크기: 약 10GB

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

# 모델 및 토크나이저 로드
model_name = "EleutherAI/gpt-neo-2.7B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")

# Transformers 텍스트 생성 파이프라인 설정
text_generation_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=150,  # 변경: 생성할 최대 토큰 수
    temperature=0.7,
    top_k=50,
    top_p=0.95,
    repetition_penalty=1.2,
    pad_token_id=tokenizer.eos_token_id  # EOS 토큰 설정으로 중간 끊김 방지
)
# 텍스트 생성 파이프라인 설정:
# max_length: 생성할 텍스트의 최대 길이를 설정합니다.
# temperature: 생성된 텍스트의 다양성을 제어합니다. 낮은 값은 더 결정적인 출력을 생성하고, 높은 값은 더 다양한 출력을 생성합니다.
# top_k: 다음 단어를 선택할 때 고려할 상위 K개의 후보 단어의 수를 설정합니다.
# top_p: 누적 확률이 이 값을 넘지 않도록 후보 단어를 선택합니다.
# repetition_penalty: 텍스트에서 반복되는 단어를 벌점으로 줄여 중복을 방지합니다.
# pad_token_id: 패딩 토큰을 eos_token_id로 설정하여 텍스트 생성을 종료합니다.

# LangChain을 사용하여 HuggingFace 파이프라인 래핑
llm = HuggingFacePipeline(pipeline=text_generation_pipeline)

# 프롬프트 템플릿 정의
prompt_template = PromptTemplate(
    input_variables=["prompt"],
    template="You are a fitness expert. Provide detailed and actionable fitness tips:\n\n{prompt}\n\nFitness Tips:"
)

# 최신 방식으로 LangChain 실행 흐름 구성
qa_chain = prompt_template | llm | RunnableLambda(lambda x: {"response": x})

# 질의응답 수행 및 출력
prompt = "What are good fitness tips?"
answer = qa_chain.invoke({"prompt": prompt})["response"]

print(f"Prompt: {prompt}")
print(f"Answer: {answer}")
