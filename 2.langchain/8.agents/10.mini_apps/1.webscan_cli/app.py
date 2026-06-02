"""
서버 점검 에이전트 — CLI 버전. (2.webscan_app_web 의 터미널 판)
자연어 명령 → 적절한 점검 도구 자동 호출 → 결과 답변. + 멀티턴 메모리.

같은 도구(tools.py)·같은 에이전트를 쓰되, 웹(Flask) 대신 '터미널 입력 루프' 로 동작:
  - create_agent + ALL_TOOLS + MemorySaver (대화 맥락 유지)
  - 한 세션 = 하나의 thread_id

실행:  python app.py        ('exit' / '종료' 로 종료)
  ※ pip install langchain langchain-openai psutil requests python-dotenv
"""

import uuid

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from tools import ALL_TOOLS

load_dotenv()

SYSTEM = """당신은 서버 상태 점검을 도와주는 한국어 어시스턴트입니다.
- 자연어 요청을 적절한 점검 도구로 변환해 호출하세요.
- 결과는 한국어로 간결히 정리해 보여주세요.
- host/port 같은 인자는 사용자가 명시한 값을 그대로 사용.
- 한 번에 여러 점검이 필요하면 도구를 여러 번 호출하세요."""

agent = create_agent(
    ChatOpenAI(model="gpt-4o-mini", temperature=0),
    ALL_TOOLS,
    system_prompt=SYSTEM,
    checkpointer=MemorySaver(),
)
config = {"configurable": {"thread_id": uuid.uuid4().hex[:8]}, "recursion_limit": 15}


def ask(message: str):
    result = agent.invoke({"messages": [("user", message)]}, config=config)
    msgs = result["messages"]

    # 이번 질문으로 추가된 메시지만 본다 (마지막 사용자 메시지 이후) — 메모리 누적분 제외
    start = max((i for i, m in enumerate(msgs) if m.type == "human"), default=-1) + 1
    calls = [(c["name"], c["args"]) for m in msgs[start:]
             if getattr(m, "tool_calls", None) for c in m.tool_calls]

    # 질문에 따라 '어떤 도구(agent)를 어떤 인자(args)로' 골랐는지 출력
    if calls:
        print("  [선택된 도구 · 인자]")
        for name, args in calls:
            arg_str = ", ".join(f"{k}={v!r}" for k, v in args.items())
            print(f"    → {name}({arg_str})")
    else:
        print("  [도구 미사용 — 모델이 직접 답변]")

    print(msgs[-1].content)


if __name__ == "__main__":
    print("서버 점검 에이전트 (CLI) — 'exit' 로 종료\n")

    demo = "내 시스템 CPU/메모리/디스크 사용률 점검해줘"      # 시작 시 1회 데모
    print(f"[데모] {demo}")
    ask(demo)
    print()

    while True:
        try:
            q = input("점검 요청> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q.lower() in ("exit", "quit", "종료"):
            break
        if q:
            ask(q)
            print()
