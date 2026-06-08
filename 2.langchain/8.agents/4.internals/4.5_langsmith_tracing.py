"""
관측성 — LangSmith 트레이싱으로 에이전트 내부를 들여다보기.
이 예제: 환경변수만 켜면 모든 LLM/도구 호출이 LangSmith 에 자동 기록된다 (코드 변경 0줄).

설정 (.env 또는 환경변수):
  LANGSMITH_TRACING=true
  LANGSMITH_API_KEY=lsv2_...        (https://smith.langchain.com 에서 발급)
  LANGSMITH_PROJECT=8.agents        (선택, 프로젝트명)

왜?
  - 에이전트는 블랙박스 → 어떤 도구를 왜 불렀는지, 토큰/지연/에러를 trace 로 확인
  - 운영 디버깅·평가·비용 분석의 출발점
"""

import os

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

from langchain_core.tools import tool
from langchain.agents import create_agent

load_dotenv()


@tool
def calculator(expression: str) -> str:
    """수학 식을 계산한다."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"오류: {e}"


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, [calculator])

# 트레이싱은 '환경변수'로만 켜짐 — 코드는 동일
enabled = os.getenv("LANGSMITH_TRACING", "").lower() == "true" and bool(os.getenv("LANGSMITH_API_KEY"))
print(f"LangSmith 트레이싱: {'ON' if enabled else 'OFF (환경변수 미설정 — 코드는 그대로 동작)'}")

result = agent.invoke({"messages": [("user", "(12 + 8) * 3 은?")]})
print(f"답변: {result['messages'][-1].content}")
if enabled:
    print("→ https://smith.langchain.com 에서 이번 실행 trace(모델/도구/토큰/지연) 확인")


# 정리:
#   - 코드 변경 없이 환경변수만으로 켜짐 (LANGSMITH_TRACING / LANGSMITH_API_KEY)
#   - trace 에 each step 기록: 모델 입력/출력, 도구 호출/결과, 토큰, 지연
#   - 평가(11.evaluation)·비용추적(4.6)과 함께 운영 모니터링 3종 세트
