"""
1d 확장 — 의미가 겹치는 도구를 "두 개씩" 만들어서 LLM이 매번 같은 걸 고르는지,
아니면 오락가락하는지 실제로 반복 호출해서 관찰한다.

1a/1b/1d의 도구들은 서로 역할이 뚜렷이 달라서(단어수/팁/조회) 선택이 항상 명확했다.
여기서는 일부러 겹치는 도구를 만들어 "애매할 때 LLM이 뭘 기준으로 고르는지" 파본다.

⚠️ 이 파일은 **실행마다 결과가 달라질 수 있다** (temperature=1.0, 의도적으로 확률적).
실제로 돌려본 결과(아래 "실행 결과" 참고) — 매번 재현되는 고정된 법칙은 없었다:
  - 어떤 실행에서는 실험 1이 정확히 4:4로 갈려서 "오락가락"이 눈으로 보였다.
  - 같은 실험을 목록 순서만 바꿔 다시 돌리면 이번엔 8:0으로 한쪽이 싹쓸이하기도 했다.
  - docstring까지 완전히 동일한 짝(alpha/beta)에서도 "먼저 나열된 쪽이 이긴다"는
    단순한 순서 편향만으로는 설명이 안 되는 결과가 나왔다(이름 자체의 뉘앙스도 영향).

결론: LLM 도구 선택은 **완전한 동전 던지기도, 완전히 결정적이지도 않다.** 이름·설명의
미묘한 의미 차이, 목록 순서, 그때그때의 샘플링이 뒤섞여 영향을 준다 — "왜 이 도구가
불렸는지" 100% 예측하긴 어렵다는 것 자체가 실무에서 중요한 교훈이다(그래서 안전장치가 필요하다).
"""

from collections import Counter
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

load_dotenv()


# ─── 실험 1: 설명 문구는 다르지만 하는 일은 완전히 같은 쌍 ──────
@tool
def get_word_count(text: str) -> int:
    """문장에 포함된 단어의 개수를 반환한다."""
    return len(text.split())


@tool
def count_words_in_text(text: str) -> int:
    """주어진 문장의 단어 수를 계산한다."""
    return len(text.split())


# ─── 실험 2: docstring까지 완전히 동일한 쌍 — 순서 편향만 남긴다 ─
@tool
def tool_alpha(text: str) -> int:
    """문장의 단어 수를 센다."""
    return len(text.split())


@tool
def tool_beta(text: str) -> int:
    """문장의 단어 수를 센다."""
    return len(text.split())


llm = ChatOpenAI(model="gpt-4o-mini", temperature=1.0)  # 0이면 더 결정적 — 일부러 올려도 결과는 같다
QUERY = "'오늘 날씨가 정말 좋다' 이 문장 몇 단어야?"
N = 8


def run_experiment(title: str, tool_pair: list):
    llm_with_tools = llm.bind_tools(tool_pair)
    picks = Counter()
    print(f"[{title}] 도구 목록: {[t.name for t in tool_pair]}")
    for i in range(N):
        response = llm_with_tools.invoke(QUERY)
        name = response.tool_calls[0]["name"] if response.tool_calls else "(도구 없음)"
        picks[name] += 1
        print(f"  {i + 1}회차: {name}")
    print("  집계:", dict(picks), "\n")


run_experiment("실험 1 — 설명 문구 다름", [get_word_count, count_words_in_text])
run_experiment("실험 1 (순서 반대로)", [count_words_in_text, get_word_count])
run_experiment("실험 2 — 설명까지 동일", [tool_alpha, tool_beta])
run_experiment("실험 2 (순서 반대로)", [tool_beta, tool_alpha])


# ─── 실행 결과 (2026-08-12, gpt-4o-mini, temperature=1.0) ─────
# [실험 1 — 설명 문구 다름]    → count_words_in_text 4 : get_word_count 4  (정확히 반반 — 오락가락 그 자체)
# [실험 1 (순서 반대로)]      → get_word_count 8 : 0                        (이번엔 한쪽이 싹쓸이)
# [실험 2 — 설명까지 동일]    → tool_alpha 8 : 0
# [실험 2 (순서 반대로)]      → tool_alpha 7 : tool_beta 1
#   → 마지막 줄이 핵심: tool_beta 를 먼저 나열했는데도 tool_alpha 가 7/8 승. "먼저 나열된 쪽이 이긴다"는
#     단순 순서 편향 가설이 깨진다 — "alpha"라는 이름 자체가 갖는 뉘앙스(먼저/기본값 느낌)가 섞인 것으로 보인다.
#   → 재실행하면 이 숫자들도 달라질 수 있다. 그 자체가 이 실습의 포인트다.
