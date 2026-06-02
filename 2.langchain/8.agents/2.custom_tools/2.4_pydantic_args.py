"""
Pydantic args_schema — 도구 인자를 Pydantic 모델로 더 강하게 명세.
이 예제: Field(description=...) / Literal enum / 검증으로 LLM 이 정확한 인자 넣도록 유도.

타입 힌트만으로도 충분하지만 (2.1), 복잡한 인자에는 Pydantic 이 좋다:
  - Field(description=...) 로 인자 하나하나에 가이드 추가
  - Literal["..."] 로 enum 강제 (LLM 이 다른 값 못 넣음)
  - Field(ge=1, le=20) 같은 검증 자동 적용
  - default 값, optional 필드 자연스럽게 표현

LLM 이 자주 헷갈리는 인자에 description 을 명시하면 정확도 ↑.
"""

import json
from typing import Literal
from pydantic import BaseModel, Field

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

load_dotenv()


# ─── Pydantic 모델로 인자 스키마 정의 ────────────────────────
class SendEmailInput(BaseModel):
    """이메일 전송 도구의 인자."""
    to: str = Field(description="수신자 이메일 주소 (반드시 유효한 이메일 형식)")
    subject: str = Field(description="이메일 제목 (50자 이내, 간결하게)")
    body: str = Field(description="이메일 본문 (반드시 한국어로 작성)")
    priority: Literal["low", "normal", "high"] = Field(
        default="normal",
        description="우선순위. urgent 한 경우에만 high 사용",
    )


@tool(args_schema=SendEmailInput)
def send_email(to: str, subject: str, body: str, priority: str = "normal") -> str:
    """사용자가 요청하면 이메일을 보낸다. 실제로 보내지 않고 결과만 출력."""
    print(f"[가짜 전송] to={to}, priority={priority}")
    print(f"  Subject: {subject}")
    print(f"  Body: {body}")
    return f"이메일이 {to} 에게 전송되었습니다 (priority={priority})."


# ─── 검색 도구 — 페이지네이션 인자 + 검증 ──────────────────
class SearchInput(BaseModel):
    """검색 도구의 인자."""
    query: str = Field(description="검색어")
    max_results: int = Field(default=5, ge=1, le=20, description="결과 개수 (1~20)")
    sort_by: Literal["relevance", "date"] = Field(
        default="relevance",
        description="정렬 기준. 최신 정보가 중요하면 'date'",
    )


@tool(args_schema=SearchInput)
def search(query: str, max_results: int = 5, sort_by: str = "relevance") -> list[str]:
    """주어진 쿼리로 가짜 검색을 수행한다."""
    return [f"결과 {i+1}: {query} (정렬={sort_by})" for i in range(max_results)]


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools([send_email, search])


# ─── 도구 명세 확인 ─────────────────────────────────────────
print("=" * 60)
print("send_email 의 args_schema (LLM 이 받는 JSON Schema)")
print("=" * 60)
print(json.dumps(send_email.args_schema.model_json_schema(), indent=2, ensure_ascii=False))


# ─── 호출 테스트 — LLM 이 description 보고 알아서 인자 채움 ──
print("\n" + "=" * 60)
print("호출 테스트")
print("=" * 60)

queries = [
    "alice@example.com 에게 '회의 일정 변경' 제목으로 이메일 보내줘. "
    "본문은 '회의가 내일 3시로 변경되었습니다.' 야. 긴급해.",        # → priority='high' 자동
    "파이썬 비동기 프로그래밍 최신 자료 5개만 날짜순으로 검색해줘.",   # → sort_by='date' 자동
]

for q in queries:
    print(f"\n[질문] {q}")
    response = llm_with_tools.invoke(q)
    for call in response.tool_calls:
        print(f"  → {call['name']}({call['args']})")

        # 실제 호출·결과를 보려면 아래 주석 해제 (@tool 은 .invoke(args) 로 실행)
        # name2tool = {t.name: t for t in [send_email, search]}
        # result = name2tool[call["name"]].invoke(call["args"])
        # print(f"     = {result}")

# 핵심:
#   - "긴급해" → priority="high"        (Literal enum 인식)
#   - "날짜순" → sort_by="date"          (Field description 인식)
#   - max_results=5  → ge=1/le=20 안에서 결정
