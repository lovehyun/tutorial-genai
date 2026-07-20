from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


# LLM 생성
llm = ChatOpenAI(model="gpt-4o-mini")


# 1) 커스텀 출력 구조 정의 (Pydantic)

class Fruit(BaseModel):
    이름: str = Field(description="과일 이름")
    설명: str = Field(description="과일에 대한 간단한 설명")

# Parser 생성
parser = PydanticOutputParser(pydantic_object=Fruit)

print(parser.get_format_instructions())


# {
#   "properties": {
#     "이름": {
#       "title": "이름",
#       "description": "과일 이름",
#       "type": "string"
#     },
#     "설명": {
#       "title": "설명",
#       "description": "과일에 대한 간단한 설명",
#       "type": "string"
#     }
#   },
#   ...
# }

prompt = (
    "한국을 대표하는 과일 5개를 알려줘.\n"
    + parser.get_format_instructions()
)

response = llm.invoke(prompt)
result = parser.invoke(response)
print(result)


# 2) 리스트를 원하면

from typing import List

class Fruit(BaseModel):
    이름: str = Field(description="과일 이름")
    설명: str = Field(description="과일 설명")

class Fruits(BaseModel):
    과일목록: List[Fruit]

parser = PydanticOutputParser(pydantic_object=Fruits)

prompt = (
    "한국을 대표하는 과일 5개를 알려줘.\n"
    + parser.get_format_instructions()
)

response = llm.invoke(prompt)
result = parser.invoke(response)
print(result)


# Fruits(
#     과일목록=[
#         Fruit(이름='사과', 설명='한국에서 널리 재배되는 대표 과일'),
#         Fruit(이름='배', 설명='명절 선물로 많이 사용됨'),
#         ...
#     ]
# )
