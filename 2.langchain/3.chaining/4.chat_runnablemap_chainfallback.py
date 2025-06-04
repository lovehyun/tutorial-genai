import os
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnableMap
from langchain_core.runnables.utils import RunnableConfig

# 환경 변수 로드
load_dotenv()

# 목적:
# Chain1: 요리사 역할 프롬프트 + Chat 모델
# Chain2: 다국어 번역 프롬프트 + Chat 모델
# Chain3: 번역 결과를 comma-separated list로 파싱하는 체인
# Chain4: 병렬로 두 번역 결과를 동시에 처리하는 체인 (RunnableParallel)
# Chain5: 반복 번역 요청을 일괄 처리하는 배치 체인 (invoke_batch)
# Chain6: 입력 필드를 매핑해 다르게 구성한 체인 (RunnableMap)
# Chain7: 예외 상황 시 기본 응답을 지정하는 fallback 체인 (with_fallbacks)

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

# 3. RunnableParallel 예제 (두 개의 체인을 동시에 실행)
parallel_chain = RunnableParallel({
    "translated_text": chain2,
    "comma_list": chain3
})

print("\n[Chain4 결과 - 병렬 실행]")
parallel_result = parallel_chain.invoke(inputs)
print(parallel_result)

# 4. invoke_batch 예제 (여러 입력값에 대해 일괄 처리)
batch_inputs = [
    {"input_language": "영어", "output_language": "한국어", "text": "Good morning."},
    {"input_language": "영어", "output_language": "프랑스어", "text": "Good evening."}
]

print("\n[Chain5 결과 - 배치 실행]")
batch_results = chain2.batch(batch_inputs)
for i, result in enumerate(batch_results):
    print(f"[{i+1}] {result['response']}")

# 5. RunnableMap 예제: 입력 필드 리매핑 (예: 'question'을 'input'으로 바꿔줌)
map_chain = RunnableMap({
    "input": lambda x: x["question"]
}) | chain1

print("\n[Chain6 결과 - 필드 매핑 체인]")
print(map_chain.invoke({"question": "How do you make pasta?"})["response"])

# 6. Fallback 예제: 실패 시 기본 응답 제공
fallback_chain = chain2.with_fallbacks([
    RunnableLambda(lambda x: {"response": "⚠️ Translation failed. Please try again later."})
])

print("\n[Chain7 결과 - Fallback 체인]")
try:
    print(fallback_chain.invoke(inputs)["response"])
except Exception as e:
    print(f"예외 발생: {e}")

