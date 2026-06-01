"""
응용 — 빌트인 도구 + 커스텀 도구를 한 에이전트에 함께 묶기.
이 예제: 위키피디아(빌트인, 1단계) + 계산기(커스텀, 2단계) 를 합쳐
        "사실 조회 → 그 값으로 계산" 을 한 번에 처리하는 에이전트.

1·2단계의 합류 지점:
  - 1.builtin_tools  : 도구를 "가져다" 쓴다 (load_tools)
  - 2.custom_tools   : 도구를 "직접 만든다" (@tool)
  - 여기(3단계)       : 둘을 한 tools 리스트에 그냥 같이 넣는다 → LLM 이 알아서 순서 결정

핵심: 빌트인이든 커스텀이든 에이전트 입장에선 똑같은 '도구' 일 뿐.
      섞는 데 특별한 코드가 필요 없다.

  ※ pip install wikipedia
"""

import wikipedia
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import create_agent

load_dotenv()

# Wikipedia 는 2024+ 부터 기본 User-Agent 를 차단 → 일반 브라우저 UA 로 교체해야 동작
# (안 하면 빈 응답이 와서 JSONDecodeError. Wikimedia User-Agent 정책)
wikipedia.wikipedia.USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


# ─── 커스텀 도구 (2단계 방식) ───────────────────────────────
@tool
def calculator(expression: str) -> str:
    """수학 식을 계산한다. 예: '330 / 3.3'"""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"오류: {e}"


# ─── 빌트인 + 커스텀 을 한 리스트로 합치기 ──────────────────
tools = load_tools(["wikipedia"]) + [calculator]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, tools)


# 위키로 사실(높이) 조회 → 계산기로 환산, 두 도구가 연쇄로 호출됨
question = "에펠탑의 높이를 찾아서, 그 높이가 한 층 3.3m 기준 몇 층 건물에 해당하는지 계산해줘."

result = agent.invoke({"messages": [("user", question)]})

print("=" * 60)
print(f"[질문] {question}")
print("=" * 60)
for m in result["messages"]:
    if hasattr(m, "tool_calls") and m.tool_calls:
        for c in m.tool_calls:
            print(f"  → 도구: {c['name']}({c['args']})")
print(f"\n[답변] {result['messages'][-1].content}")
