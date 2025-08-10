# langchain_agent_demo.py - 최신 LangChain Agent 방식
import asyncio
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent

from mcp_bridge import MCPBridge

load_dotenv()

class ModernMCPAgent:
    """최신 LangChain 방식을 사용한 MCP Agent"""
    
    def __init__(self, server_script: str = "server.py"):
        self.bridge = MCPBridge(server_script)
        self.agent_executor = None
        
    async def initialize(self):
        """에이전트 초기화 (최신 방식 사용)"""
        print("MCP Bridge를 통한 도구 자동 발견 중...")
        
        # MCP 도구들을 LangChain Tool로 자동 변환
        tools = await self.bridge.create_langchain_tools()
        
        # LangChain LLM 생성
        llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        
        # 방법 1: LangChain Hub에서 기본 ReAct 프롬프트 사용 (권장)
        try:
            prompt = hub.pull("hwchase17/react")
        except:
            # Hub 접근 실패 시 수동으로 ReAct 프롬프트 생성
            prompt = PromptTemplate.from_template("""Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
Thought:{agent_scratchpad}""")
        
        # 최신 방식: create_react_agent 사용
        agent = create_react_agent(llm, tools, prompt)
        
        # AgentExecutor 생성
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            return_intermediate_steps=False
        )
        
        print("LangChain 에이전트 초기화 완료!")
        
    def invoke(self, user_input: str) -> str:
        """사용자 입력 처리 (최신 invoke 방식)"""
        if not self.agent_executor:
            raise ValueError("에이전트가 초기화되지 않았습니다. initialize()를 먼저 호출하세요.")
        
        try:
            # 최신 방식: invoke 사용 (run은 deprecated)
            result = self.agent_executor.invoke({"input": user_input})
            return result["output"]
        except Exception as e:
            return f"에이전트 실행 오류: {str(e)}"
    
    async def stream(self, user_input: str):
        """스트리밍 응답 (최신 기능)"""
        if not self.agent_executor:
            raise ValueError("에이전트가 초기화되지 않았습니다.")
        
        try:
            print("AI 응답 (스트리밍):")
            async for chunk in self.agent_executor.astream({"input": user_input}):
                # 각 단계별 출력 처리
                if "actions" in chunk:
                    for action in chunk["actions"]:
                        print(f"도구 사용: {action.tool} - {action.tool_input}")
                elif "steps" in chunk:
                    for step in chunk["steps"]:
                        print(f"관찰: {step.observation}")
                elif "output" in chunk:
                    print(f"최종 답변: {chunk['output']}")
                elif "intermediate_step" in chunk:
                    print(f"중간 단계: {chunk['intermediate_step']}")
                else:
                    # 기타 청크 정보 출력
                    print(f"청크: {chunk}")
        except Exception as e:
            print(f"스트리밍 오류: {str(e)}")


async def langchain_automated_demo():
    """LangChain 방식 자동화된 데모"""
    agent = ModernMCPAgent("server.py")
    await agent.initialize()
    
    test_cases = [
        "Alice에게 인사해줘",
        "15 더하기 25는 얼마야?",
        "3.5 곱하기 2.8은?",
        "지금 몇 시야?",
        "16의 제곱근은?",
        "5 팩토리얼은?",
        "Bob에게 인사하고 10 더하기 20도 계산해줘"  # 복합 요청
    ]
    
    print("=== LangChain Agent 기반 MCP Bridge 데모 ===")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n테스트 {i}/{len(test_cases)}")
        print(f"사용자: {test}")
        
        try:
            response = agent.invoke(test)
            print(f"AI: {response}")
        except Exception as e:
            print(f"오류: {e}")
        
        print("-" * 50)


async def langchain_interactive_demo():
    """LangChain 방식 대화형 데모"""
    agent = ModernMCPAgent("server.py")
    await agent.initialize()
    
    print("\n=== LangChain Agent 대화형 모드 ===")
    print("'quit'를 입력하면 종료됩니다")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n사용자: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '종료']:
                print("대화를 종료합니다!")
                break
                
            if not user_input:
                continue
                
            response = agent.invoke(user_input)
            print(f"AI: {response}")
            
        except KeyboardInterrupt:
            print("\n대화를 종료합니다!")
            break
        except Exception as e:
            print(f"오류: {e}")


async def langchain_streaming_demo():
    """LangChain 스트리밍 데모"""
    agent = ModernMCPAgent("server.py")
    await agent.initialize()
    
    print("\n=== LangChain Agent 스트리밍 데모 ===")
    test_input = "Alice에게 인사하고 15 더하기 25도 계산해줘"
    print(f"사용자: {test_input}")
    
    await agent.stream(test_input)


if __name__ == "__main__":
    print("LangChain Agent 실행 모드를 선택하세요:")
    print("1. 자동 데모")
    print("2. 대화형 모드") 
    print("3. 스트리밍 데모")
    
    choice = input("선택 (1/2/3): ").strip()
    
    if choice == "1":
        asyncio.run(langchain_automated_demo())
    elif choice == "2":
        asyncio.run(langchain_interactive_demo())
    elif choice == "3":
        asyncio.run(langchain_streaming_demo())
    else:
        print(f"❌ 잘못된 선택입니다: '{choice}'")
        print("1, 2, 3 중에서 선택해주세요.")
