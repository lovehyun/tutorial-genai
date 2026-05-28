"""
[Task] 자연어 → SQL 생성기 (스키마 grounding)

DB 스키마를 프롬프트에 함께 넣어주면 LLM 이:
  - 존재하지 않는 컬럼을 만들지 않음
  - JOIN 관계를 추론할 수 있음
  - hallucination 이 크게 줄어듦

스키마 없이 시키면 어떤 일이 일어나는지도 같이 비교해 보세요(주석 처리된 부분 참고).
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# DB 스키마 — 프롬프트에 함께 넣어줌
schema = """
Table: users
- id (INTEGER)
- name (TEXT)
- email (TEXT)
- signup_date (DATE)

Table: orders
- id (INTEGER)
- user_id (INTEGER)
- product_name (TEXT)
- price (INTEGER)
- created_at (DATE)
"""

chat_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert SQL generator.\n"
     "Only generate valid SQL.\n"
     "Use only the provided schema.\n"
     "Do not explain anything — return SQL only."),
    ("human",
     "Database Schema:\n{schema}\n\n"
     "User Request:\n{query}"),
])

chain = chat_prompt | llm | StrOutputParser()

# 한국어 질문 5개 — 난이도 순서로 구성
questions = [
    "2023년 1월 1일 이후 가입한 사용자의 이름과 이메일을 조회해줘.",
    "주문 금액이 50000원 이상인 주문 목록을 조회해줘.",
    "사용자별 총 주문 금액을 계산해줘.",
    "가장 최근에 주문한 상품 5개를 보여줘.",
    "한 번도 주문하지 않은 사용자의 이름을 조회해줘.",
]

for idx, question in enumerate(questions, start=1):
    print("=" * 60)
    print(f"[질문 {idx}] {question}")
    sql = chain.invoke({"schema": schema, "query": question})
    print("\n[생성된 SQL]")
    print(sql)
    print()
