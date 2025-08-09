from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnableMap
from langchain_core.runnables.config import RunnableConfig

# 핵심 학습 포인트
# 1. 단일 체인 구성
#  - ChatPromptTemplate + ChatOpenAI + RunnableLambda
#  - 프롬프트로 역할 설정(요리사), LLM 호출, 응답 후처리까지 단일 흐름 구현
# 2. 출력 형식 지정
#  - CommaSeparatedListOutputParser를 통해 LLM 출력 형식을 강제하고 구조화
# 3. 병렬 실행 (RunnableParallel)
#  - 두 개 이상의 체인을 동시에 실행시켜 속도와 처리량을 높이는 방법 실습
# 4. 배치 실행 (.batch)
#  - 여러 입력을 한 번에 처리하여 대량 요청 처리 패턴 학습
# 5. 입력 매핑 (RunnableMap)
#  - 들어오는 데이터 구조를 변환해 다른 체인에 맞게 전달하는 방법
# 6. 예외 대비 (with_fallbacks)
#  - 실행 실패 시 대체 체인으로 폴백(fallback) 응답 제공

# ============================================================
# [0] 환경 변수 로드 및 API 키 확인
# ============================================================
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set")

# ============================================================
# [1] 공용 LLM 설정
# ============================================================
# - gpt-4o-mini 모델 사용 (가볍고 빠른 범용 모델)
# - temperature=0.5로 응답 다양성 조절
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

# ============================================================
# [2] Chain1: 요리사 역할 체인
# ============================================================
# 2-1. 프롬프트 설정
chat_prompt1 = ChatPromptTemplate.from_template(
    "You are a cook. Answer the following question in 2 concise sentences. <Q>: {input}?"
)

# 2-2. 체인 구성 (프롬프트 → LLM → 후처리)
chain1 = chat_prompt1 | llm | RunnableLambda(lambda x: {"response": x.content.strip()})

# 2-3. 실행 예시
print("\n[Chain1 결과]")
print(chain1.invoke({"input": "How is Kimchi made"})["response"])

# ============================================================
# [3] Chain2 & Chain3: 번역 체인 + CSV 파서 체인
# ============================================================
# 3-1. CommaSeparatedListOutputParser 준비
parser = CommaSeparatedListOutputParser()
format_hint = parser.get_format_instructions()

# 3-2. 번역 프롬프트 (CSV 형식 출력 강제)
chat_prompt2 = ChatPromptTemplate.from_messages([
    ("system", "You are a professional language translator who translates {input_language} "
               "to {output_language}. Return only a comma-separated list. {format_hint}"),
    ("human", "{text}")
]).partial(format_hint=format_hint)

# 3-3. 번역 체인 (일반 문자열 응답)
chain2 = chat_prompt2 | llm | RunnableLambda(lambda x: {"response": x.content.strip()})

# 3-4. CSV 파서 체인 (결과를 리스트로 파싱)
chain3 = chat_prompt2 | llm | parser

# 3-5. 실행 예시
inputs = {"input_language": "영어", "output_language": "한국어", "text": "Hello, Nice to meet you."}
print("\n[Chain2 결과]"); print(chain2.invoke(inputs)["response"])
print("\n[Chain3 결과]"); print(chain3.invoke(inputs))

# ============================================================
# [4] Chain4: 병렬 실행 (RunnableParallel)
# ============================================================
# - chain2와 chain3를 동시에 실행
parallel_chain = RunnableParallel({
    "translated_text": chain2,
    "comma_list": chain3
})
cfg = RunnableConfig(max_concurrency=3)  # 동시 실행 제한
print("\n[Chain4 결과 - 병렬 실행]")
print(parallel_chain.invoke(inputs, cfg))

# ============================================================
# [5] Chain5: 배치 실행 (.batch)
# ============================================================
batch_inputs = [
    {"input_language": "영어", "output_language": "한국어", "text": "Good morning."},
    {"input_language": "영어", "output_language": "프랑스어", "text": "Good evening."}
]
print("\n[Chain5 결과 - 배치 실행]")
for i, r in enumerate(chain2.batch(batch_inputs, config=RunnableConfig(max_concurrency=2)), 1):
    print(f"[{i}] {r['response']}")

# ============================================================
# [6] Chain6: RunnableMap (입력 필드 매핑)
# ============================================================
# - 'question' 필드를 'input' 필드로 변경하여 chain1에 전달
map_chain = RunnableMap({
    "input": lambda x: x.get("question", "")
}) | chain1
print("\n[Chain6 결과 - 필드 매핑 체인]")
print(map_chain.invoke({"question": "How do you make pasta?"})["response"])

# ============================================================
# [7] Chain7: Fallback 체인 (with_fallbacks)
# ============================================================
# - chain2가 실패하면 기본 응답 제공
fallback_chain = chain2.with_fallbacks([
    RunnableLambda(lambda x: {"response": "Translation failed. Please try again later."})
])
print("\n[Chain7 결과 - Fallback 체인]")
print(fallback_chain.invoke(inputs)["response"])
