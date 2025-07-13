from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate

from langchain_openai import OpenAI
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.runnables import RunnableLambda

# 환경 변수 로드
load_dotenv()

# 목적:
# Chain1: 요리사 역할 프롬프트 + Completion 모델
# Chain2: 다국어 번역 프롬프트 + Completion 모델
# Chain3: 번역 결과를 comma-separated list로 파싱하는 체인

# 1-1. 요리사 역할 프롬프트 설정
prompt1 = PromptTemplate.from_template(
    "You are a cook. Answer the following question. <Q>: {input}?"
)

# 1-2. Completion 기반 LLM 모델 설정
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.5)

# 1-3. 체인 구성 (프롬프트 → LLM → 후처리)
chain1 = prompt1 | llm | RunnableLambda(lambda x: {"response": x.strip()})

# 1-4. 실행
print("\n[Chain1 결과]")
print(chain1.invoke({"input": "How is Kimchi made"})["response"])


# 2-1. 번역 프롬프트 설정 (PromptTemplate으로 작성)
system_prompt = PromptTemplate.from_template(
    "You are a professional language translator who translates {input_language} to {output_language}. Text: {text}"
)

# 2-2. 체인 구성 (시스템 프롬프트 포함 번역 요청)
chain2 = system_prompt | llm | RunnableLambda(lambda x: {"response": x.strip()})

# 2-3. 체인3: comma로 구분된 번역 결과를 리스트로 파싱
chain3 = system_prompt | llm | CommaSeparatedListOutputParser()

# 2-4. 실행 예시
inputs = {
    "input_language": "영어",
    "output_language": "한국어",
    "text": "Hello, Nice to meet you."
}

print("\n[Chain2 결과]")
print(chain2.invoke(inputs)["response"])

print("\n[Chain3 결과]")
print(chain3.invoke(inputs))
