"""
response_format — 에이전트의 최종 답변을 Pydantic 모델로 강제.
이 예제: 도구로 정보 수집 후, 최종 응답을 자유 문장 대신 구조화된 dict 로 받습니다.

언제 유용한가:
  - API 응답으로 정형 데이터를 돌려줘야 할 때
  - 후속 코드가 정확한 필드 (name, score 등) 를 기대할 때
  - 자유 문장 파싱 (regex / json.loads) 의 불안정성을 피하고 싶을 때

create_agent(..., response_format=PydanticModel) 한 줄로 끝.
내부적으로 에이전트가 마지막에 그 스키마를 만족하는 JSON 을 생성하고, dict 로 파싱돼서 옴.
"""

from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent   # (구) langgraph.prebuilt.create_react_agent

load_dotenv()


# ─── 도구: 영화 정보 조회 (가짜 DB) ─────────────────────────
@tool
def lookup_movie(title: str) -> str:
    """영화 제목으로 정보를 조회한다."""
    db = {
        "인터스텔라": "감독: 크리스토퍼 놀란, 2014년, 평점 8.6/10. SF 우주 영화. 러닝타임 169분.",
        "기생충":     "감독: 봉준호, 2019년, 평점 8.5/10. 한국 영화. 칸/오스카 수상.",
    }
    return db.get(title, "정보 없음")


# ─── 출력 스키마 정의 — 에이전트가 이 모양으로 답하도록 강제 ───
class MovieReview(BaseModel):
    """영화 한 편에 대한 구조화 정보."""
    title: str = Field(description="영화 제목")
    director: str = Field(description="감독 이름")
    year: int = Field(description="개봉 연도")
    rating: float = Field(description="평점 (10점 만점)")
    genre: Literal["SF", "드라마", "액션", "코미디", "기타"] = Field(description="장르")
    summary: str = Field(description="한 줄 요약 (한국어)")


# ─── 에이전트 — response_format 지정 ─────────────────────────
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(
    llm,
    tools=[lookup_movie],
    response_format=MovieReview,    # ← 최종 답변 스키마 강제
)


# ─── 실행 — 결과에 structured_response 키가 추가됨 ─────────
result = agent.invoke({
    "messages": [("user", "'인터스텔라' 정보 조회해서 정리해줘.")]
})

# 1) 자유 문장 답변 (messages 의 마지막)
print("=== 자유 문장 답변 ===")
print(result["messages"][-1].content)

# 2) ★ 구조화된 응답 — Pydantic 모델 인스턴스
print("\n=== 구조화된 응답 (structured_response) ===")
review: MovieReview = result["structured_response"]
print(f"  title     : {review.title}")
print(f"  director  : {review.director}")
print(f"  year      : {review.year}")
print(f"  rating    : {review.rating}")
print(f"  genre     : {review.genre}")
print(f"  summary   : {review.summary}")

print(f"\n  type({type(review).__name__}) — 그대로 후속 코드에서 사용 가능")
