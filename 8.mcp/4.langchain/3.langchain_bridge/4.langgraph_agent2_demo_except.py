# 4.langgraph_agent2_demo_except.py - create_agent + 스트리밍/디버그 (현행)
# 옛 langgraph.prebuilt.create_react_agent → langchain.agents.create_agent.
# 그래프 노드 이름: 옛 'agent' → 현행 'model' (스트리밍에서 노드명 볼 때 영향).
# (옛 문법 비교: 8.mcp/4.langchain/0.legacy(deprecated)/)
import asyncio
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from mcp_bridge import MCPBridge

load_dotenv()

SYSTEM = "당신은 도구를 사용할 수 있는 어시스턴트입니다. 적절한 도구로 정확히 답하세요."


class LangGraphMCPAgent:
    def __init__(self, server_script: str = "server.py"):
        self.bridge = MCPBridge(server_script)
        self.agent = None

    async def initialize(self):
        tools = await self.bridge.create_langchain_tools()
        llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        self.agent = create_agent(llm, tools, system_prompt=SYSTEM)
        print("LangGraph(create_agent) 에이전트 초기화 완료!")

    async def invoke(self, user_input: str) -> str:
        try:
            result = await self.agent.ainvoke({"messages": [("user", user_input)]})
            return result["messages"][-1].content
        except Exception as e:
            return f"에이전트 오류: {e}"

    async def stream(self, user_input: str):
        """노드 단위 스트리밍 (model / tools 노드)"""
        print("AI 응답 (스트리밍):")
        async for chunk in self.agent.astream(
            {"messages": [("user", user_input)]}, stream_mode="updates"
        ):
            for node, update in chunk.items():
                for m in (update.get("messages", []) if isinstance(update, dict) else []):
                    for c in getattr(m, "tool_calls", []) or []:
                        print(f"  [{node}] 도구 호출: {c['name']}({c['args']})")
                    if getattr(m, "content", ""):
                        print(f"  [{node}] {m.content}")

    async def debug(self, user_input: str):
        """전체 메시지 흐름 출력 (디버깅)"""
        result = await self.agent.ainvoke({"messages": [("user", user_input)]})
        print(f"메시지 수: {len(result['messages'])}")
        for i, m in enumerate(result["messages"], 1):
            print(f"  {i}. {type(m).__name__}: {(m.content or '(도구 호출)')[:80]}")


async def automated_demo():
    agent = LangGraphMCPAgent()
    await agent.initialize()
    for t in ["Alice에게 인사해줘", "15 더하기 25는?", "5 팩토리얼은?",
              "Bob에게 인사하고 10 더하기 20도 계산해줘"]:
        print(f"\n사용자: {t}")
        print(f"AI: {await agent.invoke(t)}")
        print("-" * 50)


async def streaming_demo():
    agent = LangGraphMCPAgent()
    await agent.initialize()
    await agent.stream("Alice에게 인사하고 15 더하기 25도 계산해줘")


async def debug_demo():
    agent = LangGraphMCPAgent()
    await agent.initialize()
    print("\n=== 디버깅(메시지 흐름) ===")
    await agent.debug("15 더하기 25는 얼마야?")


if __name__ == "__main__":
    print("1. 자동 데모   2. 스트리밍   3. 디버깅")
    choice = input("선택 (1/2/3): ").strip()
    if choice == "2":
        asyncio.run(streaming_demo())
    elif choice == "3":
        asyncio.run(debug_demo())
    else:
        asyncio.run(automated_demo())
