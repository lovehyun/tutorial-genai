# 3.langgraph_agent_demo.py - create_agent (현행)
# 옛 `from langgraph.prebuilt import create_react_agent` 는 `from langchain.agents import create_agent` 로 이동·대체됨.
# create_agent 자체가 LangGraph 그래프(START→model→tools→END)이므로 이게 곧 'LangGraph 방식'이다.
# (옛 문법 비교: 8.mcp/4.langchain/0.legacy(deprecated)/)
import asyncio
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from mcp_bridge import MCPBridge

load_dotenv()

SYSTEM = ("당신은 다양한 도구를 사용할 수 있는 도움이 되는 어시스턴트입니다. "
          "요청을 분석해 적절한 도구를 사용해 정확히 답하세요. 복합 요청은 여러 도구를 순차 사용하세요.")


class LangGraphMCPAgent:
    def __init__(self, server_script: str = "server.py"):
        self.bridge = MCPBridge(server_script)
        self.agent = None

    async def initialize(self):
        print("create_agent(LangGraph) 초기화 중...")
        tools = await self.bridge.create_langchain_tools()
        llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        self.agent = create_agent(llm, tools, system_prompt=SYSTEM)
        print("초기화 완료!")

    async def invoke(self, user_input: str) -> str:
        result = await self.agent.ainvoke({"messages": [("user", user_input)]})
        return result["messages"][-1].content


async def demo():
    print("=== create_agent(LangGraph) 기반 MCP Bridge 데모 ===")
    agent = LangGraphMCPAgent()
    await agent.initialize()
    for t in ["Bob에게 인사해줘", "10 더하기 30은?", "25의 제곱근은?"]:
        print(f"\n질문: {t}")
        print(f"답변: {await agent.invoke(t)}")
        print("-" * 40)


async def interactive():
    agent = LangGraphMCPAgent()
    await agent.initialize()
    print("\n=== 대화형 모드 ('종료'로 끝) ===")
    while True:
        u = input("\n질문: ").strip()
        if u.lower() in ['종료', 'quit', 'exit']:
            print("대화를 종료합니다!")
            break
        if u:
            print(f"답변: {await agent.invoke(u)}")


if __name__ == "__main__":
    print("1. 자동 데모   2. 대화형 모드")
    choice = input("선택 (1/2): ").strip()
    asyncio.run(interactive() if choice == "2" else demo())
