# pip install langchain-ollama pydantic
#
# Ollama + LangChain 6: 구조화 출력.
# with_structured_output(Pydantic) 로 응답을 정해진 스키마 객체로 바로 받는다.
# ※ JSON/스키마를 지원하는 모델 필요(mistral · llama3.1 · qwen2.5 등). 최신 langchain-ollama 권장.

from langchain_ollama import ChatOllama
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int
    city: str

llm = ChatOllama(model="mistral", temperature=0)

structured = llm.with_structured_output(Person)

person = structured.invoke("다음에서 정보 추출: 김철수, 30세, 서울 거주.")
print(person)
print("이름:", person.name, "/ 나이:", person.age, "/ 도시:", person.city)
