"""
세션 + 슬라이딩 윈도우 — 최근 N 턴만 유지

대화가 길어지면 토큰 비용이 늘어납니다.
가장 단순한 압축 방법: "메시지 개수" 기준으로 오래된 걸 잘라냄.

  ※ 토큰 기준의 정밀한 컷은 4.compression 의 trim_messages 가 더 적합합니다.
     여기서는 RunnableWithMessageHistory + 단순 윈도우 조합만.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 어시스턴트입니다."),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
])
chain = prompt | llm | StrOutputParser()

MAX_TURNS = 2   # 1 턴 = Human + AI 2 개 메시지
sessions: dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in sessions:
        sessions[session_id] = InMemoryChatMessageHistory()
    hist = sessions[session_id]
    # 최근 N 턴만 남기기
    if len(hist.messages) > MAX_TURNS * 2:
        hist.messages = hist.messages[-MAX_TURNS * 2:]
    return hist


chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)


def chat(message, session_id="default"):
    print(f"\nQ: {message}")
    answer = chain_with_memory.invoke(
        {"input": message},
        config={"configurable": {"session_id": session_id}},
    )
    print(f"A: {answer}")


# 5 턴 진행 — MAX_TURNS=2 라 앞 부분은 잊혀짐
chat("제 이름은 홍길동입니다.")
chat("저는 등산을 좋아해요.")
chat("최근에 설악산에 다녀왔어요.")
chat("내일 한라산도 가려고 해요.")
chat("제 이름이 뭐였죠?")             # ← 윈도우 밖이라 못 알아맞춤

print(f"\n저장된 메시지: {len(sessions['default'].messages)} 개 (윈도우 적용 결과)")
