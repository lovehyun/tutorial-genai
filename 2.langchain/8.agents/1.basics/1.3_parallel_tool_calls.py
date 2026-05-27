"""
Parallel Tool Calling — 한 번의 LLM 응답으로 여러 도구를 동시에 호출

gpt-4o 같은 현행 모델은 "서울이랑 부산 날씨 비교해줘" 같은 질문에
get_weather('서울'), get_weather('부산') 두 도구를 **한 응답에 같이** 넣어준다.
순차 호출보다 빠르고 토큰도 절약.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()


# 1. 도구 정의 — 가짜 날씨 / 인구 데이터
@tool
def get_weather(city: str) -> str:
    """도시의 현재 날씨를 가져온다."""
    data = {"서울": "맑음, 22도", "부산": "흐림, 25도", "대전": "비, 19도"}
    return data.get(city, "정보 없음")

@tool
def get_population(city: str) -> str:
    """도시의 인구를 가져온다 (단위: 만 명)."""
    data = {"서울": "950", "부산": "330", "대전": "145"}
    return data.get(city, "정보 없음")


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools([get_weather, get_population])


# 2. 병렬 호출이 자연스러운 질문
question = "서울과 부산의 날씨와 인구를 모두 알려줘."

response = llm_with_tools.invoke([HumanMessage(content=question)])

print("=" * 60)
print(f"[질문] {question}")
print("=" * 60)
print(f"[LLM 이 한 번에 요청한 도구 호출 개수]: {len(response.tool_calls)}")
print()
for call in response.tool_calls:
    print(f"  - {call['name']}({call['args']})")


# 3. 병렬 실행 — 호출 4개를 모두 처리
tool_map = {"get_weather": get_weather, "get_population": get_population}
messages = [HumanMessage(content=question), response]

for call in response.tool_calls:
    result = tool_map[call["name"]].invoke(call["args"])
    print(f"\n[실행] {call['name']}({call['args']}) → {result}")
    messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))


# 4. 최종 답변
final = llm_with_tools.invoke(messages)
print("\n[최종 답변]")
print(final.content)


# ─────────────────────────────────────────────────────────
# 비교 — 옛날 (legacy) 에이전트:
#   서울 날씨 → 응답 → 부산 날씨 → 응답 → 서울 인구 → 응답 → 부산 인구 → 응답
#   = LLM 호출 4번 + 도구 실행 4번 (순차)
#
# 병렬 tool calling:
#   "이 4가지 도구를 동시에 부를게" → 도구 실행 4번 (병렬) → 최종 응답
#   = LLM 호출 2번 (1차 + 최종) + 도구 실행 4번
#
# → 입력 토큰 절약, latency 감소.
# → 명시적으로 끄려면: ChatOpenAI(..., parallel_tool_calls=False)
# ─────────────────────────────────────────────────────────
