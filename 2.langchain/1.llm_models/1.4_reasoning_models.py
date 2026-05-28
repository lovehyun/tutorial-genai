"""
Reasoning 모델 — 답하기 전 내부에서 "생각" 단계를 거치는 LLM.
이 예제: OpenAI gpt-5 계열 / Anthropic Claude 의 reasoning 을 호출해 thinking 텍스트를 같이 받습니다.

일반 chat 모델 (gpt-4o-mini 등) vs reasoning 모델
  - chat       : 질문 → 즉시 응답.   내부 추론은 가려져 있음.
  - reasoning  : 질문 → [내부 추론 → 답변]. 추론 텍스트를 별도 채널로 노출 가능.

  reasoning 모델은 수학/코딩/논리 추론에서 강하고, 도구 사용/에이전트와도 잘 결합.
  대신 토큰 비용·지연 시간이 더 큼 (추론에 토큰을 많이 씀).

지원 모델 (2026):
  OpenAI       : gpt-5, gpt-5-mini, o3, o4-mini      → reasoning_effort 옵션
  Anthropic    : claude-opus-4-7, claude-sonnet-4-6   → thinking={enabled, budget_tokens}
  DeepSeek     : deepseek-r1 등                       → reasoning_content 자동 노출
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()


# ============================================================
# (1) OpenAI reasoning 모델
# ============================================================
print("=" * 60)
print("(1) OpenAI gpt-5-mini — reasoning_effort='medium'")
print("=" * 60)

llm = ChatOpenAI(
    model="gpt-5-mini",                # gpt-5 / gpt-5-mini / o3 / o4-mini 등
    reasoning_effort="medium",         # "low" / "medium" / "high"
)

# 추론이 필요한 질문
question = "사과 3개와 배 5개를 가진 사람이 사과 2개를 친구에게 주고, 배 1개를 더 사면 총 과일은 몇 개?"
response = llm.invoke([HumanMessage(content=question)])

print(f"\n[질문] {question}")
print(f"\n[최종 답변]\n{response.content}")

# 모델이 내부 추론을 노출한 경우 — 위치는 모델/API 버전마다 다름
reasoning = (
    response.additional_kwargs.get("reasoning")
    or response.additional_kwargs.get("reasoning_content")
    or response.response_metadata.get("reasoning_summary")
)
if reasoning:
    print(f"\n[🧠 Thinking — 모델 내부 추론]")
    print(str(reasoning)[:1500])
else:
    # gpt-5 는 기본적으로 reasoning 텍스트를 외부에 안 보낼 수 있음 (요약만 / 비공개)
    # → response_metadata 에 reasoning 토큰 수만 들어옴
    usage = response.response_metadata.get("token_usage", {})
    reasoning_tokens = (
        usage.get("completion_tokens_details", {}).get("reasoning_tokens")
        if isinstance(usage, dict) else None
    )
    print(f"\n[ℹ️ ] reasoning 텍스트 노출 안 됨 (모델이 비공개로 처리).")
    if reasoning_tokens is not None:
        print(f"     reasoning 에 사용된 토큰: {reasoning_tokens}")


# ============================================================
# (2) Anthropic Claude — extended thinking
# ============================================================
# Claude 는 thinking 텍스트를 콘텐츠 블록으로 함께 반환 (가장 노출이 명시적)
# 사용하려면:  pip install langchain-anthropic
#              ANTHROPIC_API_KEY=...  in .env
print("\n" + "=" * 60)
print("(2) Anthropic claude-opus-4-7 — extended thinking")
print("=" * 60)

try:
    from langchain_anthropic import ChatAnthropic

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY 미설정 — 건너뜀")
    else:
        claude = ChatAnthropic(
            model="claude-opus-4-7",
            max_tokens=8000,
            thinking={"type": "enabled", "budget_tokens": 4000},
        )
        result = claude.invoke([HumanMessage(content=question)])

        # Claude 의 result.content 는 list of dict — thinking / text 블록이 섞여 옴
        for block in (result.content if isinstance(result.content, list) else []):
            if isinstance(block, dict):
                if block.get("type") == "thinking":
                    print(f"\n[🧠 Thinking]\n{block['thinking'][:1500]}")
                elif block.get("type") == "text":
                    print(f"\n[최종 답변]\n{block['text']}")

except ImportError:
    print("langchain-anthropic 미설치 — 건너뜀  (pip install langchain-anthropic)")


# ─────────────────────────────────────────────────────────
# 정리:
#   - reasoning 모델은 단순 chat 모델보다 비싸고 느리지만 추론 작업에 강함
#   - OpenAI 는 reasoning 토큰을 외부 노출 안 하는 경우 多 (정책상)
#     → reasoning 토큰 카운트만 token_usage 에서 확인 가능
#   - Anthropic 은 thinking 블록을 명시적으로 돌려줌 → 학습/디버깅에 유리
#   - 도구 사용 에이전트와 결합하면 "왜 이 도구를 부르는지" 추적 가능
#     (8.agents/3.builtin_tools/3.1_wikipedia_think.py 참고)
# ─────────────────────────────────────────────────────────
