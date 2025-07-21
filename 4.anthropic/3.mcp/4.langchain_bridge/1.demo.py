import asyncio
from agent import MCPAgent

async def automated_demo():
    """자동화된 데모"""
    agent = MCPAgent("server.py")
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
    
    print("MCP Bridge 기반 Agent 데모")
    print("=" * 50)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n테스트 {i}/{len(test_cases)}")
        print(f"사용자: {test}")
        
        try:
            response = agent.run(test)
            print(f"AI: {response}")
        except Exception as e:
            print(f"오류: {e}")
        
        print("-" * 40)

async def interactive_demo():
    """대화형 데모"""
    agent = MCPAgent("server.py")
    await agent.initialize()
    
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
                
            response = agent.run(user_input)
            print(f"AI: {response}")
            
        except KeyboardInterrupt:
            print("\n대화를 종료합니다!")
            break
        except Exception as e:
            print(f"오류: {e}")

if __name__ == "__main__":
    print("실행 모드를 선택하세요:")
    print("1. 자동 데모")
    print("2. 대화형 모드")
    
    choice = input("선택 (1/2): ").strip()
    
    if choice == "2":
        asyncio.run(interactive_demo())
    else:
        asyncio.run(automated_demo())
