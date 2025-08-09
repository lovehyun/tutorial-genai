# pip install langgraph langchain-openai tiktoken python-dotenv

from dotenv import load_dotenv
import uuid
import tiktoken

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver

# =========================
# 0) 설정
# =========================
load_dotenv()

MODEL_NAME = "gpt-4o-mini"   # 또는 "gpt-3.5-turbo"
TEMPERATURE = 0.0
MAX_HISTORY_TOKENS = 1000    # 임계치(요약 트리거)
KEEP_LAST_TURNS = 3          # 요약 후 보낼 최근 턴(1턴=Human+AI 2개)
FALLBACK_LAST_MSGS = 6       # 요약이 없을 때 임시로 보낼 메시지 수

# tiktoken 준비 (모델명 인식 실패 시 기본 인코딩)
try:
    enc = tiktoken.encoding_for_model(MODEL_NAME)
except KeyError:
    enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(enc.encode(text))

# =========================
# 1) LLM & 체크포인터
# =========================
llm = ChatOpenAI(model=MODEL_NAME, temperature=TEMPERATURE)
checkpointer = MemorySaver()

# =========================
# 2) 그래프 상태
# =========================
graph = StateGraph(state_schema=MessagesState)

# =========================
# 3) 요약/윈도우 유틸
# =========================
def build_summary(messages: list[BaseMessage]) -> str:
    dialogue_text = "\n".join(f"{m.type.upper()}: {m.content}" for m in messages)
    prompt = [
        SystemMessage(content="다음 대화를 핵심 사실(이름, 나이, 취미, 목표 등)을 잃지 않게 간결히 요약해줘."),
        HumanMessage(content=dialogue_text),
    ]
    return llm.invoke(prompt).content

def pick_messages_for_model(state_messages: list[BaseMessage]) -> list[BaseMessage]:
    # 최근 요약(SystemMessage 중 "(요약)"로 시작하는 가장 최신)
    # (A) 최신 요약 찾기
    latest_summary = None
    for m in reversed(state_messages):
        if isinstance(m, SystemMessage) and m.content.startswith("(요약)"):
            latest_summary = m
            break

    # (B) 요약이 아직 없다면 → 임시로 최근 N개 메시지를 넉넉히 전송
    if latest_summary is None:
        # system 제외하고 최근 N개만(사실 system 포함해도 무방)
        recent = [m for m in state_messages if m.type in ("human", "ai")][-FALLBACK_LAST_MSGS:]
        base_system = SystemMessage(
            content="너는 친절한 대화형 AI야. history에는 시스템 요약이 포함될 수 있으며, 그 사실을 신뢰해 답하라."
        )
        return [base_system] + recent

    # (C) 요약이 있으면 → 요약 + 최근 턴(휴먼/AI 2*KEEP_LAST_TURNS)
    tail = []
    human_ai_count = 0
    for m in reversed(state_messages):
        if m.type in ("human", "ai"):
            tail.append(m)
            human_ai_count += 1
            if human_ai_count >= 2 * KEEP_LAST_TURNS:
                break
    tail.reverse()

    base_system = SystemMessage(
        content="너는 친절한 대화형 AI야. history에는 시스템 요약이 포함될 수 있으며, 그 사실을 신뢰해 답하라."
    )
    return [base_system, latest_summary] + tail

# =========================
# 4) 노드: 요약 여부 판단 -> 필요 시 요약 메시지 append
# =========================
def maybe_summarize_node(state: MessagesState):
    flat_text = " ".join(m.content for m in state["messages"])
    if count_tokens(flat_text) <= MAX_HISTORY_TOKENS:
        return {}  # 아무 것도 추가하지 않음

    summary = build_summary(state["messages"])
    # 리스트로 반환해야 리듀서(add_messages)가 정상 append
    return {"messages": [SystemMessage(content=f"(요약) {summary}")]}

# =========================
# 5) 노드: 모델 호출
# =========================
def call_model_node(state: MessagesState):
    to_send = pick_messages_for_model(state["messages"])
    ai_msg = llm.invoke(to_send)
    # 반드시 리스트로 감싸서 반환
    return {"messages": [ai_msg]}

# =========================
# 6) 그래프 구성
# =========================
graph.add_node("maybe_summarize", maybe_summarize_node)
graph.add_node("model", call_model_node)

graph.add_edge(START, "maybe_summarize")
graph.add_edge("maybe_summarize", "model")
graph.add_edge("model", END)

app = graph.compile(checkpointer=checkpointer)

# =========================
# 7) 데모
# =========================
if __name__ == "__main__":
    conversation = [
        "안녕, 나는 김철수라고 해.",
        "내가 누구라고 했는지 기억해?",
        "내 취미는 등산과 독서야.",
        "그 취미 기억하고 있어?",
        "내가 마지막에 말한 두 가지 취미는 뭐였지?",
        "강아지를 키우고 있어. 이름은 뽀삐야.",
        "내 직업은 개발자야.",
        "지금까지 말한 걸 요약해줄래?",
    ]

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    for q in conversation:
        # 같은 thread_id로 호출 → 이전 state가 자동 복원 + 이번 입력이 append
        result = app.invoke({"messages": [HumanMessage(content=q)]}, config=config)
        print(f"Human: {q}")
        print(f"AI   : {result['messages'][-1].content}\n")

    # 이후에도 같은 thread_id로 호출하면 계속 이어짐:
    # result = app.invoke({"messages": [HumanMessage(content="내 이름 다시 말해봐.")]}, config=config)
