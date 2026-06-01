"""
create_agent — 도구 사용 LLM 을 한 줄로 만드는 함수 (현행 표준, LangChain 1.x).
이 예제: 도구 1개 (수학 계산) 를 가진 가장 단순한 에이전트. (옛 create_react_agent API 를 현행 create_agent 로)

에이전트가 하는 일:
  1) 질문을 받고
  2) 도구가 필요한지 LLM 이 판단
  3) 필요하면 도구 호출 → 결과 → 다시 LLM 호출 → ... 반복 (ReAct 루프)
  4) 도구 없이 답할 수 있게 되면 최종 답변

  ※ 자동 루프는 내부(LangGraph)에서 처리. 우리는 도구만 주면 됨.

─── 변경 이력 (옛 create_react_agent → 이 파일) ──────────────
  LangChain 1.0 부터 prebuilt 에이전트 생성 함수가 이동/통합되었습니다.
  (검증 환경: 2026-06 기준 langchain 1.3.2)

    이전(deprecated)                          현행
    ────────────────────────────────────────────────────────────────
    from langgraph.prebuilt import           from langchain.agents import
        create_react_agent                       create_agent
    create_react_agent(llm, tools,           create_agent(llm, tools,
        prompt=system_prompt)                    system_prompt=system_prompt)
                                              # ↑ 인자 이름 prompt → system_prompt

  · 반환값은 둘 다 LangGraph CompiledStateGraph → .invoke({"messages": [...]}),
    .stream(), checkpointer=, interrupt_before=, response_format= 사용법 동일.
  · 그래프 노드 이름은 'agent' → 'model' 로 바뀜 (스트리밍에서 노드명 볼 때만 영향).
─────────────────────────────────────────────────────────────────────
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent      # (구) langgraph.prebuilt.create_react_agent

load_dotenv()


# 1) 도구 정의 — 가장 단순한 수학 계산기
@tool
def calculator(expression: str) -> str:
    """수학 식을 계산한다. 예: '53 * 7 + 2'"""
    try:
        return str(eval(expression))
        # eval("__import__('os').system('dir')")
        # eval("__import__('os').system('del important.txt')")

        # 보안을 위해 built-in 함수들을 제거
        # return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"계산 오류: {e}"


# 2) LLM + 도구를 묶어 에이전트 생성 (한 줄)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, [calculator])         # (구) create_react_agent(llm, [calculator])


# 3) 실행 — messages 형식으로 입력 (이전과 동일)
result = agent.invoke({
    "messages": [("user", "(53 * 7 + 2) / 5 는 얼마야?")]
})


# 4) 결과 확인 — 전체 대화 흐름이 messages 리스트로 옴 (agent가 하나라 큰 의미는 없음)
print("=== 전체 메시지 흐름 ===")
for m in result["messages"]:
    if hasattr(m, "tool_calls") and m.tool_calls:
        for c in m.tool_calls:
            print(f"  [도구 호출]  {c['name']}({c['args']})")
    if m.content:
        prefix = {"human": "[사용자]", "ai": "[AI]", "tool": "[도구 결과]"}.get(m.type, m.type)
        print(f"  {prefix} {m.content}")

print(f"\n최종 답변: {result['messages'][-1].content}")
