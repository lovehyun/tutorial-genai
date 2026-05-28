"""
메모리 없는 챗봇 — 매 호출이 독립적

LLM 호출 자체는 stateless 입니다.
history 를 직접 넣어주지 않으면 이전 대화를 전혀 기억하지 못합니다.

여기서 "왜 메모리가 필요한가" 를 체감한 뒤, 다음 폴더부터 해결책을 배웁니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 어시스턴트입니다."),
    ("user",   "{input}"),
])
chain = prompt | llm | StrOutputParser()


def chat(message):
    print(f"\nQ: {message}")
    print(f"A: {chain.invoke({'input': message})}")


# 같은 챗봇처럼 보이지만, 매 호출은 완전히 독립적이라 이전 발화를 기억 못함
chat("제 이름은 홍길동입니다.")
chat("제 이름이 뭐였죠?")          # ← 모른다고 답할 것
chat("저는 등산을 좋아해요.")
chat("제가 무슨 취미라고 했죠?")    # ← 모른다고 답할 것
