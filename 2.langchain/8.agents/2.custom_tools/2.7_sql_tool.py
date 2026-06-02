"""
text-to-SQL 도구 — DB 스키마를 주고 자연어 질문 → SQL 생성 → 실제 실행 → 결과.
이 예제: SQLite 에 users/products/orders 테이블을 만들고, run_sql 도구로
        LLM 이 작성한 SQL 을 진짜 실행해 결과를 돌려준다 (create_agent 자동 루프).

흐름:
  질문 → (LLM 이 스키마 보고 SQL 작성) → run_sql 도구가 SQLite 에서 실행 → 결과 → LLM 이 한국어로 답

핵심: SQL 은 "도구의 인자"로 LLM 이 만들고, 실행은 run_sql(@tool) 이 한다.
      앞 예제들과 달리 bind_tools 가 아니라 create_agent 라서 실행→결과까지 자동.

  ※ 표준 라이브러리(sqlite3)만 사용 — 추가 설치 불필요
"""

import sqlite3
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent

load_dotenv()


# ─── 1) SQLite 인메모리 DB + 샘플 데이터 ──────────────────────
# check_same_thread=False: create_agent 의 도구 실행이 별도 스레드일 수 있어 필요
conn = sqlite3.connect(":memory:", check_same_thread=False)
conn.executescript(
    """
    CREATE TABLE users    (id INTEGER PRIMARY KEY, name TEXT, city TEXT, age INTEGER);
    CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER, category TEXT);
    CREATE TABLE orders   (id INTEGER PRIMARY KEY, user_id INTEGER, product_id INTEGER,
                           qty INTEGER, ordered_at TEXT);

    INSERT INTO users (id, name, city, age) VALUES
      (1, '홍길동', '서울', 30), (2, '김철수', '부산', 25),
      (3, '이영희', '서울', 28), (4, '박민수', '대구', 35);

    INSERT INTO products (id, name, price, category) VALUES
      (1, '노트북', 1500000, '전자'), (2, '마우스', 30000, '전자'),
      (3, '책상', 200000, '가구'),   (4, '의자', 150000, '가구');

    INSERT INTO orders (id, user_id, product_id, qty, ordered_at) VALUES
      (1, 1, 1, 1, '2026-05-01'), (2, 1, 2, 2, '2026-05-02'),
      (3, 2, 3, 1, '2026-05-03'), (4, 3, 1, 1, '2026-05-04'),
      (5, 3, 4, 4, '2026-05-05'), (6, 4, 2, 3, '2026-05-06');
    """
)
conn.commit()


# ─── 2) LLM 에게 줄 스키마 설명 ───────────────────────────────
SCHEMA = """\
users(id, name, city, age)
products(id, name, price, category)              -- price 단위: 원
orders(id, user_id, product_id, qty, ordered_at) -- user_id→users.id, product_id→products.id
"""


# ─── 3) SQL 실행 도구 (읽기 전용) ─────────────────────────────
@tool
def run_sql(query: str) -> str:
    """SQLite DB 에 SELECT SQL 을 실행하고 결과 행을 반환한다. SELECT 만 허용."""
    q = query.strip().rstrip(";")
    if not q.lower().startswith("select"):
        return "오류: 안전을 위해 SELECT 쿼리만 실행합니다."
    try:
        cur = conn.execute(q)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        if not rows:
            return "결과 없음"
        out = [" | ".join(cols)]
        out += [" | ".join(str(v) for v in row) for row in rows]
        return "\n".join(out)
    except Exception as e:
        return f"SQL 오류: {e}"


# ─── 4) 에이전트 — 스키마를 시스템 프롬프트로, 도구는 run_sql 하나 ──
SYSTEM = f"""당신은 SQLite 데이터 분석가입니다. 아래 스키마만 사용해 질문에 답하세요.

[스키마]
{SCHEMA}
규칙:
- 답하려면 반드시 run_sql 도구로 SELECT 쿼리를 실행해 실제 데이터를 확인하세요 (추측 금지).
- SQLite 문법 사용. JOIN / GROUP BY / 집계함수 모두 가능.
- 마지막엔 결과를 한국어로 간결히 설명하세요.
"""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, [run_sql], system_prompt=SYSTEM)


# ─── 5) 다양한 질문 → SQL 생성·실행·답변 ──────────────────────
questions = [
    "서울에 사는 사용자는 몇 명이야?",
    "가장 비싼 상품 3개를 가격 높은 순으로 알려줘.",
    "홍길동이 주문한 상품 이름과 수량을 보여줘.",
    "카테고리별 총 주문 수량을 구해줘.",
]

for q in questions:
    print("\n" + "=" * 60)
    print(f"[질문] {q}")
    result = agent.invoke({"messages": [("user", q)]})

    # LLM 이 실제로 만들어 실행한 SQL 도 함께 표시
    for m in result["messages"]:
        for call in getattr(m, "tool_calls", None) or []:
            print(f"  [실행한 SQL] {call['args'].get('query')}")
    print(f"[답변] {result['messages'][-1].content}")
