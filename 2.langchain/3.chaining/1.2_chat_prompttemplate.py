from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.runnables import RunnableLambda

# 환경 변수 로드
load_dotenv()

# 목적:
# Chain1: 요리사 역할 프롬프트 + Chat 모델
# Chain2: 다국어 번역 프롬프트 + Chat 모델
# Chain3: 번역 결과를 comma-separated list로 파싱하는 체인

# 1-1. 요리사 역할 프롬프트 설정
chat_prompt1 = ChatPromptTemplate.from_template(
    "You are a cook. Answer the following question. <Q>: {input}?"
)

# 1-2. Chat 기반 LLM 모델 설정
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)

# 1-3. 체인 구성 (프롬프트 → LLM → 후처리)
chain1 = chat_prompt1 | llm | RunnableLambda(lambda x: {"response": x.content.strip()})

# 1-4. 실행
print("\n[Chain1 결과]")
print(chain1.invoke({"input": "How is Kimchi made"})["response"])


# 2-1. 번역 프롬프트 설정 (System + Human 메시지 조합)
system_template = "You are a professional language translator who translates {input_language} to {output_language}"
system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
human_message_prompt = HumanMessagePromptTemplate.from_template("{text}")

# 2-2. 시스템 + 사용자 메시지를 ChatPrompt로 묶기
chat_prompt2 = ChatPromptTemplate.from_messages([
    system_message_prompt,
    human_message_prompt
])

# 2-3. 체인 구성
chain2 = chat_prompt2 | llm | RunnableLambda(lambda x: {"response": x.content.strip()})
chain3 = chat_prompt2 | llm | CommaSeparatedListOutputParser()

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
