"""
4b — 주제 범위 제한 적용 (4a와 똑같은 질문으로 테스트)
# pip install langchain-ollama   (GUARDRAIL_PROVIDER=ollama 로 로컬 모델을 쓸 때만 필요)

두 겹으로 막는다:
  ① 프롬프트로 유도 — 시스템 프롬프트에 스코프를 명시하고 벗어나면 거절하도록 지시 (싸다, 하지만 가끔 새어나감)
  ② 별도 분류기로 사후 검증 — "이 질문이 스코프 안인가?"를 LLM 분류기로 한 번 더 판정 (더 견고, 호출 1회 추가)
"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
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

# ── ① 프롬프트로 유도 ──
scoped_prompt = ChatPromptTemplate.from_messages([
    ("system",
     f"당신은 오직 '{SCOPE}'에 대해서만 답하는 챗봇입니다. "
     f"그 외 주제(일반 상식, 다른 회사 업무, 사적인 조언 등)를 물으면 "
     f"'죄송하지만 저는 휴가·연차 정책만 안내해드릴 수 있어요.'라고만 답하세요."),
    ("human", "{question}"),
])
scoped_chain = scoped_prompt | llm


# ── ② 분류기로 사후 검증 — 프롬프트 유도가 뚫렸을 때의 안전망 ──
class ScopeVerdict(BaseModel):
    in_scope: bool = Field(description=f"질문이 '{SCOPE}' 범위 안이면 True")


scope_judge_prompt = ChatPromptTemplate.from_messages([
    ("system", f"질문이 '{SCOPE}' 범위 안인지만 판정하세요."),
    ("human", "{question}"),
])
scope_judge_chain = scope_judge_prompt | llm.with_structured_output(ScopeVerdict)

OUT_OF_SCOPE_MESSAGE = "죄송하지만 저는 휴가·연차 정책만 안내해드릴 수 있어요."


def ask_within_scope(question: str) -> str:
    # 사후 검증을 답변 생성보다 먼저 해서, 스코프 밖이면 답변 생성 호출 자체를 아낀다.
    verdict = scope_judge_chain.invoke({"question": question})
    print(f"  [내부] 스코프 판정: in_scope={verdict.in_scope}")
    if not verdict.in_scope:
        return OUT_OF_SCOPE_MESSAGE
    return scoped_chain.invoke({"question": question}).content


if __name__ == "__main__":
    print("=== 4b: 스코프 제한 적용 (4a와 동일 질문) ===")
    print(f"질문(스코프 밖): {OFF_TOPIC_QUESTION}\n")

    answer = ask_within_scope(OFF_TOPIC_QUESTION)
    print(f"\n답변: {answer}")

    print("\n👉 4a.topic_unscoped.py 는 같은 질문에 그냥 답했었다.")
