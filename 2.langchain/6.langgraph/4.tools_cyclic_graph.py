"""
4_tools_cyclic_graph.py - 도구 사용과 순환 그래프

이 파일은 LangGraph에서 도구를 사용하는 ReAct 에이전트와 순환 그래프를 구현하는 방법을 보여줍니다.
도구 사용과 순환 처리를 통해 더 복잡하고 지능적인 에이전트를 구현할 수 있습니다.
"""

import uuid
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

print("=" * 50)
print("4단계: 도구 사용과 순환 그래프")
print("=" * 50)

# 1. LLM 초기화 (ReAct 에이전트에는 GPT-4를 추천하지만, 비용 절감을 위해 GPT-3.5 사용)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

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
        "날씨": "특정 지역의 날씨 정보는 기상청 웹사이트에서 확인할 수 있습니다.",
        "랑그래프": "LangGraph는 LangChain의 일부로, 복잡한 에이전트 기반 AI 애플리케이션을 구축하기 위한 프레임워크입니다.",
        "에이전트": "AI 에이전트는 환경을 인식하고, 자율적으로 의사결정을 내려 목표를 달성하는 소프트웨어 시스템입니다."
    }
    
    # 검색어에 맞는 결과 반환, 없으면 기본 메시지 반환
    for key, value in search_results.items():
        if key in query.lower():
            print(f"검색 결과 찾음: {value[:50]}...")
            return value
            
    print("검색 결과를 찾을 수 없습니다.")
    return f"'{query}'에 대한 정보를 찾을 수 없습니다. 다른 검색어를 시도해보세요."

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

@tool
def get_current_time() -> str:
    """현재 시간을 반환합니다."""
    current_time = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분 %S초")
    print(f"현재 시간: {current_time}")
    return f"현재 시간은 {current_time}입니다."

# 3. 메모리 체크포인터 생성
memory = MemorySaver()

# 4. 도구 목록
tools = [search_tool, calculator, get_current_time]

# 5. ReAct 에이전트 생성
react_agent = create_react_agent(
    llm,
    tools,
    prompt="""당신은 도구를 사용할 수 있는 지능적인 AI 비서입니다. 
사용자의 질문에 답하기 위해 필요한 경우 도구를 사용하세요.
계산이 필요한 경우 calculator 도구를 사용하세요.
정보 검색이 필요한 경우 search_tool 도구를 사용하세요.
현재 시간을 알아야 할 때는 get_current_time 도구를 사용하세요.""",
    checkpointer=memory
)

print("ReAct 에이전트 생성 완료")
print("\nReAct 에이전트 동작 방식:")
print("1. 사용자 입력을 받아 에이전트가 처리합니다.")
print("2. 에이전트는 도구 사용이 필요한지 결정합니다.")
print("3. 도구 사용이 필요하면 도구를 호출하고 결과를 받습니다.")
print("4. 결과를 바탕으로 다시 추론하여 추가 도구 사용이나 최종 응답을 생성합니다.")
print("5. 이 과정은 순환적으로 반복되며, 최종 응답이 생성될 때까지 계속됩니다.")

# 6. 스트리밍 또는 단일 응답 모드 선택
print("\nReAct 에이전트 테스트:")
print("1. 단일 응답 모드: 최종 결과만 보여줍니다.")
print("2. 스트리밍 모드: 에이전트의 생각 과정과 도구 사용을 단계별로 보여줍니다.")

mode = input("모드를 선택하세요 (1 또는 2, 기본값: 2): ")
if not mode or mode not in ["1", "2"]:
    mode = "2"

# 7. 대화 세션 ID 생성
thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

# 8. 대화 루프
while True:
    # 사용자 입력 받기
    user_input = input("\n질문을 입력하세요 (종료하려면 'exit' 입력): ")
    if user_input.lower() == 'exit':
        break
    
    if not user_input.strip():
        continue
    
    print(f"사용자 입력: {user_input}")
    
    if mode == "1":
        # 단일 응답 모드
        result = react_agent.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config
        )
        print(f"\nAI 최종 응답: {result['messages'][-1].content}")
        
    else:
        # 스트리밍 모드
        print("\n에이전트 실행 과정:")
        steps = 0
        
        try:
            for step in react_agent.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="updates"
            ):
                steps += 1
                print(f"\n--- 스텝 {steps} ---")
                
                # 에이전트 생각 단계
                if 'agent' in step:
                    messages = step['agent'].get('messages', [])
                    if messages:
                        content = messages[0].content
                        if content:
                            print(f"에이전트 생각: {content[:100]}..." if len(content) > 100 else f"에이전트 생각: {content}")
                        
                        # 도구 호출 확인
                        if hasattr(messages[0], 'tool_calls') and messages[0].tool_calls:
                            tool_calls = messages[0].tool_calls
                            for tool_call in tool_calls:
                                print(f"도구 호출: {tool_call['name']}({tool_call['args']})")
                
                # 도구 응답 단계
                if 'tools' in step:
                    messages = step['tools'].get('messages', [])
                    if messages and hasattr(messages[0], 'content'):
                        content = messages[0].content
                        name = messages[0].name if hasattr(messages[0], 'name') else "unknown"
                        print(f"도구 응답 ({name}): {content}")
            
            # 최종 결과 가져오기
            final_result = react_agent.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )
            print(f"\n최종 응답: {final_result['messages'][-1].content}")
            
        except Exception as e:
            print(f"\n오류 발생: {str(e)}")

print("\nReAct 에이전트 테스트 완료")
print("\n설명:")
print("1. create_react_agent 함수를 사용해 도구를 활용할 수 있는 ReAct 에이전트를 생성했습니다.")
print("2. 에이전트는 사용자 질문에 답하기 위해 필요한 경우 도구를 호출합니다.")
print("3. 도구 호출 결과를 바탕으로 추가 도구 호출이나 최종 응답을 생성하는 순환 과정을 거칩니다.")
print("4. 스트리밍 모드에서는 에이전트의 생각 과정과 도구 사용을 단계별로 확인할 수 있습니다.")
print("\n다음 단계에서는 전체 상태 변화를 추적하고 디버깅하는 방법을 살펴보겠습니다.")
