"""
RunnablePassthrough — 입력을 그대로 흘려보내며 .assign() 으로 새 키를 덧붙이는 Runnable.
이 예제: 질문(question) 을 보존한 채 답변/모델명/타임스탬프를 추가해 API 응답 형태 dict 를 만듭니다.

QA·챗봇 API 의 표준 응답 패턴.
클라이언트가 "내가 뭘 물어봤지?" 를 다시 확인할 수 있도록 질문도 함께 돌려주고,
LLM 답변과 운영 메타데이터(모델, 시각) 를 같은 dict 에 묶어서 반환합니다.
"""

import json
import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

MODEL_NAME = "gpt-4o-mini"
llm = ChatOpenAI(model=MODEL_NAME)

answer_chain = ChatPromptTemplate.from_template("{question}") | llm | StrOutputParser()

# question 은 그대로 흘리며 answer / model / timestamp 키를 차례로 부착
api_chain = (
    RunnablePassthrough.assign(answer=answer_chain)
    | RunnablePassthrough.assign(
        model=lambda _: MODEL_NAME,
        timestamp=lambda _: datetime.datetime.now().isoformat(timespec="seconds"),
    )
)

result = api_chain.invoke({"question": "파이썬에서 리스트와 튜플의 차이는?"})

# 실제 REST API 가 돌려줄 법한 응답 모양
print(json.dumps(result, ensure_ascii=False, indent=2))
