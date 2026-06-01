"""
5_state_debugging.py - 전체 상태 및 스트리밍 디버깅

이 파일은 LangGraph에서 상태 변화를 추적하고 디버깅하는 방법을 보여줍니다.
복잡한 에이전트 시스템의 상태 변화를 분석하고 디버깅하는 기술을 배울 수 있습니다.

그래프 구조 (4.tools_cyclic_graph 와 동일한 ReAct 순환 그래프):
    ┌───────┐     ┌──────────┐   tool_calls 있음    ┌─────────┐
    │ START │──▶ │  agent   │ ──────────────────▶ │  tools  │
    └───────┘     │  (LLM)   │ ◀────────────────── │         │
                  └──────────┘                      └─────────┘
                      │ 최종 답변
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
from typing import Dict, List, Any, Optional, Union

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage, BaseMessage

from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

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
    
    # 실제로는 API 호출 등을 통해 검색을 수행하지만, 여기서는 간단한 구현
    search_results = {
        "인공지능": "인공지능(AI)은 인간의 학습, 추론, 지각, 문제 해결 능력 등을 컴퓨터로 구현하는 기술입니다.",
        "파이썬": "파이썬은 플랫폼 독립적이며 인터프리터식, 객체지향적, 동적 타이핑 대화형 언어입니다.",
        "랑그래프": "LangGraph는 LangChain의 일부로, 복잡한 에이전트 기반 AI 애플리케이션을 구축하기 위한 프레임워크입니다.",
    }
    
    # 검색어에 맞는 결과 반환, 없으면 기본 메시지 반환
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

# 도구 목록
tools = [search_tool, calculator]

# 3. 메모리 체크포인터 생성
memory = MemorySaver()

# 4. ReAct 에이전트 생성
react_agent = create_react_agent(
    llm,
    tools,
    prompt="""당신은 도구를 사용할 수 있는 지능적인 AI 비서입니다. 
사용자의 질문에 답하기 위해 필요한 경우 도구를 사용하세요.
계산이 필요한 경우 calculator 도구를 사용하세요.
정보 검색이 필요한 경우 search_tool 도구를 사용하세요.""",
    checkpointer=memory
)

print("ReAct 에이전트 생성 완료")

# 5. 디버깅을 위한 유틸리티 함수들
def print_state(state: Dict[str, Any], prefix: str = "", detail_level: int = 1):
    """상태 객체를 읽기 쉽게 출력"""
    print(f"{prefix} 상태:")
    
    for key, value in state.items():
        if key == "messages":
            messages = value
            print(f"{prefix} 메시지 ({len(messages)}개):")
            
            for i, msg in enumerate(messages):
                # 간략한 또는 상세한 메시지 출력
                if detail_level == 1:
                    # 간략한 출력
                    content = msg.content
                    content_preview = content[:50] + "..." if content and len(content) > 50 else content
                    print(f"{prefix}    {i+1}. {msg.type}: {content_preview}")
                else:
                    # 상세한 출력
                    print(f"{prefix}    {i+1}. {msg.type}:")
                    
                    if hasattr(msg, 'content') and msg.content:
                        print(f"{prefix}       내용: {msg.content}")
                    
                    # 도구 호출 정보
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        print(f"{prefix}       도구 호출:")
                        for tc in msg.tool_calls:
                            print(f"{prefix}         - {tc.get('name', 'unknown')}: {tc.get('args', {})}")
                    
                    # 도구 응답 정보
                    if hasattr(msg, 'name') and msg.name:
                        print(f"{prefix}       도구 이름: {msg.name}")
                    
                    # 추가 속성들
                    if hasattr(msg, 'additional_kwargs') and msg.additional_kwargs:
                        print(f"{prefix}       추가 속성: {msg.additional_kwargs}")
        else:
            print(f"{prefix}, {key}: {value}")

def log_step(step_num: int, step_data: Dict[str, Any], detail_level: int = 1):
    """단계별 데이터를 로깅"""
    print("\n" + "=" * 30)
    print(f"스텝 {step_num}")
    print("=" * 30)
    
    # 에이전트 단계
    if 'agent' in step_data:
        print("에이전트 상태 업데이트:")
        if 'messages' in step_data['agent']:
            messages = step_data['agent']['messages']
            if messages:
                last_message = messages[0]
                
                # 도구 호출 확인
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    tool_calls = last_message.tool_calls
                    print(f"  도구 호출 ({len(tool_calls)}개):")
                    for tc in tool_calls:
                        print(f"    - {tc['name']}({tc['args']})")
                else:
                    # 일반 응답
                    content = last_message.content
                    if content:
                        print(f"  생각: {content[:100]}..." if len(content) > 100 else f"  생각: {content}")
    
    # 도구 단계
    if 'tools' in step_data:
        print("도구 응답:")
        if 'messages' in step_data['tools']:
            messages = step_data['tools']['messages']
            if messages and hasattr(messages[0], 'content'):
                content = messages[0].content
                name = messages[0].name if hasattr(messages[0], 'name') else "unknown"
                print(f"  {name}: {content}")
    
    # 상세 디버깅 정보 출력
    if detail_level >= 2:
        print("\n전체 단계 데이터:")
        try:
            # 더 읽기 쉬운 형태로 출력
            for key, value in step_data.items():
                print(f" {key}:")
                if isinstance(value, dict) and 'messages' in value:
                    for i, msg in enumerate(value['messages']):
                        msg_type = msg.__class__.__name__
                        content = getattr(msg, 'content', '')
                        tool_calls = getattr(msg, 'tool_calls', [])
                        name = getattr(msg, 'name', '')
                        
                        print(f"    메시지 {i+1} ({msg_type}):")
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
        # BaseMessage 객체를 직렬화 가능한 형태로 변환
        def message_to_dict(msg):
            if isinstance(msg, BaseMessage):
                result = {
                    "type": msg.type,
                    "content": msg.content if hasattr(msg, 'content') else None
                }
                
                # 추가 속성들
                if hasattr(msg, 'name'):
                    result["name"] = msg.name
                if hasattr(msg, 'tool_calls'):
                    result["tool_calls"] = msg.tool_calls
                if hasattr(msg, 'additional_kwargs'):
                    result["additional_kwargs"] = msg.additional_kwargs
                    
                return result
            return str(msg)
        
        # 상태 데이터 변환
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

# 디버깅 레벨 설정
basic_debug = "1" in debug_level
detailed_debug = "2" in debug_level
file_logging = "3" in debug_level

# 대화 세션 ID 생성
thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

print("\n상태 디버깅 테스트 시작:")
print(f"대화 스레드 ID: {thread_id}")

# 대화 루프
while True:
    # 사용자 입력 받기
    user_input = input("\n질문을 입력하세요 (종료하려면 'exit' 입력): ")
    if user_input.lower() == 'exit':
        break
    
    if not user_input.strip():
        continue
    
    print(f"사용자 입력: {user_input}")
    
    # 디버깅 정보 수집
    debug_data = []
    step_counter = 0
    
    try:
        print("\n에이전트 실행 과정:")
        
        # 상태 스트리밍을 통한 디버깅
        for step in react_agent.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            stream_mode="values" if detailed_debug else "updates"
        ):
            step_counter += 1
            
            # 디버그 정보 저장
            debug_data.append(step)
            
            # 디버그 출력
            if basic_debug:
                log_step(step_counter, step, detail_level=1)
            
            if detailed_debug:
                print_state(step, prefix="  ", detail_level=2)
                
        # 최종 결과 가져오기
        final_result = react_agent.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config
        )
        
        print("\n최종 응답:")
        print(f"{final_result['messages'][-1].content}")
        
        # 파일 로깅
        if file_logging:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_file = f"debug_log_{timestamp}.json"
            save_debug_log(debug_file, final_result)
            
    except Exception as e:
        print(f"\n오류 발생: {str(e)}")

print("\n상태 디버깅 테스트 완료")
print("\n설명:")
print("1. stream 메서드를 사용해 에이전트 실행의 각 단계를 스트리밍했습니다.")
print("2. 'values' 모드는 전체 상태를, 'updates' 모드는 변경된 부분만 스트리밍합니다.")
print("3. 각 단계의 상태를 분석하여 에이전트의 생각 과정과 도구 사용을 확인했습니다.")
print("4. 디버깅 정보를 파일로 저장하여 후속 분석이 가능하게 했습니다.")

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
