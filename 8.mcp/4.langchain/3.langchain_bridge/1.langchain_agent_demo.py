# 2.langchain_agent_demo.py - MCPBridge + create_agent (현행 LangChain 1.x)
# 옛 create_react_agent + AgentExecutor + hub.pull → create_agent 한 줄로 통합.
# (옛 문법 비교: 8.mcp/4.langchain/0.legacy(deprecated)/)
import asyncio
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from mcp_bridge import MCPBridge

load_dotenv()


class SimpleMCPAgent:
    """MCPBridge 로 도구를 받아 create_agent 에 연결하는 간단 에이전트"""

    def __init__(self):
        self.bridge = MCPBridge("server.py")
        self.agent = None

    async def initialize(self):
        print("MCP 도구 발견 중...")
        tools = await self.bridge.create_langchain_tools()
        print(f"{len(tools)}개 도구 준비 완료")
        llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        self.agent = create_agent(llm, tools)   # 옛 create_react_agent + AgentExecutor + hub 통합

    async def run(self, user_input: str) -> str:
        result = await self.agent.ainvoke({"messages": [("user", user_input)]})
        return result["messages"][-1].content


async def demo():
    print("=== LangChain MCP Agent 데모 (create_agent) ===\n")
    agent = SimpleMCPAgent()
    await agent.initialize()

    for q in ["Alice에게 인사해줘", "15 더하기 25는?", "16의 제곱근은?"]:
        print(f"\n질문: {q}")
        print(f"답변: {await agent.run(q)}")
        print("-" * 40)


async def interactive():
    print("=== 대화형 모드 ('종료'로 끝) ===\n")
    agent = SimpleMCPAgent()
    await agent.initialize()
    while True:
        user_input = input("\n질문: ").strip()
        if user_input.lower() in ['종료', 'quit', 'exit']:
            print("대화를 종료합니다!")
            break
        if user_input:
            print(f"답변: {await agent.run(user_input)}")


if __name__ == "__main__":
    print("1. 자동 데모   2. 대화형 모드")
    choice = input("선택 (1/2): ").strip()
    asyncio.run(interactive() if choice == "2" else demo())
