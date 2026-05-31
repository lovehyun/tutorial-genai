"""
Wikipedia 에이전트 + Reasoning 모델 — "왜 이 도구를 부르는지" 추론까지 함께 출력.
이 예제: 3.1 과 동일한 위키 도구 에이전트지만, LLM 을 reasoning 모델로 바꿔 thinking 추출.

3.1 (gpt-4o-mini) 와의 차이:
  - 모델: gpt-4o-mini → gpt-5-mini (또는 Anthropic claude-opus-4-7)
  - reasoning_effort / thinking 옵션 추가
  - 결과 출력 시 thinking 블록도 함께 표시

  ※ 자세한 reasoning 모델 개요는 ../../1.llm_models/1.4_reasoning_models.py 참고.


─── 주의 ──────────────────────────────────────────────────────

OpenAI 의 gpt-5 / o-series 는 reasoning 텍스트를 정책상 외부 노출 안 하는 경우 많음
(token usage 의 reasoning_tokens 만 보임). 추론을 명시적으로 받고 싶으면
Anthropic claude-opus-4-7 의 extended thinking 이 가장 노출이 명확함.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain.agents import create_agent

load_dotenv()


# ─── 도구 (3.1 과 동일) ─────────────────────────────────────
wiki_ko = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(lang="ko", top_k_results=3, doc_content_chars_max=2000),
    name="wikipedia_ko",
    description="한국어 위키피디아에서 사실/배경 정보를 검색한다.",
)
wiki_en = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(lang="en", top_k_results=3, doc_content_chars_max=2000),
    name="wikipedia_en",
    description="English Wikipedia. 글로벌 / 영어권 주제용.",
)


system_prompt = """\
당신은 위키피디아로 사실을 확인하는 한국어 비서입니다.
- 한국 주제 → wikipedia_ko, 글로벌 → wikipedia_en
- 같은 주제로 도구 2번 이상 호출 금지
- 결과 빈약하면 그 안에서 답하고 종료
- 출력은 한국어 5문장 이내
"""


# ─── 옵션 A: OpenAI gpt-5-mini (reasoning_effort) ─────────────
USE_CLAUDE = os.getenv("USE_CLAUDE", "").lower() in {"1", "true", "yes"}

if not USE_CLAUDE:
    print("[모델] OpenAI gpt-5-mini  (reasoning_effort='medium')\n")
    llm = ChatOpenAI(
        model="gpt-5-mini",
        reasoning_effort="medium",
    )
else:
    # ─── 옵션 B: Anthropic Claude — thinking 블록을 명시적으로 받음 ──
    from langchain_anthropic import ChatAnthropic
    print("[모델] Anthropic claude-opus-4-7  (extended thinking 5000 tokens)\n")
    llm = ChatAnthropic(
        model="claude-opus-4-7",
        max_tokens=10000,
        thinking={"type": "enabled", "budget_tokens": 5000},
    )


agent = create_agent(llm, [wiki_ko, wiki_en], system_prompt=system_prompt)


# ─── thinking / reasoning 추출 헬퍼 ─────────────────────────
def extract_thinking(message) -> str | None:
    """AIMessage 에서 reasoning / thinking 텍스트가 있으면 꺼낸다.
    OpenAI / Anthropic 등 모델마다 위치가 달라 여러 곳을 시도.
    """
    # 1) Anthropic 스타일 — content 가 블록 리스트
    if isinstance(message.content, list):
        thoughts = []
        for block in message.content:
            if isinstance(block, dict) and block.get("type") == "thinking":
                thoughts.append(block.get("thinking", ""))
        if thoughts:
            return "\n\n".join(thoughts)

    # 2) OpenAI 스타일 — additional_kwargs / response_metadata 안쪽
    for key in ("reasoning", "reasoning_content"):
        v = message.additional_kwargs.get(key)
        if v:
            return str(v)

    rm = getattr(message, "response_metadata", {}) or {}
    for key in ("reasoning_summary", "reasoning"):
        if key in rm:
            return str(rm[key])

    return None


# ─── 실행 ─────────────────────────────────────────────────
for q in [
    "세종대왕은 누구이고 어떤 업적을 남겼어?",
    "Python 프로그래밍 언어는 누가 만들었고, 왜 이름이 'Python' 이야?",
]:
    print("=" * 60)
    print(f"[질문] {q}")
    print("=" * 60)

    try:
        result = agent.invoke(
            {"messages": [("user", q)]},
            config={"recursion_limit": 15},
        )
    except Exception as e:
        print(f"  [에러] {type(e).__name__}: {e}\n")
        continue

    for m in result["messages"]:
        # AI 가 추론한 thinking 노출 (있다면)
        if m.type == "ai":
            thinking = extract_thinking(m)
            if thinking:
                print(f"\n  🧠 [Thinking]\n  {thinking[:500].replace(chr(10), chr(10) + '  ')}\n")

        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → 도구: {c['name']}({c['args']})")
        if m.type == "tool":
            content = m.content if isinstance(m.content, str) else str(m.content)
            print(f"  ← 결과: {content[:100]}...")

    # 최종 답변
    final = result["messages"][-1]
    final_text = (
        final.content if isinstance(final.content, str)
        else "".join(b.get("text", "") for b in final.content if isinstance(b, dict) and b.get("type") == "text")
    )
    print(f"\n[최종 답변]\n{final_text}\n")


# ─────────────────────────────────────────────────────────
# 실행 비교 팁:
#   1) USE_CLAUDE=1 환경변수 켜고 다시 돌리면 Claude thinking 이 더 풍부하게 보임
#   2) 같은 질문을 3.1_wikipedia.py (gpt-4o-mini) 와 이 파일로 각각 돌려서
#      "추론 흐름 노출 여부" / "정확도" / "응답 시간" 차이를 체감해보세요
# ─────────────────────────────────────────────────────────
