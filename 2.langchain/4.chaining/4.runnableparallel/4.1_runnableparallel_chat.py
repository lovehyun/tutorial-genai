from dotenv import load_dotenv
from time import perf_counter

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnableMap

# 환경 변수 로드
load_dotenv()
import os
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set")

# 목적:
# Chain1: 요리사 역할 프롬프트 + Chat 모델
# Chain2: 다국어 번역 프롬프트 + Chat 모델
# Chain4: 병렬로 두 번역 결과를 동시에 처리하는 체인 (RunnableParallel)
# Chain5: 반복 번역 요청을 일괄 처리하는 배치 체인 (invoke_batch)

# -----------------------------------------------------------------------------
# Chain1: 요리사 역할 (기존 예제 유지)
# -----------------------------------------------------------------------------
chat_prompt1 = ChatPromptTemplate.from_template(
    "You are a cook. Answer the following question. <Q>: {input}?"
)

# 1-2. Chat 기반 LLM 모델 설정
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

# 1-3. 체인 구성 (프롬프트 → LLM → 후처리)
chain1 = chat_prompt1 | llm | RunnableLambda(lambda x: {"response": x.content.strip()})

# 1-4. 실행
print("\n[Chain1 결과]")
print(chain1.invoke({"input": "How is Kimchi made"})["response"])


# -----------------------------------------------------------------------------
# 번역 체인 구성 (입력언어는 영어로 고정, 출력언어만 partial로 주입)
#   - 동일한 입력에 대해 한국어/프랑스어/일본어로 번역 3개를 실행
#   - 순차 실행 vs 병렬 실행 시간 비교
# -----------------------------------------------------------------------------

# 2-1. 번역 프롬프트 설정 (System + Human 메시지 조합)
# system_template = "You are a professional language translator who translates {input_language} to {output_language}"
# system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
# human_message_prompt = HumanMessagePromptTemplate.from_template("{text}")

# 2-2. 시스템 + 사용자 메시지를 ChatPrompt로 묶기
# chat_prompt2 = ChatPromptTemplate.from_messages([
#     system_message_prompt,
#     human_message_prompt
# ])

# 2-3. 체인 구성
# chain2 = chat_prompt2 | llm | RunnableLambda(lambda x: {"response": x.content.strip()})
# chain3 = chat_prompt2 | llm | CommaSeparatedListOutputParser()

# 2-4. 실행 예시
# inputs = {
#     "input_language": "영어",
#     "output_language": "한국어",
#     "text": "Hello, Nice to meet you."
# }

# print("\n[Chain2 결과]")
# print(chain2.invoke(inputs)["response"])

# print("\n[Chain3 결과]")
# print(chain3.invoke(inputs))


base_translate_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a professional language translator who translates {input_language} to {output_language}. "
     "Be accurate and concise."),
    ("human", "{text}")
]).partial(input_language="영어")

# 각 언어별 체인 (출력언어를 partial로 고정)
chain_to_ko = (base_translate_prompt.partial(output_language="한국어") | llm
               | RunnableLambda(lambda x: {"response": x.content.strip()}))
chain_to_fr = (base_translate_prompt.partial(output_language="프랑스어") | llm
               | RunnableLambda(lambda x: {"response": x.content.strip()}))
chain_to_ja = (base_translate_prompt.partial(output_language="일본어") | llm
               | RunnableLambda(lambda x: {"response": x.content.strip()}))

# 테스트 입력
text_input = {"text": "Hello, nice to meet you. I hope we can work together on this project."}

t0 = perf_counter()
res_ko_seq = chain_to_ko.invoke(text_input)["response"]
res_fr_seq = chain_to_fr.invoke(text_input)["response"]
res_ja_seq = chain_to_ja.invoke(text_input)["response"]
t1 = perf_counter()
sequential_elapsed = t1 - t0

print("\n[순차 실행 결과]")
print("KO:", res_ko_seq)
print("FR:", res_fr_seq)
print("JA:", res_ja_seq)
print(f"[순차 실행 소요 시간] {sequential_elapsed:.3f} sec")


# 3. RunnableParallel 예제 (두 개의 체인을 동시에 실행)
parallel_chain = RunnableParallel({
    "to_ko": chain_to_ko,
    "to_fr": chain_to_fr,
    "to_ja": chain_to_ja
})

# 4. invoke_batch 예제 (여러 입력값에 대해 일괄 처리)
print("\n[Chain4 결과 - 병렬 실행]")
t2 = perf_counter()
parallel_result = parallel_chain.invoke(text_input)
t3 = perf_counter()
parallel_elapsed = t3 - t2

print("\n[병렬 실행 결과]")
print("KO:", parallel_result["to_ko"]["response"])
print("FR:", parallel_result["to_fr"]["response"])
print("JA:", parallel_result["to_ja"]["response"])
print(f"[병렬 실행 소요 시간] {parallel_elapsed:.3f} sec")


speedup = (sequential_elapsed / parallel_elapsed) if parallel_elapsed > 0 else float('inf')
print("\n[비교 요약]")
print(f"- 순차:  {sequential_elapsed:.3f}s")
print(f"- 병렬:  {parallel_elapsed:.3f}s")
print(f"- 가속비(speedup): x{speedup:.2f}")
