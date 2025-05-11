from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

# MCP 툴 호출을 감싸는 함수
def call_mcp_say_hello(name: str) -> str:
    async def run_tool():
        server_params = StdioServerParameters(command="python", args=["server.py"])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("say_hello", {"name": name})
                content_text = result.content[0].text
                return json.loads(content_text)["greeting"]

    return asyncio.run(run_tool())

say_hello_tool = Tool(
    name="say_hello",
    func=call_mcp_say_hello,
    description="입력된 이름으로 인사합니다."
)

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(temperature=0)
agent = initialize_agent(
    tools=[say_hello_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

response = agent.run("John 에게 인사해줘")
print(response)
