# 필요한 라이브러리 설치
# pip install langgraph langchain-openai

# 항목	            RunnableWithMessageHistory	    LangGraph
# 구조	            단일 체인 기반	                 노드-엣지 기반 그래프
# 분기 처리	        어려움 (조건문 직접 구현)	      노드 연결로 간단
# 멀티모델/병렬	    복잡	                         자연스럽게 지원
# 메모리	        session_id 기반	                 thread_id 기반 + 자동 저장/복원
# 복잡도	        간단한 대화형 앱에 적합	          복잡한 워크플로우에 적합

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
import uuid

# 1. 환경 변수 로드
load_dotenv()

# 2. LLM 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 3. 메모리 저장소 생성
memory = MemorySaver()

# 4. 그래프 상태 정의
graph = StateGraph(state_schema=MessagesState)

# 5. 모델 호출 함수 정의
def call_model(state: MessagesState):
    system_prompt = "당신은 친절한, 대화형 AI 비서입니다. 사용자의 질문에 정확하게 답변하세요."
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": response}

# 6. 노드 및 엣지 추가
graph.add_node("model", call_model)
graph.add_edge("__start__", "model")
graph.add_edge("model", "__end__")

# 7. 그래프 컴파일
app = graph.compile(checkpointer=memory)

# 8. 대화 진행
conversation = [
    "안녕, 나는 김철수라고 해.",
    "내가 누구라고 했는지 기억해?",
    "내 취미는 등산과 독서야.",
    "그 취미 기억하고 있어?",
    "내가 마지막에 말한 두 가지 취미는 뭐였지?",
    "강아지를 키우고 있어. 이름은 뽀삐야.",
    "내 직업은 개발자야.",
    "지금까지 말한 걸 요약해줄래?"
]

# 고유 대화 ID 생성
thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

for message in conversation:
    result = app.invoke(
        {"messages": [HumanMessage(content=message)]},
        config=config
    )
    print(f"Human: {message}")
    print(f"AI: {result['messages'][-1].content}\n")

# 9. 메모리 내용 확인 (선택 사항)
# 메모리는 자동으로 관리되며 thread_id로 접근 가능
