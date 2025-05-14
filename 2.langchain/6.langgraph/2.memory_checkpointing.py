"""
2_memory_checkpointing.py - 메모리 및 체크포인팅 추가하기

이 파일은 LangGraph에서 체크포인팅을 통해 대화 기록을 저장하고 불러오는 방법을 보여줍니다.
체크포인팅을 사용하면 대화 세션을 지속적으로 유지하고 이전 대화 내용을 기억할 수 있습니다.
"""

import os
import uuid
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

print("=" * 50)
print("2단계: 메모리 및 체크포인팅 추가하기")
print("=" * 50)

# 1. LLM 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 2. 메모리 체크포인터 생성
memory = MemorySaver()

# 3. 모델 호출 함수 정의
def call_model(state: MessagesState):
    """LLM에 메시지를 전달하고 응답을 생성하는 함수"""
    messages = state["messages"]
    system_message = SystemMessage(content="당신은 친절한 AI 비서입니다.")
    all_messages = [system_message] + messages
    
    print(f"모델 호출 함수 실행 중... 메시지 수: {len(messages)}")
    response = llm.invoke(all_messages)
    print(f"모델 응답 생성 완료: {response.content[:50]}...")
    return {"messages": response}

# 4. 그래프 생성 및 노드/엣지 추가
graph = StateGraph(state_schema=MessagesState)
graph.add_node("model", call_model)
graph.add_edge(START, "model")
graph.add_edge("model", END)

# 5. 체크포인터를 사용해 그래프 컴파일
app = graph.compile(checkpointer=memory)
print("체크포인터를 사용한 그래프 컴파일 완료")

# 6. 스레드 ID 정의 (사용자 세션마다 고유한 ID)
thread_id = str(uuid.uuid4())
print(f"대화 스레드 ID 생성: {thread_id}")
config = {"configurable": {"thread_id": thread_id}}

# 7. 대화 멀티턴 테스트
print("\n지속적인 대화 테스트:")

# 첫 번째 대화
print("\n첫 번째 메시지 전송:")
first_input = input("첫 번째 메시지를 입력하세요 (기본값: '안녕하세요, 제 이름은 김철수입니다.'): ")
if not first_input.strip():
    first_input = "안녕하세요, 제 이름은 김철수입니다."

result1 = app.invoke(
    {"messages": [HumanMessage(content=first_input)]},
    config=config
)
print(f"AI 응답: {result1['messages'][-1].content}")

# 두 번째 대화 (이전 대화 기억 테스트)
print("\n두 번째 메시지 전송 (이전 대화 기억 테스트):")
second_input = input("두 번째 메시지를 입력하세요 (기본값: '제 이름이 뭐였죠?'): ")
if not second_input.strip():
    second_input = "제 이름이 뭐였죠?"

result2 = app.invoke(
    {"messages": [HumanMessage(content=second_input)]},
    config=config
)
print(f"AI 응답: {result2['messages'][-1].content}")

# 세 번째 대화
print("\n세 번째 메시지 전송:")
third_input = input("세 번째 메시지를 입력하세요 (기본값: '제가 무슨 일을 하는지 알려드릴게요. 저는 프로그래머입니다.'): ")
if not third_input.strip():
    third_input = "제가 무슨 일을 하는지 알려드릴게요. 저는 프로그래머입니다."

result3 = app.invoke(
    {"messages": [HumanMessage(content=third_input)]},
    config=config
)
print(f"AI 응답: {result3['messages'][-1].content}")

# 네 번째 대화 (직업 기억 테스트)
print("\n네 번째 메시지 전송 (직업 기억 테스트):")
fourth_input = input("네 번째 메시지를 입력하세요 (기본값: '제 직업이 뭐였죠?'): ")
if not fourth_input.strip():
    fourth_input = "제 직업이 뭐였죠?"

result4 = app.invoke(
    {"messages": [HumanMessage(content=fourth_input)]},
    config=config
)
print(f"AI 응답: {result4['messages'][-1].content}")

# 전체 대화 내용 확인 (옵션)
print("\n전체 대화 내용:")
all_messages = result4["messages"]
for i, message in enumerate(all_messages):
    print(f"{message.type}: {message.content}")

print("\n메모리 체크포인팅 테스트 완료")
print("\n설명:")
print("1. MemorySaver를 사용해 대화 기록을 메모리에 저장하는 체크포인터를 생성했습니다.")
print("2. 그래프 컴파일 시 체크포인터를 연결하여 상태 지속성을 부여했습니다.")
print("3. 고유한 thread_id를 사용해 대화 세션을 식별하고 관리했습니다.")
print("4. 이전 대화 내용(이름, 직업 등)을 기억하고 참조할 수 있음을 확인했습니다.")
print("\n다음 단계에서는 사용자 의도에 따라 다른 경로로 분기하는 조건부 브랜칭을 구현해 보겠습니다.")


# 새로운 대화 시작 (선택 사항)
print("\n새로운 대화 세션 시작:")
new_thread = input("새로운 대화 세션을 시작하시겠습니까? (y/n, 기본값: n): ")
if new_thread.lower() == 'y':
    new_thread_id = str(uuid.uuid4())
    print(f"새 대화 스레드 ID 생성: {new_thread_id}")
    config = {"configurable": {"thread_id": new_thread_id}}
    
    new_input = input("새 메시지를 입력하세요: ")
    if new_input.strip():
        new_result = app.invoke(
            {"messages": [HumanMessage(content=new_input)]},
            config=config
        )
        print(f"AI 응답: {new_result['messages'][-1].content}")
        print("\n이 응답에서는 이전 대화의 내용이 기억되지 않습니다. (새로운 thread_id 사용)")
