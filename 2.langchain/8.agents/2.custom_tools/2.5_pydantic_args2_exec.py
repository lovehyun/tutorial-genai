"""
도구를 쓸지 / 직접 답할지 LLM 이 고르고, 고른 도구를 실제로 실행까지.
이 예제: 2.4 의 Pydantic 도구(send_email, search) 에 "적합한 도구가 없는 질문" 을 섞고,
        (1) 도구가 맞으면 → 인자 채워 호출 → @tool.invoke 로 실제 실행·결과 출력
        (2) 적합한 도구가 없으면 → 호출하지 않고 LLM 이 스스로 답변

핵심:
  - bind_tools 기본 tool_choice="auto" → LLM 이 "도구 vs 직접답변" 을 알아서 선택.
  - 시스템 프롬프트로 "적합한 도구 없으면 호출하지 말고 직접 답하라" 명시.
  - 2.2/2.4 는 인자만 출력하고 실행은 주석이었지만, 여기선 실제로 실행해 결과를 보여준다.
"""

from typing import Literal
from pydantic import BaseModel, Field

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage

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
    """사용자가 요청하면 이메일을 보낸다. 실제로 보내지 않고 결과만 반환."""
    return f"이메일이 {to} 에게 전송되었습니다 (priority={priority}, subject='{subject}')."


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


tools = [send_email, search]
name2tool = {t.name: t for t in tools}

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)


# ─── 적합한 도구가 없으면 직접 답하게 가이드 ─────────────────
SYSTEM = (
    "당신은 비서입니다. 제공된 도구(send_email, search)가 적합할 때만 도구를 호출하세요. "
    "이메일 전송·검색과 무관한 질문은 도구를 호출하지 말고 당신이 아는 지식으로 직접 답하세요."
)


# ─── 호출 테스트 — 도구 선택 + 실제 실행까지 ────────────────
print("=" * 60)
print("도구를 쓸지 / 직접 답할지 + 실제 실행")
print("=" * 60)

queries = [
    "alice@example.com 에게 '회의 일정 변경' 제목으로 이메일 보내줘. "
    "본문은 '회의가 내일 3시로 변경되었습니다.' 야. 긴급해.",        # → send_email 실행
    "파이썬 비동기 프로그래밍 최신 자료 5개만 날짜순으로 검색해줘.",   # → search 실행
    "대한민국의 수도는 어디야?",                                     # → 적합한 도구 없음 → 직접 답
]

for q in queries:
    response = llm_with_tools.invoke([SystemMessage(SYSTEM), HumanMessage(q)])
    print(f"\n[질문] {q}")

    if not response.tool_calls:                       # 적합한 도구 없음 → LLM 이 직접 답
        print(f"  (도구 없이 직접 답변) {response.content}")
        continue

    for call in response.tool_calls:                  # 적합한 도구 → 인자 채워 실제 실행
        print(f"  → {call['name']}({call['args']})")
        result = name2tool[call["name"]].invoke(call["args"])   # @tool 실행
        print(f"     = {result}")
