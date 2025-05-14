"""
3_conditional_branching.py - 조건부 브랜칭 구현하기

이 파일은 LangGraph에서 조건부 브랜칭을 구현하는 방법을 보여줍니다.
사용자의 의도에 따라 다른 경로로 분기하여 특화된 응답을 생성할 수 있습니다.
"""

import os
import uuid
from dotenv import load_dotenv

from typing import TypedDict, List, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

print("=" * 50)
print("3단계: 조건부 브랜칭 구현하기")
print("=" * 50)

# 1. LLM 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 2. 메모리 체크포인터 생성
memory = MemorySaver()

# 3. 날씨와 뉴스 가상 데이터
class State(TypedDict):
    messages: List[AIMessage]
    topic: str

def get_weather():
    return "오늘 서울의 날씨는 맑고 기온은 22도입니다."

def get_news():
    return "최신 뉴스: 새로운 AI 기술 개발로 생산성이 향상되었습니다."

# 4. 라우팅 함수 (조건부 분기)
def topic_router(state: State, config: RunnableConfig) -> str:
    """사용자 의도에 따라 다른 경로로 라우팅하는 함수"""
    last_message = state["messages"][-1].content.lower()
    
    if "날씨" in last_message:
        print("라우터: '날씨' 의도 감지 -> weather 노드로 라우팅")
        return "weather"
    elif "뉴스" in last_message:
        print("라우터: '뉴스' 의도 감지 -> news 노드로 라우팅")
        return "news"
    else:
        print("라우터: 일반 대화 감지 -> chat 노드로 라우팅")
        return "chat"

# 5. 라우터 노드 함수 (no state update, placeholder)
def router_node(state: State, config: RunnableConfig) -> Dict[str, Any]:
    return {}

# 5. 날씨 노드 함수
def weather_node(state: State, config: RunnableConfig) -> Dict[str, Any]:
    """날씨 정보를 가져오는 함수"""
    print("날씨 노드 실행 중...")
    weather_info = get_weather()
    response = llm.invoke([
        SystemMessage(content="당신은 날씨 전문가입니다."),
        HumanMessage(content=f"다음 날씨 정보를 사용자에게 친절하게 설명해주세요: {weather_info}")
    ])
    print(f"날씨 응답 생성 완료: {response.content[:50]}...")
    return {"messages": state["messages"] + [response], "topic": "weather"}

# 6. 뉴스 노드 함수
def news_node(state: State, config: RunnableConfig) -> Dict[str, Any]:
    """뉴스 정보를 가져오는 함수"""
    print("뉴스 노드 실행 중...")
    news_info = get_news()
    response = llm.invoke([
        SystemMessage(content="당신은 뉴스 전문가입니다."),
        HumanMessage(content=f"다음 뉴스를 사용자에게 친절하게 설명해주세요: {news_info}")
    ])
    print(f"뉴스 응답 생성 완료: {response.content[:50]}...")
    return {"messages": state["messages"] + [response], "topic": "news"}

# 7. 일반 채팅 노드 함수
def chat_node(state: State, config: RunnableConfig) -> Dict[str, Any]:
    """일반 대화를 처리하는 함수"""
    print("채팅 노드 실행 중...")
    messages = state["messages"]
    system_message = SystemMessage(content="당신은 친절한 AI 비서입니다.")
    all_messages = [system_message] + messages
    response = llm.invoke(all_messages)
    print(f"채팅 응답 생성 완료: {response.content[:50]}...")
    return {"messages": state["messages"] + [response], "topic": "chat"}

# 8. 조건부 그래프 생성
graph = StateGraph(State)
graph.add_node("router", router_node)
graph.add_node("weather", weather_node)
graph.add_node("news", news_node)
graph.add_node("chat", chat_node)

# 시작 노드와 라우터 연결
graph.add_edge(START, "router")

# 조건부 엣지 추가
graph.add_conditional_edges(
    "router",
    topic_router,
    path_map = {
        "weather": "weather", 
        "news": "news", 
        "chat": "chat"
    }
)

# 각 노드에서 종료 노드로 연결
# graph.add_edge("weather", END)
# graph.add_edge("news", END)
# graph.add_edge("chat", END)
for node in ["weather", "news", "chat"]:
    graph.add_edge(node, END)

# 9. 그래프 컴파일
app = graph.compile(checkpointer=memory)
print("조건부 브랜칭 그래프 컴파일 완료")

# 10. 각 조건 테스트
print("\n조건부 브랜칭 테스트:")
thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

# 12. 대화 루프
while True:
    user_input = input("\n질문을 입력하세요 (종료하려면 'exit' 입력): ")
    if user_input.lower() == 'exit':
        break
    
    if not user_input.strip():
        continue
        
    print(f"사용자 입력: {user_input}")
    
    # 그래프 실행
    result = app.invoke(
        {"messages": [HumanMessage(content=user_input)], "topic": ""},
        config=config
    )
    
    print(f"AI 응답: {result['messages'][-1].content}")
    print(f"선택된 토픽: {result['topic']}")
    
    # 라우팅 경로 설명
    topic = result['topic']
    if topic == "weather":
        print("실행 경로: START -> router -> weather -> END")
    elif topic == "news":
        print("실행 경로: START -> router -> news -> END")
    else:
        print("실행 경로: START -> router -> chat -> END")

print("\n조건부 브랜칭 테스트 완료")
print("\n설명:")
print("1. 사용자 의도(날씨, 뉴스, 일반 대화)에 따라 다른 경로로 분기하는 라우터 노드를 구현했습니다.")
print("2. 각 경로마다 특화된 시스템 프롬프트와 처리 로직을 가진 노드를 정의했습니다.")
print("3. add_conditional_edges를 사용해 라우터 함수의 반환값에 따라 다른 경로로 이동하도록 설정했습니다.")
print("4. 모든 경로는 최종적으로 END 노드로 연결되어 그래프 실행이 완료됩니다.")
print("\n다음 단계에서는 도구를 사용하는 ReAct 에이전트와 순환 그래프를 구현해 보겠습니다.")
