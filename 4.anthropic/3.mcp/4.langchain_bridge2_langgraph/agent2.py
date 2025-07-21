# agent2.py - Verbose 출력 수정 버전

import asyncio
from typing import List
from dotenv import load_dotenv
import warnings

load_dotenv()

# LangGraph Agent (권장)
class MCPAgent:
    """LangGraph를 사용한 MCP Agent"""
    
    def __init__(self, server_script: str = "server.py"):
        from mcp_bridge import MCPBridge
        self.bridge = MCPBridge(server_script)
        self.agent = None
        self.tools = []
        
    async def initialize(self):
        """에이전트 초기화 (MCP 도구 자동 발견)"""
        from langgraph.prebuilt import create_react_agent
        from langchain_openai import ChatOpenAI
        
        print("MCP Bridge를 통한 도구 자동 발견 중...")
        
        # MCP 도구들을 LangChain Tool로 자동 변환
        self.tools = await self.bridge.create_langchain_tools()
        
        # LangGraph ReAct Agent 생성
        llm = ChatOpenAI(temperature=0, model="gpt-4")
        
        self.agent = create_react_agent(
            model=llm,
            tools=self.tools,
            state_modifier="당신은 MCP 도구를 사용할 수 있는 유능한 AI 어시스턴트입니다."
        )
        
        print("LangGraph 에이전트 초기화 완료!")
        
    async def run(self, user_input: str) -> str:
        """사용자 입력 처리 (비동기)"""
        if not self.agent:
            raise ValueError("에이전트가 초기화되지 않았습니다.")
        
        try:
            response = await self.agent.ainvoke(
                {"messages": [("user", user_input)]},
                config={"configurable": {"thread_id": "1"}}
            )
            
            last_message = response["messages"][-1]
            return last_message.content
            
        except Exception as e:
            return f"에이전트 실행 오류: {str(e)}"

# Legacy Agent (Verbose 출력 보장)
class LegacyMCPAgent:
    """기존 LangChain Agent (Verbose 출력 보장)"""
    
    def __init__(self, server_script: str = "server.py", verbose: bool = True):
        from mcp_bridge import MCPBridge
        self.bridge = MCPBridge(server_script)
        self.agent = None
        self.verbose = verbose
        
    async def initialize(self):
        """에이전트 초기화 (초기화만 비동기)"""
        from langchain.agents import initialize_agent, AgentType
        from langchain_openai import ChatOpenAI
        
        print("MCP Bridge를 통한 도구 자동 발견 중...")
        
        # MCP 도구들을 LangChain Tool로 자동 변환
        tools = await self.bridge.create_langchain_tools()
        
        # Deprecation 경고만 억제, 다른 출력은 유지
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*LangChain agents will continue.*")
            warnings.filterwarnings("ignore", message=".*deprecated.*")
            
            llm = ChatOpenAI(temperature=0)
            self.agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=self.verbose,  # Verbose 설정
                handle_parsing_errors=True,
                return_intermediate_steps=False
            )
        
        print(f"레거시 에이전트 초기화 완료! (Verbose: {self.verbose})")
        
    def run(self, user_input: str) -> str:
        """사용자 입력 처리 (완전 동기)"""
        if not self.agent:
            raise ValueError("에이전트가 초기화되지 않았습니다.")
        
        try:
            # Run 메서드의 deprecation 경고만 억제
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message=".*method.*run.*deprecated.*")
                
                # run 메서드 사용 (verbose 출력을 위해)
                response = self.agent.run(user_input)
                return response
                
        except Exception as e:
            return f"에이전트 실행 오류: {str(e)}"

# Verbose 강제 활성화 버전
class VerboseMCPAgent(LegacyMCPAgent):
    """Verbose 출력을 강제로 활성화한 Agent"""
    
    def __init__(self, server_script: str = "server.py"):
        super().__init__(server_script, verbose=True)
        
    async def initialize(self):
        """Verbose 출력을 위한 특별 초기화"""
        from langchain.agents import initialize_agent, AgentType
        from langchain_openai import ChatOpenAI
        import sys
        
        print("MCP Bridge를 통한 도구 자동 발견 중...")
        
        # MCP 도구들을 LangChain Tool로 자동 변환
        tools = await self.bridge.create_langchain_tools()
        
        # 표준 출력 확보
        original_stdout = sys.stdout
        
        try:
            llm = ChatOpenAI(temperature=0)
            
            # Verbose 출력을 위해 경고 최소화
            import logging
            logging.getLogger("langchain").setLevel(logging.WARNING)
            
            self.agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,  # 강제 활성화
                handle_parsing_errors=True,
                max_iterations=5,
                early_stopping_method="generate"
            )
            
        finally:
            sys.stdout = original_stdout
        
        print("Verbose Agent 초기화 완료! (Thought 출력 보장)")
        
    def run(self, user_input: str) -> str:
        """Verbose 출력을 보장하는 실행"""
        if not self.agent:
            raise ValueError("에이전트가 초기화되지 않았습니다.")
        
        print(f"\n{'='*20} AGENT 실행 시작 {'='*20}")
        
        try:
            # 모든 경고 억제 해제하여 Verbose 출력 보장
            response = self.agent.run(user_input)
            print(f"{'='*20} AGENT 실행 완료 {'='*20}\n")
            return response
                
        except Exception as e:
            print(f"{'='*20} AGENT 실행 오류 {'='*20}\n")
            return f"에이전트 실행 오류: {str(e)}"
