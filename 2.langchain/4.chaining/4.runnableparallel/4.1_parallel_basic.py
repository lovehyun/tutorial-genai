"""
RunnableParallel — 같은 입력을 여러 체인에 동시 실행하고 결과를 dict 로 모으는 Runnable.
이 예제: 같은 영어 문장을 한국어/일본어/프랑스어 번역 체인 3개에 병렬 분배합니다.

같은 입력을 여러 체인에 동시에 흘려보내고, 결과를 dict 로 받습니다.
서로 독립적인 작업을 묶을 때 유용합니다(번역, 요약, 키워드 추출 동시 등).
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

# 같은 입력 {"text": ...} 을 받는 3개의 독립 체인
ko_chain = ChatPromptTemplate.from_template("다음을 한국어로 번역해줘: {text}") | llm | StrOutputParser()
ja_chain = ChatPromptTemplate.from_template("다음을 일본어로 번역해줘: {text}") | llm | StrOutputParser()
fr_chain = ChatPromptTemplate.from_template("다음을 프랑스어로 번역해줘: {text}") | llm | StrOutputParser()

parallel = RunnableParallel({
    "ko": ko_chain,
    "ja": ja_chain,
    "fr": fr_chain,
})

result = parallel.invoke({"text": "Hello, nice to meet you."})
print("[한국어]", result["ko"])
print("[일본어]", result["ja"])
print("[프랑스어]", result["fr"])
