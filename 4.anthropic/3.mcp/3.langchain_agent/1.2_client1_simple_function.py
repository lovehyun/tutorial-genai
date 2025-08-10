# simple_mcp_client.py - 핵심 흐름만
import asyncio
import os
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain_core.tools import Tool

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "false"


def create_mcp_tool():
    """MCP 도구 생성"""
    
    def call_say_hello(name: str) -> str:
        """server.py의 say_hello 호출"""
        async def run():
            server_params = StdioServerParameters(
                command="python", 
                args=["server.py"]
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool("say_hello", {"name": name})
                    return result.content[0].text
        
        return asyncio.run(run())
    
    return Tool(
        name="say_hello",
        func=call_say_hello,
        description="이름을 입력받아 인사말을 생성합니다"
    )


async def main():
    """메인 실행"""
    print("간단한 MCP 클라이언트 실행")
    
    # 도구 생성
    tool = create_mcp_tool()
    
    # LLM과 Agent 설정
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, [tool], prompt)
    agent_executor = AgentExecutor(agent=agent, tools=[tool], verbose=True)
    
    # 테스트 실행
    queries = ["Alice에게 인사해줘", "Bob에게 Hello라고 말해줘"]
    
    for query in queries:
        print(f"\n질문: {query}")
        response = await agent_executor.ainvoke({"input": query})
        print(f"결과: {response['output']}")


if __name__ == "__main__":
    asyncio.run(main())
