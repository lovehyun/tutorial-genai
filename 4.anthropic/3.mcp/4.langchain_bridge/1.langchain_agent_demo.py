# simple_langchain_demo.py - 간단한 LangChain Agent 데모
import asyncio
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from mcp_bridge import MCPBridge

load_dotenv()

class SimpleMCPAgent:
    """간단한 MCP Agent"""
    
    def __init__(self):
        self.bridge = MCPBridge("server.py")
        self.agent_executor = None
        
    async def initialize(self):
        """에이전트 초기화"""
        print("MCP 도구 발견 중...")
        tools = await self.bridge.create_langchain_tools()
        print(f"{len(tools)}개 도구 준비 완료")
        
        # LLM과 프롬프트 설정
        llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        prompt = hub.pull("hwchase17/react")
        
        # 에이전트 생성
        agent = create_react_agent(llm, tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent, 
            tools=tools, 
            verbose=True,
            max_iterations=3
        )
        
    def run(self, user_input: str) -> str:
        """사용자 입력 처리"""
        result = self.agent_executor.invoke({"input": user_input})
        return result["output"]

async def demo():
    """간단한 데모"""
    print("=== LangChain MCP Agent 데모 ===\n")
    
    # 에이전트 초기화
    agent = SimpleMCPAgent()
    await agent.initialize()
    
    # 테스트 케이스
    tests = [
        "Alice에게 인사해줘",
        "15 더하기 25는?",
        "16의 제곱근은?",
    ]
    
    for test in tests:
        print(f"\n질문: {test}")
        response = agent.run(test)
        print(f"답변: {response}")
        print("-" * 40)

async def interactive():
    """대화형 모드"""
    print("=== LangChain 대화형 모드 ===")
    print("'종료'를 입력하면 끝납니다\n")
    
    agent = SimpleMCPAgent()
    await agent.initialize()
    
    while True:
        user_input = input("\n질문: ").strip()
        if user_input.lower() in ['종료', 'quit', 'exit']:
            print("대화를 종료합니다!")
            break
        
        if user_input:
            response = agent.run(user_input)
            print(f"답변: {response}")

if __name__ == "__main__":
    print("모드를 선택하세요:")
    print("1. 자동 데모")
    print("2. 대화형 모드")
    
    choice = input("선택 (1/2): ").strip()
    
    if choice == "1":
        asyncio.run(demo())
    elif choice == "2":
        asyncio.run(interactive())
    else:
        print("1 또는 2를 선택해주세요.")
