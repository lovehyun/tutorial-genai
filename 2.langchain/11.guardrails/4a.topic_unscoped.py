"""
4a — 주제 범위 제한 없음 (엉뚱한 질문에도 답해버림)
# pip install langchain-ollama   (GUARDRAIL_PROVIDER=ollama 로 로컬 모델을 쓸 때만 필요)

사내 챗봇이 "회사 휴가 정책"만 안내해야 하는데 스코프 제한이 없으면 아무 주제나 답해버린다.
신뢰도 문제(엉뚱한 답)와 비용 낭비(불필요한 호출)가 함께 생긴다.

테스트 질문은 일부러 "로또 번호 예측"처럼 모델이 알아서 거절할 만한 것 대신,
불특정 다수의 어시스턴트가 흔쾌히 답해줄 만한 '중립적으로 도움이 되는' 질문을 썼다 —
그래야 "스코프 제한이 없어서 답해버림"이라는 현상이 명확하게 재현된다.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

PROVIDER = os.getenv("GUARDRAIL_PROVIDER", "openai")
OLLAMA_MODEL = os.getenv("GUARDRAIL_OLLAMA_MODEL", "qwen2.5:7b")

if PROVIDER == "ollama":
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)
    print(f"[모델] Ollama · {OLLAMA_MODEL} (로컬)\n")
else:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    print("[모델] OpenAI · gpt-4o-mini\n")

SCOPE = "회사의 휴가·연차 정책"
OFF_TOPIC_QUESTION = "파이썬으로 피보나치 수열 구하는 함수 짜줘"

# [문제] 스코프를 시스템 프롬프트에 명시만 했을 뿐 강제하는 장치가 없다.
unscoped_prompt = ChatPromptTemplate.from_messages([
    ("system", f"당신은 '{SCOPE}'를 안내하는 챗봇입니다."),
    ("human", "{question}"),
])
unscoped_chain = unscoped_prompt | llm


if __name__ == "__main__":
    print("=== 4a: 스코프 제한 없음 ===")
    print(f"질문(스코프 밖): {OFF_TOPIC_QUESTION}\n")

    answer = unscoped_chain.invoke({"question": OFF_TOPIC_QUESTION}).content
    print(f"답변: {answer}")

    print("\n👉 휴가 정책과 무관한 질문에 그냥 답해버렸는지 확인할 것.")
    print("   4b.topic_scoped.py 에서 같은 질문이 어떻게 거절되는지 비교.")
