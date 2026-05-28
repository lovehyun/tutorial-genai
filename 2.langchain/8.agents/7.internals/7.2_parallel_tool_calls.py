"""
Parallel Tool Calling — 한 응답에 여러 도구를 동시에 호출.
이 예제: "서울이랑 부산 날씨/인구 비교" 처럼 자연스러운 병렬 호출을 관찰합니다.

gpt-4o 같은 현대 모델은 독립적인 여러 도구 호출을 한 응답에 모아서 줍니다.
순차 호출보다 빠르고 LLM 호출 횟수 절약.

  - 순차 (옛 방식): 도구 1회 호출 → LLM → 도구 1회 호출 → LLM → ... (LLM 호출 N+1)
  - 병렬 (현 방식): 도구 N개 한꺼번에 → 결과 모아서 → LLM 1회 (LLM 호출 2)

명시적으로 끄려면: `ChatOpenAI(parallel_tool_calls=False)`
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """도시의 현재 날씨를 가져온다."""
    return {"서울": "맑음, 22도", "부산": "흐림, 25도", "대전": "비, 19도"}.get(city, "정보 없음")

@tool
def get_population(city: str) -> str:
    """도시의 인구를 가져온다 (단위: 만 명)."""
    return {"서울": "950", "부산": "330", "대전": "145"}.get(city, "정보 없음")


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools([get_weather, get_population])


# 병렬 호출이 자연스러운 질문
question = "서울과 부산의 날씨와 인구를 모두 알려줘."
response = llm_with_tools.invoke([HumanMessage(content=question)])

print("=" * 60)
print(f"[질문] {question}")
print("=" * 60)
print(f"[병렬로 요청된 도구 호출 수]: {len(response.tool_calls)}\n")
for call in response.tool_calls:
    print(f"  - {call['name']}({call['args']})")


# 모든 도구 결과를 모아서 LLM 에 회신
tool_map = {"get_weather": get_weather, "get_population": get_population}
messages = [HumanMessage(content=question), response]
for call in response.tool_calls:
    result = tool_map[call["name"]].invoke(call["args"])
    messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))


final = llm_with_tools.invoke(messages)
print(f"\n[최종 답변]\n{final.content}")


# 비교:
#   옛 (initialize_agent ZERO_SHOT_REACT): 매 도구 호출마다 LLM 한 번씩 → 4개 도구 = 5번 LLM 호출
#   현재 (parallel tool calls):           1차 LLM → 도구 4개 병렬 → 1차 LLM = 2번 LLM 호출
#   → latency / 비용 둘 다 ↓
