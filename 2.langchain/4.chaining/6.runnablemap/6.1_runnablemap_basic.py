"""
RunnableMap — RunnableParallel 의 별칭. 입력 dict 를 다음 체인 형태로 재구성하는 Runnable.
이 예제: 호출 쪽 {"question": ...} 을 체인이 기대하는 {"input": ...} 으로 키 이름을 매핑합니다.

체인은 {"input": ...} 을 기대하는데, 호출하는 쪽은 {"question": ...} 으로 넘긴다면?
중간에 RunnableMap 으로 키 이름을 갈아끼울 수 있습니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableMap

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

# 체인은 {input} 자리표시자만 받음
prompt = ChatPromptTemplate.from_template("질문에 한 줄로 답해: {input}")
answer_chain = prompt | llm | StrOutputParser()

# 호출하는 쪽은 {"question": ...} 형태로 넘긴다고 가정
# → RunnableMap 으로 키 이름을 question → input 으로 변환
chain = RunnableMap({"input": lambda x: x["question"]}) | answer_chain

print(chain.invoke({"question": "파이썬이 뭐야?"}))
