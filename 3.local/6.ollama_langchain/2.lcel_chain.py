# pip install langchain-ollama
#
# Ollama + LangChain 2: LCEL 체인.
# prompt | llm | parser 를 | 로 연결한다. StrOutputParser 가 AIMessage 에서 문자열만 뽑는다.

from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOllama(model="mistral", temperature=0.7)

prompt = PromptTemplate.from_template("다음 주제로 블로그 글의 개요 5가지를 만들어줘: {topic}")

chain = prompt | llm | StrOutputParser()

print(chain.invoke({"topic": "로컬 LLM 활용"}))


# for chunk in chain.stream({"topic": "로컬 LLM 활용"}):
#     print(chunk, end="", flush=True)
