"""
[Task] 다국어 병렬 번역기

같은 문장을 한국어 / 일본어 / 프랑스어로 동시에 번역합니다.
RunnableParallel 로 3개 체인을 묶어 한 번의 invoke 로 처리합니다.

핵심 패턴
  - base_prompt.partial(language=...) 로 언어만 다른 변종 체인 만들기
  - RunnableParallel({"korean": ..., "japanese": ..., "french": ...}) 로 동시 실행
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

base_prompt = ChatPromptTemplate.from_messages([
    ("system", "Translate English to {language}. Only return the translation."),
    ("human", "{text}"),
])

# 언어만 다른 3개의 변종 체인
chain_ko = base_prompt.partial(language="Korean")   | llm | StrOutputParser()
chain_ja = base_prompt.partial(language="Japanese") | llm | StrOutputParser()
chain_fr = base_prompt.partial(language="French")   | llm | StrOutputParser()

# 동시에 실행
parallel_chain = RunnableParallel({
    "korean":   chain_ko,
    "japanese": chain_ja,
    "french":   chain_fr,
})

result = parallel_chain.invoke({"text": "Hello, nice to meet you."})

print("[KO]", result["korean"])
print("[JA]", result["japanese"])
print("[FR]", result["french"])
