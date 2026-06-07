# pip install langchain-ollama
#
# Ollama + LangChain 4: system/human 메시지 + ChatPromptTemplate.
# 역할(system)과 사용자 입력(human)을 분리하고 변수로 채운다.

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOllama(model="mistral")

prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 {role} 전문가다. 초보자도 알기 쉽게 설명한다."),
    ("human", "{concept} 를 설명해줘."),
])

chain = prompt | llm | StrOutputParser()

print(chain.invoke({"role": "물리학", "concept": "엔트로피"}))
