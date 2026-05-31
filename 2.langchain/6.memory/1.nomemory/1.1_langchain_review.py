"""
LangChain 빠른 복습 — 메모리 학습 전 워밍업

이 폴더부터 시작하는 학생을 위한 최소 복습.
앞 폴더(2.prompts, 4.chaining)에서 다룬 핵심 빌딩 블록만 한 파일에 모았습니다.

여기서 알아둘 핵심:
  - ChatPromptTemplate / ChatOpenAI / LCEL 파이프(|)
  - MessagesPlaceholder ← 메모리의 모든 패턴이 이걸로 출발합니다.
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ============================================================
# (1) 가장 단순한 LCEL 체인 — prompt | llm | parser
# ============================================================
print("=" * 60)
print("(1) 기본 체인")
print("=" * 60)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 어시스턴트입니다."),
    ("user",   "{input}"),
])
chain = prompt | llm | StrOutputParser()
print(chain.invoke({"input": "안녕하세요!"}))


# ============================================================
# (2) MessagesPlaceholder — 메모리의 핵심 빌딩 블록
# ============================================================
# 외부에서 받은 메시지 리스트를 프롬프트 중간에 끼워 넣는 placeholder.
# "메모리" 라는 건 결국 "이전 대화 메시지를 history 자리에 끼워 LLM 에 보내는 것" 입니다.
# 이 폴더의 나머지 예제들은 이 history 를 어떻게 자동으로 만들/관리하는지가 전부입니다.
print("\n" + "=" * 60)
print("(2) MessagesPlaceholder — 메모리의 출발점")
print("=" * 60)

prompt_with_history = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 어시스턴트입니다."),
    MessagesPlaceholder("history"),        # ← 여기에 이전 대화 메시지들이 들어감
    ("user",   "{input}"),
])
chain2 = prompt_with_history | llm | StrOutputParser()

# 수동으로 history 를 구성해 끼워 넣어보기
fake_history = [
    HumanMessage(content="제 이름은 홍길동입니다."),
    AIMessage(content="네, 홍길동님 반갑습니다."),
]

answer = chain2.invoke({
    "history": fake_history,
    "input":   "제 이름이 뭐였죠?",
})
print(answer)
# → "홍길동" 을 정확히 기억합니다. fake_history 가 prompt 에 끼워졌기 때문.
