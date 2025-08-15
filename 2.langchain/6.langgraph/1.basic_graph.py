"""
1_basic_graph.py - LangGraph 기본 그래프 구조

이 파일은 LangGraph의 가장 기본적인 그래프 구조를 생성하고 실행하는 방법을 보여줍니다.
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from langgraph.graph import StateGraph, START, END, MessagesState

load_dotenv()

print("=" * 50)
print("1단계: 기본 그래프 구조 이해하기")
print("=" * 50)

# 1. LLM 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 2. 간단한 상태 그래프 생성
graph = StateGraph(state_schema=MessagesState)

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

# 4. 노드와 엣지 추가
graph.add_node("model", call_model)
graph.add_edge(START, "model")
graph.add_edge("model", END)

# 5. 그래프 컴파일
app = graph.compile()
print("그래프 컴파일 완료")

# 6. 그래프 실행
print("\n기본 그래프 실행 테스트:")

# 사용자 입력 받기 (선택 사항)
user_input = input("\n질문을 입력하세요 (기본값: '안녕하세요, 오늘 날씨 어때요?'): ")
if not user_input.strip():
    user_input = "안녕하세요, 오늘 날씨 어때요?"

result = app.invoke({"messages": [HumanMessage(content=user_input)]})

# 7. 결과 출력
print("\n결과:")
for i, message in enumerate(result["messages"]):
    print(f"메시지 {i}: {message.type} - {message.content}")

print("\n기본 그래프 실행 완료")
print("\n설명:")
print("1. MessagesState를 사용해 메시지 목록을 상태로 관리하는 그래프를 생성했습니다.")
print("2. call_model 함수는 상태에서 메시지를 가져와 LLM에 전달하고 응답을 생성합니다.")
print("3. START -> 'model' -> END로 이어지는 단순한 그래프 구조를 정의했습니다.")
print("4. invoke 메서드로 그래프를 실행하고 결과를 얻었습니다.")
print("\n다음 단계에서는 메모리와 체크포인팅을 추가하여 대화 기록을 저장하고 불러오는 방법을 살펴보겠습니다.")
