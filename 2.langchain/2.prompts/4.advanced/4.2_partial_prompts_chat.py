from dotenv import load_dotenv
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# Partial Prompts: 프롬프트의 일부 변수를 "미리" 채워두는 패턴.
#   - 같은 시스템 프롬프트를 여러 곳에서 재사용할 때
#   - 일부 값은 호출 시점이 아니라 시작 시점에 정해질 때 유용

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ─── 방법 (1) partial_variables 인자로 초기 지정 ──────────────
base_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a {role} assistant. Respond in {language}."),
        ("user",   "{question}"),
    ],
    partial_variables={"role": "Korean cooking", "language": "Korean"},
)

# role/language 는 이미 채워졌으니 호출 시엔 question 만 넘기면 된다
chain1 = base_prompt | llm | StrOutputParser()
print("== (1) 클래스 인자 partial_variables ==")
print(chain1.invoke({"question": "김치찌개 끓이는 법 한 줄로 알려줘."}))


# ─── 방법 (2) .partial() 메서드로 나중에 채우기 ─────────────
template = ChatPromptTemplate.from_messages([
    ("system", "You are a {role} assistant. Respond in {language}."),
    ("user",   "{question}"),
])

cooking_ko = template.partial(role="Korean cooking", language="Korean")
travel_en  = template.partial(role="travel",         language="English")

chain2 = cooking_ko | llm | StrOutputParser()
chain3 = travel_en  | llm | StrOutputParser()

print("\n== (2) .partial() 로 분기 ==")
print("[요리/한국어]", chain2.invoke({"question": "김치찌개 재료 5개만."}))
print("[여행/영어]",   chain3.invoke({"question": "Top 3 places to visit in Seoul (one line each)."}))


# ─── 방법 (3) callable 도 partial 가능 — 호출 시점마다 동적 값 ───
# 예: 현재 시각을 system 프롬프트에 자동으로 박아주기
def now_iso():
    return datetime.now().isoformat(timespec="seconds")

time_prompt = ChatPromptTemplate.from_messages([
    ("system", "Current server time: {now}. You are a helpful assistant."),
    ("user",   "{question}"),
]).partial(now=now_iso)     # 함수 자체를 넘기면, 호출 시마다 자동으로 실행됨

chain4 = time_prompt | llm | StrOutputParser()
print("\n== (3) callable partial — 호출마다 동적 ==")
print(chain4.invoke({"question": "Just print: I was asked at the timestamp above."}))
