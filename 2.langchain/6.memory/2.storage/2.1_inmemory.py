"""
InMemoryChatMessageHistory — 프로세스 메모리에 대화 저장

가장 단순한 메모리 저장소.
직접 history 객체를 다루어 메시지를 누적·삽입하는 흐름을 익힙니다.

자주 나오는 질문 → 어디서 해결되는지
  Q. 얼마나 저장 가능? 무제한?
    → 자료구조 차원에선 사실상 무제한(RAM 이 허용하는 만큼) 입니다. 단, 프로세스가
      종료되면 모두 사라집니다(영속성 X — 파일/DB 가 필요하면 2.2 / 2.3).
  Q. 메시지가 계속 쌓이면 토큰 한도 넘지 않나?
    → 넘습니다. 모델 컨텍스트 윈도우 초과 시 호출이 실패합니다.
      → 해결: 4.compression/ (trim_messages / 자동 요약).
  Q. 여러 사용자/대화 분리는?
    → 이 파일은 단일 history 하나만 씁니다. 여러 사용자 동시 사용 불가.
      → 해결: 3.sessions/ 에서 RunnableWithMessageHistory + session_id 별 분리.

즉 2.storage 는 "저장소 자체" 만 보는 단계이고, 위 문제들은 3 / 4 폴더에서 단계적으로 풀어갑니다.
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 어시스턴트입니다."),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
])
chain = prompt | llm | StrOutputParser()

# ← 이 한 줄만 storage 종류별로 달라집니다 (2.2 / 2.3 비교)
history = InMemoryChatMessageHistory()


def chat(message):
    print(f"\nQ: {message}")
    answer = chain.invoke({
        "input":   message,
        "history": history.messages,    # 현재까지 누적된 메시지를 끼워 넣음
        # "history": history.messages[-10:]   # 최근 10개만 전달
    })
    print(f"A: {answer}")
    # 호출 후 메시지 누적
    history.add_user_message(message)
    history.add_ai_message(answer)


chat("제 이름은 홍길동입니다.")
chat("저는 등산을 좋아해요.")
chat("제 이름과 취미를 다시 말해줄래요?")
