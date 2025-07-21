from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from mcp_bridge import MCPBridge

load_dotenv()

class MCPAgent:
    """MCP Bridge를 사용한 LangChain Agent"""
    
    def __init__(self, server_script: str = "server.py"):
        self.bridge = MCPBridge(server_script)
        self.agent = None
        
    async def initialize(self):
        """에이전트 초기화 (MCP 도구 자동 발견)"""
        print("MCP Bridge를 통한 도구 자동 발견 중...")
        
        # MCP 도구들을 LangChain Tool로 자동 변환
        tools = await self.bridge.create_langchain_tools()
        
        # LangChain LLM 및 Agent 생성
        llm = ChatOpenAI(temperature=0)
        self.agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )
        
        print("에이전트 초기화 완료!")
        
    def run(self, user_input: str) -> str:
        """사용자 입력 처리"""
        if not self.agent:
            raise ValueError("에이전트가 초기화되지 않았습니다. initialize()를 먼저 호출하세요.")
        
        try:
            return self.agent.run(user_input)
        except Exception as e:
            return f"에이전트 실행 오류: {str(e)}"
