"""
토큰/비용 추적 — 응답의 usage_metadata 로 호출별 토큰 집계.
이 예제: 에이전트 실행 후 누적 입력/출력 토큰을 합산해 대략 비용을 가늠한다.

왜?
  - 도구 호출마다 LLM 이 여러 번 불리므로 '한 질문'도 토큰이 쌓임
  - 운영 비용/한도 관리의 기본 = 토큰 가시화
"""

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

result = agent.invoke({"messages": [("user", "(53*7+2)/5 와 100-37 을 각각 계산해줘")]})

# 각 AIMessage 에 usage_metadata 가 붙음 → 합산
in_tok = out_tok = 0
for m in result["messages"]:
    u = getattr(m, "usage_metadata", None)
    if u:
        in_tok += u["input_tokens"]
        out_tok += u["output_tokens"]

print(f"답변: {result['messages'][-1].content}")
print(f"누적 토큰 — 입력 {in_tok}, 출력 {out_tok}, 합 {in_tok + out_tok}")

# gpt-4o-mini 예시 단가(2026 기준, 변동 가능): 입력 $0.15/1M, 출력 $0.60/1M
cost = in_tok / 1e6 * 0.15 + out_tok / 1e6 * 0.60
print(f"대략 비용: ${cost:.6f}")


# 정리:
#   - 각 AIMessage.usage_metadata = {input_tokens, output_tokens, total_tokens}
#   - 도구 루프가 길수록 토큰 누적 → 5.5(trim) / 12.1(요약)로 관리
#   - 정확한 비용은 모델별 최신 단가표 확인, 운영 집계는 LangSmith(4.5) 권장
