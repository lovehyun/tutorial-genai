"""
human 빌트인 — 에이전트가 모르는 정보를 사용자에게 직접 되묻는 도구.
이 예제: load_tools(["human"]) 로 human 도구를 끼우면, LLM 이 모르는 것을 만나면
        답변 텍스트로 추측하지 않고 input() 으로 사람에게 질문해 값을 받아온다.

  - 사용자 이름·취향·일정처럼 LLM 이 알 수 없는 정보 → 추측 대신 되묻기 (HITL 의 가장 단순한 형태).
  - 주의: LLM 은 그냥 답변에 "알려주세요" 라고 쓰려는 경향이 있어, 시스템 프롬프트로
          "반드시 human 도구를 호출하라" 고 강하게 지시해야 도구를 쓴다.
  - 대화형 예제 — 실행하면 에이전트가 터미널로 질문을 던지고, 입력하면 이어서 답한다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import create_agent

load_dotenv()

SYSTEM = """당신은 사용자를 돕는 비서입니다.
사용자 개인정보(이름·취향·일정 등) 처럼 당신이 알 수 없는 정보가 필요하면,
답변 텍스트로 되묻지 말고 반드시 human 도구를 호출해 사용자에게 직접 물어보세요.
도구로 받은 값을 사용해 작업을 완료하세요."""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
tools = load_tools(["human"])     # 도구 이름: "human" (기본 input() 으로 사용자에게 질문)

agent = create_agent(llm, tools, system_prompt=SYSTEM)

# 에이전트는 이름을 모르므로 → human 도구로 사용자에게 물어본 뒤, 그 이름으로 인사한다.
result = agent.invoke({"messages": [("user", "내 이름을 넣어서 환영 인사 한 문장 만들어줘.")]})

print("\n[최종 답변]")
print(result["messages"][-1].content)
