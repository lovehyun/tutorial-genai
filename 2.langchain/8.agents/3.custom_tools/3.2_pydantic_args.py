"""
Pydantic Args Schema — 도구 인자를 Pydantic 모델로 명시

타입 힌트만으로도 충분하지만 (2.1), 복잡한 인자에는 Pydantic 모델이 좋다:
  - 필드별 description 으로 LLM 에게 더 자세한 가이드
  - 검증(validation) 자동 적용
  - default 값, optional 필드, enum 등 풍부한 표현

특히 LLM 이 자주 헷갈리는 인자에 description 을 명시하면 정확도 ↑.
"""

from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
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


# ─── args_schema= 로 도구에 연결 ────────────────────────────
@tool(args_schema=SendEmailInput)
def send_email(to: str, subject: str, body: str, priority: str = "normal") -> str:
    """사용자가 요청하면 이메일을 보낸다. 실제로 보내지는 않고 결과만 출력."""
    print(f"[가짜 전송] to={to}, priority={priority}")
    print(f"  Subject: {subject}")
    print(f"  Body: {body}")
    return f"이메일이 {to} 에게 전송되었습니다 (priority={priority})."


# ─── 검색 도구 — 페이지네이션 인자 ──────────────────────────
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


# ─── LLM 에 바인딩 ──────────────────────────────────────────
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools([send_email, search])


# ─── 도구 명세 확인 ─────────────────────────────────────────
print("=" * 60)
print("Pydantic 으로 정의된 send_email 도구 스키마:")
print("=" * 60)
import json
print(json.dumps(send_email.args_schema.model_json_schema(), indent=2, ensure_ascii=False))


# ─── 도구 호출 테스트 ───────────────────────────────────────
print("\n" + "=" * 60)
print("도구 호출 테스트 — LLM 이 description 을 보고 알아서 인자 채움")
print("=" * 60)

queries = [
    "alice@example.com 에게 '회의 일정 변경' 제목으로 이메일 보내줘. 본문은 '회의가 내일 3시로 변경되었습니다.' 야. 긴급해.",
    "파이썬 비동기 프로그래밍 최신 자료 5개만 날짜 순으로 검색해줘.",
]

for q in queries:
    print(f"\n[질문] {q}")
    response = llm_with_tools.invoke(q)
    for call in response.tool_calls:
        print(f"  → {call['name']}({call['args']})")


# ─────────────────────────────────────────────────────────
# 핵심:
#   - Field(description=...) 가 LLM 에게 보이는 가이드라인
#   - Literal["..."] 로 enum 강제 (LLM 이 다른 값 못 넣음)
#   - Field(ge=1, le=20) 같은 검증도 작동
#   - "긴급해" → priority="high" 로 자동 변환되는 거 확인하세요
# ─────────────────────────────────────────────────────────
