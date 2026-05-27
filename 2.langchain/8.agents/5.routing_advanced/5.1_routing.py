"""
다중 도구 라우팅 — 어떤 도구를 쓸지 LLM 이 판단

legacy 의 `9.smartagent_router*` 는 직접 if/else 분기로 라우팅했지만,
**현행 표준은 `create_react_agent` 에 도구 여러 개를 그냥 등록**하는 것.
모델이 알아서 어떤 도구를 부를지 (또는 아무것도 안 부를지) 판단한다.

LLM (특히 gpt-4o 계열) 의 tool calling 이 정확해서 별도 라우터 필요 없음.
정말 라우팅 로직을 명시하고 싶으면 LangGraph 의 RunnableBranch 또는 그래프 노드로 구현.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langgraph.prebuilt import create_react_agent

load_dotenv()


# ─── 다양한 도구 등록 ──────────────────────────────────────
@tool
def calculator(expression: str) -> str:
    """수학 계산을 수행한다. 입력 예시: '15 * 24', '(3+5) * 2'"""
    try:
        # 안전 처리: eval 대신 ast.literal_eval 등이 더 안전하지만 데모용
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"계산 오류: {e}"


wiki_ko = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(lang="ko", top_k_results=2, doc_content_chars_max=1500),
    name="wikipedia_ko",
    description="한국어 위키피디아. 사실/배경/인물 정보 조회.",
)


@tool
def get_current_time() -> str:
    """현재 시각을 반환한다 (서버 기준). 시간/날짜 관련 질문에 사용."""
    from datetime import datetime
    return datetime.now().isoformat(timespec="seconds")


# ─── 시스템 프롬프트 — 라우팅 가이드라인 ───────────────────
system_prompt = """\
당신은 사용자 질문에 가장 적합한 도구를 선택해 답하는 한국어 어시스턴트입니다.

도구 선택 기준:
- 계산 / 수식 → calculator
- 사실/인물/배경 지식 → wikipedia_ko
- 현재 시각 → get_current_time
- 위 어디에도 해당 안 되는 일반 대화/의견 → 도구 없이 직접 답변

도구 결과를 그대로 출력하지 말고, 사용자에게 자연스러운 한국어로 풀어 설명하세요.
"""


# ─── 에이전트 ─────────────────────────────────────────────
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_react_agent(
    llm,
    [calculator, wiki_ko, get_current_time],
    prompt=system_prompt,
)


# ─── 다양한 질문으로 라우팅 확인 ───────────────────────────
questions = [
    "153 곱하기 (3.2 + 4.8) 은 얼마야?",        # → calculator
    "세종대왕은 누구야?",                        # → wikipedia_ko
    "지금 몇 시야?",                              # → get_current_time
    "오늘 기분 어떻게 풀어줄까?",                  # → 도구 없이 직접 답변
]

for q in questions:
    print("=" * 60)
    print(f"[질문] {q}")
    print("=" * 60)
    result = agent.invoke({"messages": [("user", q)]})

    # 어떤 도구를 호출했는지 추적
    used_tools = []
    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                used_tools.append(c["name"])

    if used_tools:
        print(f"[사용한 도구] {', '.join(used_tools)}")
    else:
        print(f"[사용한 도구] (없음 — 모델이 직접 답변)")

    print(f"[답변] {result['messages'][-1].content}\n")


# ─────────────────────────────────────────────────────────
# Legacy 대비:
#   ❌ 9.smartagent_router*.py:
#      - decide_tool() 로 LLM 한번 호출 → 어떤 도구 쓸지 판정
#      - 그 결과 보고 단일 도구 에이전트를 동적 생성
#      - hard_rule_decision() 같은 키워드 분기 룰 따로 작성
#      - 코드 200줄+
#
#   ✅ 현행 (이 파일):
#      - 도구 다 등록하고 LLM 에게 맡김
#      - 모델이 tool calling 으로 알아서 판단
#      - 코드 ~70줄
#      - gpt-4o 의 tool selection 정확도가 높아서 별도 라우터 불필요
#
# 명시적 라우팅이 꼭 필요하면? → LangGraph 의 RunnableBranch / StateGraph 분기
#   (9.langgraph/ 폴더 참고)
# ─────────────────────────────────────────────────────────
