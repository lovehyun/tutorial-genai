# 2.langchain_agent2_demo_except.py - create_agent + 예외 처리 + 스트리밍 (현행)
# 옛 create_react_agent + AgentExecutor.astream → create_agent + agent.astream(stream_mode=...).
# (옛 문법 비교: 8.mcp/4.langchain/0.legacy(deprecated)/)
import asyncio
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from mcp_bridge import MCPBridge

load_dotenv()


class ModernMCPAgent:
    def __init__(self, server_script: str = "server.py"):
        self.bridge = MCPBridge(server_script)
        self.agent = None

    async def initialize(self):
        print("MCP Bridge 로 도구 자동 발견 중...")
        tools = await self.bridge.create_langchain_tools()
        llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        self.agent = create_agent(llm, tools)
        print("에이전트 초기화 완료!")

    async def invoke(self, user_input: str) -> str:
        try:
            result = await self.agent.ainvoke({"messages": [("user", user_input)]})
            return result["messages"][-1].content
        except Exception as e:
            return f"에이전트 실행 오류: {e}"

    async def stream(self, user_input: str):
        """노드 단위 스트리밍 — 도구 호출/응답을 단계별로 출력"""
        print("AI 응답 (스트리밍):")
        try:
            async for chunk in self.agent.astream(
                {"messages": [("user", user_input)]}, stream_mode="updates"
            ):
                for node, update in chunk.items():
                    msgs = update.get("messages", []) if isinstance(update, dict) else []
                    for m in msgs:
                        for c in getattr(m, "tool_calls", []) or []:
                            print(f"  [도구 호출] {c['name']}({c['args']})")
                        if getattr(m, "content", ""):
                            print(f"  [{node}] {m.content}")
        except Exception as e:
            print(f"스트리밍 오류: {e}")


async def automated_demo():
    agent = ModernMCPAgent("server.py")
    await agent.initialize()
    tests = ["Alice에게 인사해줘", "15 더하기 25는?", "16의 제곱근은?",
             "5 팩토리얼은?", "Bob에게 인사하고 10 더하기 20도 계산해줘"]
    print("=== create_agent 기반 MCP Bridge 데모 ===")
    for i, t in enumerate(tests, 1):
        print(f"\n[{i}] 사용자: {t}")
        print(f"AI: {await agent.invoke(t)}")
        print("-" * 50)


async def streaming_demo():
    agent = ModernMCPAgent("server.py")
    await agent.initialize()
    test = "Alice에게 인사하고 15 더하기 25도 계산해줘"
    print(f"\n사용자: {test}")
    await agent.stream(test)


if __name__ == "__main__":
    print("1. 자동 데모   2. 스트리밍 데모")
    choice = input("선택 (1/2): ").strip()
    asyncio.run(streaming_demo() if choice == "2" else automated_demo())
