"""
JsonOutputParser — JSON dict 로 받기 (스키마 없음, 가벼움)

PydanticOutputParser(7.2) 가 스키마를 강제한다면, JsonOutputParser 는
"그냥 JSON 으로 답해줘" 정도의 가벼운 강제. 결과는 일반 dict.

언제 쓰나?
  - 스키마까지 강제할 필요는 없고 "JSON 형태로만 받으면 OK" 일 때
  - 필드가 동적으로 변할 가능성이 있을 때 (스키마 고정 어려움)
  - Pydantic 의존성 추가하기 싫을 때
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 1. 파서 — 인자 없음 (스키마 없음)
parser = JsonOutputParser()

# 2. format_instructions 를 prompt 에 끼워넣어 "JSON 으로 답해" 지시
prompt = ChatPromptTemplate.from_messages([
    ("system", "Always respond with valid JSON only. No prose, no markdown."),
    ("user",   "{question}\n\n{format_instructions}"),
]).partial(format_instructions=parser.get_format_instructions())

chain = prompt | llm | parser

# 3. 실행
print("=" * 50)
print("JsonOutputParser — 스키마 없는 JSON dict")
print("=" * 50)

result = chain.invoke({"question": "남미 국가 3개의 이름과 수도를 알려줘."})
print(f"타입: {type(result).__name__}")    # dict
print(f"결과: {result}")

# 4. 한 번 더 — 필드가 동적으로 다를 수 있는 경우
print("\n" + "=" * 50)
print("동적 필드 — 입력에 따라 응답 구조가 달라질 수 있음")
print("=" * 50)

result2 = chain.invoke({"question": "오늘 점심으로 김치찌개를 먹은 후기를 JSON 으로 표현해줘."})
print(f"결과: {result2}")


# ============================================================
# [참고] 세 가지 구조화 출력 방식 비교 (이 폴더 안에서)
# ============================================================
# 7.1 StrOutputParser              → 그냥 문자열 (스키마 X)
# 7.2 PydanticOutputParser         → Pydantic 모델 (스키마 강제, prompt injection 방식)
# 7.3 with_structured_output()     → LLM native 구조화 출력 (function calling 기반, 가장 강력)
# 7.4 JsonOutputParser (이 파일)    → JSON dict (스키마 없음, 가벼움)
#
# 권장:
#   - 스키마 명확하고 타입 안전성 중요   → 7.3 with_structured_output()
#   - 어떤 LLM 에도 동작 + 스키마 강제   → 7.2 PydanticOutputParser
#   - 빠른 프로토타입 / 동적 필드        → 7.4 JsonOutputParser (이 파일)
#   - 자유로운 자연어 답변               → 7.1 StrOutputParser
