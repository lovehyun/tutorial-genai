# langgraph_agent_demo.py - LangGraph 방식 (가장 최신)
import asyncio
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from mcp_bridge import MCPBridge

load_dotenv()

class LangGraphMCPAgent:
    """LangGraph를 사용한 최신 MCP Agent"""
    
    def __init__(self, server_script: str = "server.py"):
        self.bridge = MCPBridge(server_script)
        self.agent = None
        
    async def initialize(self):
        """LangGraph 에이전트 초기화"""
        print("LangGraph MCP Agent 초기화 중...")
        
        # MCP 도구들을 LangChain Tool로 자동 변환
        tools = await self.bridge.create_langchain_tools()
        
        # LangChain LLM 생성
        llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        
        # LangGraph의 create_react_agent 사용
        # 시스템 프롬프트를 문자열로 제공
        system_prompt = """당신은 다양한 도구를 사용할 수 있는 도움이 되는 어시스턴트입니다.
사용자의 요청을 분석하고 적절한 도구를 사용하여 정확한 답변을 제공하세요.
복합적인 요청의 경우 여러 도구를 순차적으로 사용할 수 있습니다."""
        
        self.agent = create_react_agent(
            model=llm, 
            tools=tools,
            prompt=system_prompt
        )
        
        print("LangGraph 에이전트 초기화 완료!")
        
    async def invoke(self, user_input: str):
        """LangGraph 방식으로 처리"""
        if not self.agent:
            raise ValueError("에이전트가 초기화되지 않았습니다.")
        
        try:
            # LangGraph 방식
            messages = [HumanMessage(content=user_input)]
            result = await self.agent.ainvoke({"messages": messages})
            
            # 마지막 메시지 반환 (AI의 최종 응답)
            last_message = result["messages"][-1]
            return last_message.content
        except Exception as e:
            return f"LangGraph 에이전트 오류: {str(e)}"
    
    async def stream(self, user_input: str):
        """LangGraph 스트리밍"""
        if not self.agent:
            raise ValueError("에이전트가 초기화되지 않았습니다.")
        
        try:
            messages = [HumanMessage(content=user_input)]
            
            print("AI 응답 (스트리밍):")
            async for chunk in self.agent.astream({"messages": messages}):
                # 각 노드의 출력을 처리
                for node_name, node_output in chunk.items():
                    if node_name == "agent" and "messages" in node_output:
                        message = node_output["messages"][-1]
                        if hasattr(message, 'content') and message.content:
                            print(f"[{node_name}]: {message.content}")
                    elif node_name == "tools" and "messages" in node_output:
                        message = node_output["messages"][-1]
                        print(f"[도구 실행 결과]: {message.content}")
                        
        except Exception as e:
            print(f"스트리밍 오류: {str(e)}")
    
    async def get_graph_state(self, user_input: str):
        """그래프 상태 정보 반환 (디버깅용)"""
        if not self.agent:
            raise ValueError("에이전트가 초기화되지 않았습니다.")
        
        messages = [HumanMessage(content=user_input)]
        
        # 중간 단계들도 포함해서 반환
        config = {"configurable": {"thread_id": "demo"}}
        result = await self.agent.ainvoke({"messages": messages}, config=config)
        
        return result


async def langgraph_automated_demo():
    """LangGraph 방식 자동화된 데모"""
    agent = LangGraphMCPAgent("server.py")
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
    
    print("=== LangGraph Agent 기반 MCP Bridge 데모 ===")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n테스트 {i}/{len(test_cases)}")
        print(f"사용자: {test}")
        
        try:
            response = await agent.invoke(test)
            print(f"AI: {response}")
        except Exception as e:
            print(f"오류: {e}")
        
        print("-" * 50)


async def langgraph_interactive_demo():
    """LangGraph 방식 대화형 데모"""
    agent = LangGraphMCPAgent("server.py")
    await agent.initialize()
    
    print("\n=== LangGraph Agent 대화형 모드 ===")
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
                
            response = await agent.invoke(user_input)
            print(f"AI: {response}")
            
        except KeyboardInterrupt:
            print("\n대화를 종료합니다!")
            break
        except Exception as e:
            print(f"오류: {e}")


async def langgraph_streaming_demo():
    """LangGraph 스트리밍 데모"""
    agent = LangGraphMCPAgent("server.py")
    await agent.initialize()
    
    print("\n=== LangGraph Agent 스트리밍 데모 ===")
    test_input = "Alice에게 인사하고 15 더하기 25도 계산해줘"
    print(f"사용자: {test_input}")
    
    await agent.stream(test_input)


async def langgraph_debug_demo():
    """LangGraph 디버깅 데모 (그래프 상태 확인)"""
    agent = LangGraphMCPAgent("server.py")
    await agent.initialize()
    
    print("\n=== LangGraph 디버깅 데모 ===")
    test_input = "15 더하기 25는 얼마야?"
    print(f"사용자: {test_input}")
    
    try:
        result = await agent.get_graph_state(test_input)
        print(f"\n전체 그래프 상태:")
        print(f"메시지 수: {len(result['messages'])}")
        for i, msg in enumerate(result['messages']):
            print(f"  {i+1}. {type(msg).__name__}: {msg.content[:100]}...")
    except Exception as e:
        print(f"디버깅 오류: {e}")


if __name__ == "__main__":
    print("LangGraph Agent 실행 모드를 선택하세요:")
    print("1. 자동 데모")
    print("2. 대화형 모드")
    print("3. 스트리밍 데모") 
    print("4. 디버깅 데모")
    
    choice = input("선택 (1/2/3/4): ").strip()
    
    if choice == "1":
        asyncio.run(langgraph_automated_demo())
    elif choice == "2":
        asyncio.run(langgraph_interactive_demo())
    elif choice == "3":
        asyncio.run(langgraph_streaming_demo())
    elif choice == "4":
        asyncio.run(langgraph_debug_demo())
    else:
        print(f"❌ 잘못된 선택입니다: '{choice}'")
        print("1, 2, 3, 4 중에서 선택해주세요.")
