from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import SystemMessage
import tiktoken

load_dotenv()

# ===== 설정 상수 =====
MODEL_NAME = "gpt-4o-mini"
MAX_HISTORY_TOKENS = 1000      # ≤ 요약 임계치
KEEP_LAST_TURNS = 1            # 요약 후 유지할 최근 턴 수(1턴=Human+AI 2개 메시지)

# ===== LLM & tokenizer =====
llm = ChatOpenAI(model=MODEL_NAME, temperature=0)

# tiktoken이 모델명을 모를 수 있어 fallback
try:
    token_encoder = tiktoken.encoding_for_model(MODEL_NAME)
except KeyError:
    token_encoder = tiktoken.get_encoding("cl100k_base")

# 사용자별 대화 저장소
user_histories: dict[str, InMemoryChatMessageHistory] = {}

def count_tokens_of_history(history: InMemoryChatMessageHistory) -> int:
    # 단순 합산(역할 토큰/시스템 프롬프트는 제외). 여유 버퍼를 두고 임계치를 잡는 게 안전.
    text = " ".join(m.content for m in history.messages)
    return len(token_encoder.encode(text))

def summarize_if_needed(session_id: str, history: InMemoryChatMessageHistory):
    num_tokens = count_tokens_of_history(history)
    if num_tokens <= MAX_HISTORY_TOKENS:
        return

    # 전체 대화 요약 프롬프트 (핵심 사실 포함 유도)
    dialogue_text = "\n".join(f"{m.type.upper()}: {m.content}" for m in history.messages)
    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", "다음 대화를 핵심 사실(이름, 나이, 취미, 목표 등)을 잃지 않게 간결히 요약해줘."),
        ("human", "{dialogue}")
    ])
    summary = (summary_prompt | llm | StrOutputParser()).invoke({"dialogue": dialogue_text})

    # 최근 턴 보존(1턴 = Human+AI 2개 메시지)
    tail = history.messages[-2*KEEP_LAST_TURNS:] if KEEP_LAST_TURNS > 0 else []
    history.clear()
    # 요약은 시스템 메시지로 넣어야 모델이 '컨텍스트'로 인식
    history.add_message(SystemMessage(content=f"(요약) {summary}"))
    for m in tail:
        history.add_message(m)

# 프롬프트/체인
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 친절한 요약 AI야. history에 시스템 요약이 포함될 수 있으며, 그 사실을 신뢰해 답하라."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])
chain = prompt | llm | StrOutputParser()

# RunnableWithMessageHistory
def get_session_history(arg):
    # LangChain 버전에 따라 문자열/딕셔너리 두 경우 모두 대응
    if isinstance(arg, str):
        session_id = arg
    else:
        session_id = (arg.get("configurable", {}) or {}).get("session_id", "default-user")
    return user_histories.setdefault(session_id, InMemoryChatMessageHistory())

chat_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

def chat(message: str, session_id: str = "default-user"):
    print(f"Q: {message}")
    history = user_histories.setdefault(session_id, InMemoryChatMessageHistory())
    # 호출 '직전'에 요약해서 프롬프트 길이를 관리
    summarize_if_needed(session_id, history)
    response = chat_chain.invoke({"input": message}, config={"configurable": {"session_id": session_id}})
    print(f"A: {response}")
    return response 


# 테스트
chat("안녕, 나는 김철수야.")
chat("내가 누구라고 했는지 기억해?")
chat("내 취미는 등산과 독서야.")
chat("마지막에 말한 두 가지 취미가 뭐였지?")
chat("강아지도 키워. 이름은 뽀삐야.")
chat("내 직업은 개발자야.")
chat("지금까지 말한 걸 요약해줄래?")
