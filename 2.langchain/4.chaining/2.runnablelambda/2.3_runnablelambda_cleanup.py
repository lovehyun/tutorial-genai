"""
RunnableLambda — 임의의 파이썬 함수를 체인 단계로 끼우는 Runnable.
이 예제: LLM 출력의 따옴표·"prefix:" 같은 잡음을 cleanup 함수로 후처리합니다.

LLM이 답할 때 종종 따옴표를 두르거나 "회사명:" 같은 prefix를 붙입니다.
RunnableLambda 안에 정리 함수를 넣어서 노이즈를 제거합니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")


def cleanup(text: str) -> str:
    """LLM 출력에 흔히 끼는 잡음 제거"""
    s = text.strip()                # 앞뒤 공백
    s = s.strip('"').strip("'")     # 양쪽 따옴표
    if ":" in s:                    # "회사명: ..." 같은 prefix 제거
        s = s.split(":", 1)[-1].strip()
    return s


prompt = ChatPromptTemplate.from_template(
    "{product}을(를) 만드는 회사 이름을 1개만 추천해줘."
)

chain_raw   = prompt | llm | StrOutputParser()
chain_clean = chain_raw | RunnableLambda(cleanup)

raw   = chain_raw.invoke({"product": "웹게임"})
clean = chain_clean.invoke({"product": "웹게임"})

# 원본은 따옴표/prefix가 섞여있을 수 있고, 정리된 결과는 깔끔한 회사명만 남는다.
print(f"[원본]   {raw!r}")
print(f"[정리]   {clean!r}")
