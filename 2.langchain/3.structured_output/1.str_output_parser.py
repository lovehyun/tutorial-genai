"""
기본 출력 파서 — StrOutputParser, CommaSeparatedListOutputParser

LLM 응답을 문자열 또는 리스트로 파싱하는 기본 패턴을 학습합니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# ===== 1. StrOutputParser =====
# AIMessage 객체에서 .content 문자열만 추출합니다.
print("=" * 50)
print("1. StrOutputParser 예시")
print("=" * 50)

prompt1 = ChatPromptTemplate.from_template(
    "{product}을(를) 만드는 회사의 이름을 하나 추천해주세요."
)

chain1 = prompt1 | llm | StrOutputParser()
result1 = chain1.invoke({"product": "웹게임"})
print(f"타입: {type(result1)}")  # <class 'str'>
print(f"결과: {result1}")

# ===== 2. CommaSeparatedListOutputParser =====
# 쉼표로 구분된 응답을 파이썬 리스트로 변환합니다.
print("\n" + "=" * 50)
print("2. CommaSeparatedListOutputParser 예시")
print("=" * 50)

list_parser = CommaSeparatedListOutputParser()

prompt2 = ChatPromptTemplate.from_template(
    "{topic}에 관련된 키워드를 5개만 쉼표로 구분하여 나열해주세요."
)

chain2 = prompt2 | llm | list_parser
result2 = chain2.invoke({"topic": "인공지능"})
print(f"타입: {type(result2)}")  # <class 'list'>
print(f"결과: {result2}")



# ===== 3. StrOutputParser를 활용한 체이닝 =====
# 문자열로 추출한 결과를 다음 프롬프트에 전달합니다.
print("\n" + "=" * 50)
print("3. 체이닝 예시: 회사명 → 캐치프레이즈")
print("=" * 50)

prompt_name = ChatPromptTemplate.from_template(
    "{product}을(를) 만드는 회사의 이름을 하나만 추천해주세요. 이름만 답하세요."
)
prompt_slogan = ChatPromptTemplate.from_template(
    "'{company_name}' 회사의 캐치프레이즈를 만들어주세요. 캐치프레이즈만 답하세요."
)

# StrOutputParser로 중간 결과를 깔끔한 문자열로 변환
chain3 = (
    prompt_name
    | llm
    | StrOutputParser()
    | (lambda name: {"company_name": name.strip()})
    | prompt_slogan
    | llm
    | StrOutputParser()
)

result3 = chain3.invoke({"product": "친환경 패키징"})
print(f"결과: {result3}")
