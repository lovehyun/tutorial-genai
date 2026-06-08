"""
에이전트 평가 (1) — '올바른 도구를 골랐는가' 를 자동 검증.
이 예제: 외부 의존성 없이, 테스트 케이스를 돌려 에이전트의 도구 선택을 채점한다.

왜 필요한가?
  - 에이전트는 비결정적 → "그냥 돌려보니 잘 되더라" 로는 회귀(regression)를 못 잡음
  - 프롬프트/모델/도구를 바꿀 때마다 핵심 시나리오가 여전히 통과하는지 확인 필요
  - 가장 기본 지표: (1) 의도한 도구를 불렀는가  (2) 안 불러야 할 때 안 불렀는가

  ※ 여기선 messages 를 직접 뜯어 보는 '손으로 만든' 평가입니다.
     실전에선 LangSmith Evaluations / agentevals 같은 도구로 확장 (정리 참고).
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent

load_dotenv()


@tool
def calculator(expression: str) -> str:
    """수학 식을 계산한다."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"오류: {e}"


@tool
def get_weather(city: str) -> str:
    """도시 날씨를 조회한다."""
    return {"서울": "맑음, 22도"}.get(city, "정보 없음")


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, [calculator, get_weather])


# ─── 실행 결과에서 '호출된 도구 이름들' 추출 ────────────────
def tools_called(result) -> list[str]:
    names = []
    for m in result["messages"]:
        for c in getattr(m, "tool_calls", []) or []:
            names.append(c["name"])
    return names


# ─── 테스트 케이스: 입력 → 기대 도구 ───────────────────────
#   expect = 도구 이름  → 그 도구를 한 번 이상 불러야 통과
#   expect = None       → 어떤 도구도 부르지 않고 바로 답해야 통과
CASES = [
    {"q": "123 * 7 은 얼마야?",        "expect": "calculator"},
    {"q": "서울 날씨 어때?",            "expect": "get_weather"},
    {"q": "안녕? 반가워!",              "expect": None},          # 도구 불필요
    {"q": "(10 + 5) / 3 계산해줘",      "expect": "calculator"},
]


# ─── 채점 ───────────────────────────────────────────────────
passed = 0
print("=" * 60)
print("도구 선택 평가")
print("=" * 60)
for i, case in enumerate(CASES, 1):
    result = agent.invoke({"messages": [("user", case["q"])]})
    called = tools_called(result)
    expect = case["expect"]

    if expect is None:
        ok = len(called) == 0
    else:
        ok = expect in called

    passed += ok
    mark = "✅ PASS" if ok else "❌ FAIL"
    print(f"{mark} [{i}] {case['q']}")
    print(f"        기대={expect}  실제={called or '없음'}")

print("-" * 60)
print(f"결과: {passed}/{len(CASES)} 통과")


# 정리:
#   - 가장 기본 평가 = 도구 선택 정확도 (불러야 할 때/말아야 할 때)
#   - 확장 방향:
#       · 도구 '인자' 까지 검증 (예: city == '서울')
#       · 최종 답변 품질은 LLM-as-judge 로 채점 (9.3_parallelization_eg2 참고)
#       · LangSmith Evaluations / agentevals 로 데이터셋·리포트 자동화
#   - temperature=0 으로 두면 평가 재현성 ↑
