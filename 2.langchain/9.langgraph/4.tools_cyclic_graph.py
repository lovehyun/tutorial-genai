"""
4_tools_cyclic_graph.py - 도구 사용과 순환(cyclic) 그래프

3번(조건부 분기, DAG)과 달리 여기서는 **순환(cycle)** 이 있는 그래프를 직접 만든다.
ReAct 루프: agent(LLM) 가 도구를 호출하면 tools 노드 실행 → 결과를 다시 agent 로 되먹임
→ 더 이상 도구가 필요 없을 때(LLM 이 그냥 답하면) END.

그래프 구조 (StateGraph 로 직접 구성):
    ┌───────┐     ┌──────────┐  tool_calls 있음   ┌─────────┐
    │ START │──▶ │  agent   │ ─────────────────▶ │  tools  │
    └───────┘     │  (LLM)   │ ◀───────────────── │ ToolNode│
                  └──────────┘   도구 결과 되먹임   └─────────┘
                      │
                      │ tool_calls 없음 = 최종 답변 (tools_condition → END)
                      ▼
                   ┌─────┐
                   │ END │
                   └─────┘

핵심: add_edge("tools", "agent") 가 '순환' 을 만든다. add_conditional_edges 의
      tools_condition 이 "도구 더 호출" vs "끝(END)" 을 판단한다.
      (create_agent 같은 프리빌트는 이 그래프를 자동 생성해 숨기지만, 여기선 직접 만든다)
"""

import uuid
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

print("=" * 50)
print("4단계: 도구 사용과 순환(cyclic) 그래프 — StateGraph 직접 구성")
print("=" * 50)

# 1. LLM 초기화
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. 도구 정의
class SearchInput(BaseModel):
    """검색 도구 입력 스키마"""
    query: str = Field(description="검색할 쿼리")

@tool(args_schema=SearchInput)
def search_tool(query: str) -> str:
    """검색 엔진을 사용하여 정보를 찾습니다."""
    print(f"  [도구] 검색: '{query}'")
    search_results = {
        "인공지능": "인공지능(AI)은 인간의 학습·추론·지각·문제해결 능력을 컴퓨터로 구현하는 기술입니다.",
        "파이썬": "파이썬은 인터프리터식, 객체지향, 동적 타이핑의 대화형 프로그래밍 언어입니다.",
        "날씨": "특정 지역의 날씨 정보는 기상청 웹사이트에서 확인할 수 있습니다.",
        "랑그래프": "LangGraph 는 복잡한 에이전트 기반 AI 앱을 그래프로 구축하는 프레임워크입니다.",
        "에이전트": "AI 에이전트는 환경을 인식하고 자율적으로 의사결정해 목표를 달성하는 시스템입니다.",
    }
    for key, value in search_results.items():
        if key in query.lower():
            return value
    return f"'{query}'에 대한 정보를 찾을 수 없습니다."

@tool
def calculator(expression: str) -> str:
    """간단한 수학 계산을 수행합니다. 예: '3 * (4 + 5)'"""
    print(f"  [도구] 계산: '{expression}'")
    try:
        return f"계산 결과: {eval(expression)}"
    except Exception as e:
        return f"계산 오류: {e}"

@tool
def get_current_time() -> str:
    """현재 시간을 반환합니다."""
    now = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분 %S초")
    print(f"  [도구] 현재 시간: {now}")
    return f"현재 시간은 {now}입니다."

tools = [search_tool, calculator, get_current_time]

# 3. LLM 에 도구를 바인딩 (LLM 이 tool_calls 를 낼 수 있게)
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = SystemMessage(content=(
    "당신은 도구를 사용할 수 있는 지능적인 AI 비서입니다. "
    "필요하면 도구를 호출하세요 — 계산은 calculator, 정보검색은 search_tool, 시간은 get_current_time."
))

# 4. agent 노드 — LLM 을 호출해 '답하거나 / 도구를 호출' 한다
def agent_node(state: MessagesState):
    response = llm_with_tools.invoke([SYSTEM_PROMPT] + state["messages"])
    return {"messages": [response]}   # MessagesState 의 add_messages 리듀서가 누적해줌

# 5. 순환 그래프 직접 구성 (★ 이 파일의 핵심)
memory = MemorySaver()
graph = StateGraph(MessagesState)

graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))      # 프리빌트 도구 실행 노드

graph.add_edge(START, "agent")                # 시작 → agent
graph.add_conditional_edges(                  # agent 후 분기:
    "agent",
    tools_condition,                          #   tool_calls 있으면 "tools", 없으면 END
    {"tools": "tools", END: END},             #   분기 목적지 명시 (도구로 / 끝으로)
)
graph.add_edge("tools", "agent")              # ★ 순환: 도구 결과를 agent 로 되먹임

app = graph.compile(checkpointer=memory)
print("순환 그래프 컴파일 완료 (START → agent ⇄ tools → END)")

# 6. 대화 루프 (스트리밍으로 agent/tools 스텝을 단계별 출력)
thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

print("\nReAct 에이전트 테스트 (exit 입력 시 종료):")
while True:
    user_input = input("\n질문을 입력하세요: ")
    if user_input.lower() == "exit":
        break
    
    if not user_input.strip():
        continue

    print("\n에이전트 실행 과정:")
    final_answer = ""
    for step in app.stream(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
        stream_mode="updates",
    ):
        # agent 노드 업데이트 — 생각 / 도구 호출 결정
        if "agent" in step:
            msg = step["agent"]["messages"][-1]
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    print(f"  → 도구 호출 결정: {tc['name']}({tc['args']})")
            else:
                final_answer = msg.content   # 도구 호출 없음 = 최종 답변
        # tools 노드 업데이트 — 도구 실행 결과
        if "tools" in step:
            for m in step["tools"]["messages"]:
                print(f"  ← 도구 결과({m.name}): {m.content[:60]}...")

    print(f"\nAI 최종 응답: {final_answer}")

print("\n설명:")
print("1. StateGraph 로 agent·tools 두 노드와 START/END 를 직접 연결했습니다.")
print("2. add_conditional_edges(agent, tools_condition): 도구가 더 필요하면 tools, 아니면 END.")
print("3. add_edge('tools','agent') 가 '순환' 을 만들어 ReAct 루프가 됩니다.")
print("4. 3번(분기, 비순환)과 달리 여기서는 그래프에 '사이클' 이 있다는 점이 핵심입니다.")
