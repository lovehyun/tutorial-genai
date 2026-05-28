"""
ConversationBufferMemory — 가장 원형의 옛 메모리 (모든 대화 누적, 압축 없음)

블로그·튜토리얼에서 가장 흔히 보이는 옛 패턴.
참고용으로만 보세요. 현행 코드는 `RunnableWithMessageHistory` + `InMemoryChatMessageHistory`
조합을 쓰면 됩니다 (메인 폴더 1.~5.).

옛 메모리 발전사
  1. ConversationBufferMemory          — 이 파일. 모든 대화 누적.
  2. ConversationBufferWindowMemory    — 최근 k 턴만 (1.buffer_window_memory.py)
  3. ConversationSummaryBufferMemory   — 토큰 초과 시 자동 요약 (2.summary_buffer_memory.py)

  → 현행 대체:
     - ConversationBufferMemory       → InMemoryChatMessageHistory (2.storage/2.1)
     - ConversationBufferWindowMemory → 메시지 슬라이스 (3.sessions/3.3)
     - ConversationSummaryBufferMemory → trim_messages / 수동 요약 (4.compression)
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory   # ← deprecated (참고용)

load_dotenv()
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 옛 메모리 — return_messages=True 로 두면 message 객체 리스트가 옴
memory = ConversationBufferMemory(memory_key="history", return_messages=True)

prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 친절한 어시스턴트야."),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}"),
])
chain = prompt | llm | StrOutputParser()

# 옛 방식: 매번 memory.load_memory_variables() / memory.save_context() 를 수동 호출
conversation = [
    "안녕, 나는 홍길동이야.",
    "내 나이는 35살이야.",
    "내 취미는 등산이야.",
    "내가 누구고 몇 살이고 무슨 취미를 좋아한다고 했지?",
]

for q in conversation:
    history_vars = memory.load_memory_variables({})
    answer = chain.invoke({**history_vars, "input": q})

    print(f"\nHuman: {q}")
    print(f"AI: {answer}")

    memory.save_context({"input": q}, {"output": answer})

print(f"\n총 누적 메시지: {len(memory.chat_memory.messages)} 개 (윈도우 없음 → 무한 누적)")
