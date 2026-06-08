"""
5_state_debugging.py - 전체 상태 및 스트리밍 디버깅

이 파일은 LangGraph에서 상태 변화를 추적하고 디버깅하는 방법을 보여줍니다.
복잡한 에이전트 시스템의 상태 변화를 분석하고 디버깅하는 기술을 배울 수 있습니다.

그래프 구조 (4.tools_cyclic_graph 와 동일한 ReAct 순환 그래프 — StateGraph 로 직접 구성):
    ┌───────┐     ┌──────────┐   tool_calls 있음    ┌─────────┐
    │ START │──▶ │  agent   │ ──────────────────▶ │  tools  │
    └───────┘     │  (LLM)   │ ◀────────────────── │ ToolNode│
                  └──────────┘                      └─────────┘
                      │ 최종 답변 (tools_condition → END)
                      ▼
                   ┌─────┐
                   │ END │
                   └─────┘
    여기선 stream(stream_mode="updates"/"values") 로 각 노드 전이(상태 변화)를 관찰·디버깅
"""

import uuid
import json
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.tools import tool

from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

print("=" * 50)
print("5단계: 전체 상태 및 스트리밍 디버깅")
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
    print(f"검색 도구 실행: '{query}' 검색 중...")
    search_results = {
        "인공지능": "인공지능(AI)은 인간의 학습, 추론, 지각, 문제 해결 능력 등을 컴퓨터로 구현하는 기술입니다.",
        "파이썬": "파이썬은 플랫폼 독립적이며 인터프리터식, 객체지향적, 동적 타이핑 대화형 언어입니다.",
        "랑그래프": "LangGraph는 LangChain의 일부로, 복잡한 에이전트 기반 AI 애플리케이션을 구축하기 위한 프레임워크입니다.",
    }
    for key, value in search_results.items():
        if key in query.lower():
            print(f"검색 결과 찾음: {value[:50]}...")
            return value
    print("검색 결과를 찾을 수 없습니다.")
    return f"'{query}'에 대한 정보를 찾을 수 없습니다."

@tool
def calculator(expression: str) -> str:
    """간단한 수학 계산을 수행합니다."""
    print(f"계산기 도구 실행: '{expression}' 계산 중...")
    try:
        result = eval(expression)
        print(f"계산 결과: {result}")
        return f"계산 결과: {result}"
    except Exception as e:
        print(f"계산 오류: {str(e)}")
        return f"계산 중 오류가 발생했습니다: {str(e)}"

tools = [search_tool, calculator]

# 3. 메모리 체크포인터 생성
memory = MemorySaver()

# 4. ReAct 순환 그래프 직접 구성 (4단계와 동일 구조 — 디버깅 대상)
llm_with_tools = llm.bind_tools(tools)
SYSTEM_PROMPT = SystemMessage(content=(
    "당신은 도구를 사용할 수 있는 지능적인 AI 비서입니다. "
    "계산은 calculator, 정보 검색은 search_tool 을 사용하세요."
))

def agent_node(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([SYSTEM_PROMPT] + state["messages"])]}

graph = StateGraph(MessagesState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent", tools_condition,
    {"tools": "tools", END: END},   # tool_calls 있으면 tools 노드로, 없으면 END 로 (분기 명시)
)
graph.add_edge("tools", "agent")                        # 순환 (ReAct 루프)
app = graph.compile(checkpointer=memory)

print("ReAct 순환 그래프 컴파일 완료 (START → agent ⇄ tools → END)")

# 5. 디버깅을 위한 유틸리티 함수들
def print_state(state: Dict[str, Any], prefix: str = "", detail_level: int = 1):
    """상태 객체를 읽기 쉽게 출력"""
    print(f"{prefix} 상태:")
    for key, value in state.items():
        if key == "messages":
            messages = value
            print(f"{prefix} 메시지 ({len(messages)}개):")
            for i, msg in enumerate(messages):
                if detail_level == 1:
                    content = msg.content
                    content_preview = content[:50] + "..." if content and len(content) > 50 else content
                    print(f"{prefix}    {i+1}. {msg.type}: {content_preview}")
                else:
                    print(f"{prefix}    {i+1}. {msg.type}:")
                    if hasattr(msg, 'content') and msg.content:
                        print(f"{prefix}       내용: {msg.content}")
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        print(f"{prefix}       도구 호출:")
                        for tc in msg.tool_calls:
                            print(f"{prefix}         - {tc.get('name', 'unknown')}: {tc.get('args', {})}")
                    if hasattr(msg, 'name') and msg.name:
                        print(f"{prefix}       도구 이름: {msg.name}")
                    if hasattr(msg, 'additional_kwargs') and msg.additional_kwargs:
                        print(f"{prefix}       추가 속성: {msg.additional_kwargs}")
        else:
            print(f"{prefix}, {key}: {value}")

def log_step(step_num: int, step_data: Dict[str, Any], detail_level: int = 1):
    """단계별 데이터를 로깅 (수동 그래프의 노드 이름: 'agent' / 'tools')"""
    print("\n" + "=" * 30)
    print(f"스텝 {step_num}")
    print("=" * 30)

    # 에이전트 단계
    if 'agent' in step_data:
        print("에이전트 상태 업데이트:")
        messages = step_data['agent'].get('messages', [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                print(f"  도구 호출 ({len(last_message.tool_calls)}개):")
                for tc in last_message.tool_calls:
                    print(f"    - {tc['name']}({tc['args']})")
            elif last_message.content:
                content = last_message.content
                print(f"  생각: {content[:100]}..." if len(content) > 100 else f"  생각: {content}")

    # 도구 단계
    if 'tools' in step_data:
        print("도구 응답:")
        messages = step_data['tools'].get('messages', [])
        if messages and hasattr(messages[0], 'content'):
            name = messages[0].name if hasattr(messages[0], 'name') else "unknown"
            print(f"  {name}: {messages[0].content}")

    # 상세 디버깅 정보 출력
    if detail_level >= 2:
        print("\n전체 단계 데이터:")
        try:
            for key, value in step_data.items():
                print(f" {key}:")
                if isinstance(value, dict) and 'messages' in value:
                    for i, msg in enumerate(value['messages']):
                        content = getattr(msg, 'content', '')
                        tool_calls = getattr(msg, 'tool_calls', [])
                        name = getattr(msg, 'name', '')
                        print(f"    메시지 {i+1} ({msg.__class__.__name__}):")
                        if content:
                            print(f"     내용: {content[:100]}..." if len(content) > 100 else f"     내용: {content}")
                        if tool_calls:
                            print(f"     도구 호출: {tool_calls}")
                        if name:
                            print(f"     이름: {name}")
                else:
                    print(f"    {value}")
        except Exception as e:
            print(f"데이터 출력 오류: {e}")

def save_debug_log(file_name: str, data: Dict[str, Any]):
    """디버그 로그를 파일로 저장"""
    try:
        def message_to_dict(msg):
            if isinstance(msg, BaseMessage):
                result = {"type": msg.type, "content": getattr(msg, 'content', None)}
                if hasattr(msg, 'name'):
                    result["name"] = msg.name
                if hasattr(msg, 'tool_calls'):
                    result["tool_calls"] = msg.tool_calls
                if hasattr(msg, 'additional_kwargs'):
                    result["additional_kwargs"] = msg.additional_kwargs
                return result
            return str(msg)

        serializable_data = {}
        for key, value in data.items():
            if key == "messages":
                serializable_data[key] = [message_to_dict(msg) for msg in value]
            else:
                serializable_data[key] = value

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=2)
        print(f"디버그 로그가 '{file_name}'에 저장되었습니다.")
    except Exception as e:
        print(f"로그 저장 오류: {e}")

# 디버깅 옵션
print("\n디버깅 옵션:")
print("1. 기본 디버깅: 각 단계의 주요 정보만 표시")
print("2. 상세 디버깅: 모든 상태 정보와 메시지 세부 정보 표시")
print("3. 파일 로깅: 상태 변화를 JSON 파일로 저장")

debug_level = input("디버깅 레벨을 선택하세요 (1, 2, 3 중 하나 또는 조합, 예: '12', 기본값: 1): ")
if not debug_level:
    debug_level = "1"

basic_debug = "1" in debug_level
detailed_debug = "2" in debug_level
file_logging = "3" in debug_level

thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

print("\n상태 디버깅 테스트 시작:")
print(f"대화 스레드 ID: {thread_id}")

# 대화 루프
while True:
    user_input = input("\n질문을 입력하세요 (종료하려면 'exit' 입력): ")
    if user_input.lower() == 'exit':
        break
    if not user_input.strip():
        continue

    print(f"사용자 입력: {user_input}")
    step_counter = 0

    try:
        print("\n에이전트 실행 과정:")
        # 상태 스트리밍을 통한 디버깅
        #   updates 모드: 노드별 '변경분'(노드 이름 키) / values 모드: '전체 상태'
        for step in app.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            stream_mode="values" if detailed_debug else "updates",
        ):
            step_counter += 1
            if basic_debug and not detailed_debug:
                log_step(step_counter, step, detail_level=1)
            if detailed_debug:
                print_state(step, prefix="  ", detail_level=2)

        # 최종 상태 (재실행 없이 체크포인트에서 조회)
        final_state = app.get_state(config).values
        print("\n최종 응답:")
        print(f"{final_state['messages'][-1].content}")

        if file_logging:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_file = f"debug_log_{timestamp}.json"
            save_debug_log(debug_file, final_state)

    except Exception as e:
        print(f"\n오류 발생: {str(e)}")

print("\n상태 디버깅 테스트 완료")
print("\n설명:")
print("1. stream 메서드로 에이전트 실행의 각 단계(상태 변화)를 스트리밍했습니다.")
print("2. 'values' 모드는 전체 상태를, 'updates' 모드는 변경된 부분(노드별)만 스트리밍합니다.")
print("3. 각 단계의 상태를 분석해 에이전트의 생각 과정과 도구 사용을 확인했습니다.")
print("4. app.get_state(config) 로 재실행 없이 최종 상태를 조회/저장했습니다.")

print("\n🎓 LangGraph 단계별 디버깅 학습 완료!")
print("""
LangGraph의 핵심 기능들을 단계별로 살펴보았습니다:
1. 기본 그래프 구조 이해하기 (1_basic_graph.py)
2. 메모리 및 체크포인팅 추가하기 (2_memory_checkpointing.py)
3. 조건부 브랜칭 구현하기 (3_conditional_branching.py)
4. 도구 사용과 순환 그래프 (4_tools_cyclic_graph.py)
5. 전체 상태 및 스트리밍 디버깅 (5_state_debugging.py)

이제 LangGraph를 사용하여 자신만의 복잡한 에이전트 시스템을 구현할 준비가 되었습니다!
""")
