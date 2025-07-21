# 완전히 수정된 demo.py

import asyncio
import warnings
from agent2 import MCPAgent, LegacyMCPAgent

# 경고 전체 억제
warnings.filterwarnings("ignore")

async def langgraph_demo():
    """LangGraph 기반 데모 (권장)"""
    try:
        agent = MCPAgent("server.py")
        await agent.initialize()
        
        test_cases = [
            "Alice에게 인사해줘",
            "15 더하기 25는 얼마야?",
            "3.5 곱하기 2.8은?",
            "지금 몇 시야?",
            "16의 제곱근은?",
            "5 팩토리얼은?",
            "Bob에게 인사하고 10 더하기 20도 계산해줘"
        ]
        
        print("LangGraph 기반 MCP Agent 데모")
        print("=" * 50)
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n테스트 {i}/{len(test_cases)}")
            print(f"사용자: {test}")
            
            try:
                # 비동기로 실행
                response = await agent.run(test)
                print(f"AI: {response}")
            except Exception as e:
                print(f"오류: {e}")
            
            print("-" * 40)
            
    except Exception as e:
        print(f"LangGraph 데모 초기화 오류: {e}")
        print("langgraph 패키지를 설치해주세요: pip install langgraph")

def legacy_demo_sync():
    """완전 동기 Legacy 데모"""
    async def init_agent():
        agent = LegacyMCPAgent("server.py")
        await agent.initialize()
        return agent
    
    # 초기화만 비동기로 실행
    agent = asyncio.run(init_agent())
    
    test_cases = [
        "Alice에게 인사해줘",
        "15 더하기 25는 얼마야?",
        "지금 몇 시야?",
        "Bob에게 인사하고 10 더하기 20도 계산해줘"
    ]
    
    print("레거시 Agent 데모 (완전 동기)")
    print("=" * 40)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n테스트 {i}/{len(test_cases)}")
        print(f"사용자: {test}")
        
        try:
            # 완전 동기 실행 (await 절대 사용 안함)
            response = agent.run(test)
            print(f"AI: {response}")
        except Exception as e:
            print(f"오류: {e}")
        
        print("-" * 40)

async def interactive_demo():
    """대화형 데모"""
    print("Agent 타입을 선택하세요:")
    print("1. LangGraph (권장)")
    print("2. Legacy (경고 없음)")
    
    agent_choice = input("선택 (1/2): ").strip()
    
    if agent_choice == "2":
        # Legacy Agent는 초기화만 비동기
        agent = LegacyMCPAgent("server.py")
        await agent.initialize()
        is_async = False
        print("Legacy Agent 선택됨 (동기 실행)")
    else:
        # LangGraph Agent는 완전 비동기
        try:
            agent = MCPAgent("server.py")
            await agent.initialize()
            is_async = True
            print("LangGraph Agent 선택됨 (비동기 실행)")
        except Exception as e:
            print(f"LangGraph 초기화 실패: {e}")
            print("Legacy Agent로 대체합니다...")
            agent = LegacyMCPAgent("server.py")
            await agent.initialize()
            is_async = False
    
    print("\nMCP Bridge 대화형 Agent")
    print("'quit'를 입력하면 종료됩니다")
    print("=" * 40)
    
    while True:
        try:
            user_input = input("\n사용자: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '종료']:
                print("대화를 종료합니다!")
                break
                
            if not user_input:
                continue
            
            # 명확한 동기/비동기 구분
            if is_async:
                response = await agent.run(user_input)  # LangGraph
            else:
                response = agent.run(user_input)        # Legacy (동기)
                
            print(f"AI: {response}")
            
        except KeyboardInterrupt:
            print("\n대화를 종료합니다!")
            break
        except Exception as e:
            print(f"오류: {e}")

def simple_test():
    """가장 간단한 테스트"""
    async def run_test():
        agent = LegacyMCPAgent("server.py")
        await agent.initialize()
        
        print("간단한 테스트")
        print("-" * 20)
        
        # 동기 실행
        response = agent.run("Alice에게 인사해줘")
        print(f"결과: {response}")
    
    asyncio.run(run_test())

if __name__ == "__main__":
    print("실행 모드를 선택하세요:")
    print("1. LangGraph 데모 (권장)")
    print("2. Legacy 데모 (동기)")
    print("3. 대화형 모드")
    print("4. 간단한 테스트")
    
    choice = input("선택 (1/2/3/4): ").strip()
    
    if choice == "2":
        legacy_demo_sync()  # 완전 동기 실행
    elif choice == "3":
        asyncio.run(interactive_demo())
    elif choice == "4":
        simple_test()
    else:
        asyncio.run(langgraph_demo())
