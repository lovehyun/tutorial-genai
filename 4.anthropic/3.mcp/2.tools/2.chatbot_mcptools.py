# 완전 자동화된 MCP + LLM 시스템
# - 서버: 도구만 정의, 스키마 자동 생성
# - 클라이언트: 스키마 자동 가져와서 LLM과 연동

# MCP의 동작 방식
# 1. 서버: @mcp.tool() 데코레이터로 도구 등록
#    ↓
# 2. 클라이언트: session.list_tools()로 도구 스키마 자동 조회
#    ↓  
# 3. 자동 변환: MCP 스키마 → OpenAI Function Calling 형식
#    ↓
# 4. LLM: tools 매개변수를 통해 사용 가능한 도구 자동 인식
#    ↓
# 5. 자동 실행: 필요한 도구들을 자동 선택하여 실행

import asyncio
import json
import os
from dotenv import load_dotenv
import openai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

class SimpleMCPAgent:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def chat_with_tools(self, user_message: str) -> str:
        """사용자 메시지를 처리하고 필요시 MCP 도구 자동 사용"""
        server_params = StdioServerParameters(command="python", args=["server.py"])
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print(f"[User] 사용자: {user_message}")
                
                # 핵심 1: 서버에서 도구 스키마 자동 가져오기
                tools_response = await session.list_tools()
                openai_tools = []
                
                print("서버에서 발견된 도구들:")
                for tool in tools_response.tools:
                    print(f" - {tool.name}: {tool.description}")
                    
                    # 핵심 2: MCP 스키마를 OpenAI 형식으로 자동 변환
                    openai_tool = {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema
                        }
                    }
                    openai_tools.append(openai_tool)
                
                # 핵심 3: LLM에게 자동 생성된 도구 정보 전달
                response = await self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "당신은 도구를 사용할 수 있는 AI 어시스턴트입니다. 필요시 적절한 도구를 선택하여 사용하세요."
                        },
                        {
                            "role": "user", 
                            "content": user_message
                        }
                    ],
                    tools=openai_tools,  # 자동 생성된 도구들
                    tool_choice="auto"
                )
                
                message = response.choices[0].message
                
                # 도구 사용이 필요한 경우
                if message.tool_calls:
                    print(f"\nLLM이 {len(message.tool_calls)}개 도구 사용 결정:")
                    
                    tool_results = []
                    for i, tool_call in enumerate(message.tool_calls, 1):
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        
                        print(f" - 도구 {i}: {tool_name} 실행, 입력 매개변수: {tool_args}")
                        
                        # 핵심 4: MCP 도구 자동 실행
                        if tool_args:
                            result = await session.call_tool(tool_name, tool_args)
                        else:
                            result = await session.call_tool(tool_name)
                        
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_name,
                            "content": result.content[0].text
                        })
                    
                    simple_system_prompt1 = """도구 실행 결과를 바탕으로 사용자에게 도움이 되는 응답을 해주세요."""
                    simple_system_prompt2 = """
당신은 도구를 사용할 수 있는 AI 어시스턴트입니다.

사용자의 요청을 분석하여:
- 필요한 모든 작업을 파악하세요
- 여러 작업이 필요하면 해당하는 모든 도구를 사용하세요
- 도구 실행 결과를 바탕으로 완전하고 자연스러운 답변을 제공하세요

복합 요청도 한 번에 모든 필요한 도구를 사용하여 처리하세요.
"""
                    # 도구 결과를 바탕으로 최종 응답 생성
                    final_messages = [
                        {
                            "role": "system",
                            "content": simple_system_prompt1
                        },
                        {
                            "role": "user",
                            "content": user_message
                        },
                        {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": message.tool_calls
                        }
                    ] + tool_results
                    
                    print(f"\nLLM에게 전달되는 도구 결과:")
                    for result in tool_results:
                        print(f" - {result['name']}: '{result['content']}'")
                    
                    final_response = await self.client.chat.completions.create(
                        model="gpt-4",
                        messages=final_messages
                    )

                    return final_response.choices[0].message.content
                
                else:
                    # 도구 사용 없이 직접 응답
                    print(f"\n도구 사용 없이 직접 응답")
                    return message.content

async def demo():
    """간단한 데모"""
    agent = SimpleMCPAgent()
    
    test_cases = [
        "안녕하세요! 저는 John 입니다.",
        "15 더하기 25는 얼마야?", 
        "지금 몇 시인지 알려주세요",
        "안녕하세요! 그리고 100 더하기 200도 계산해주세요", # 복합 동작 처리 확인
    ]
    
    print("[ChatBot] 완전 자동화된 MCP 시스템 데모")
    print("=" * 50)
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n테스트 {i}/{len(test_cases)}")
        try:
            response = await agent.chat_with_tools(test_input)
            print(f"[ChatBot] AI: {response}")
        except Exception as e:
            print(f"[Error] 오류: {e}")
        print("-" * 30)

async def interactive():
    """대화형 모드"""
    agent = SimpleMCPAgent()
    
    print("대화형 MCP 에이전트")
    print("'quit'를 입력하면 종료됩니다")
    print("=" * 40)
    
    while True:
        try:
            user_input = input(f"\n[System] 입력: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '종료']:
                print("[System] 대화를 종료합니다!")
                break
                
            if not user_input:
                continue
                
            response = await agent.chat_with_tools(user_input)
            print(f"[ChatBot] AI: {response}")
            
        except KeyboardInterrupt:
            print(f"\n[System] 대화를 종료합니다!")
            break
        except Exception as e:
            print(f"[Error] 오류: {e}")

if __name__ == "__main__":
    print("실행 모드를 선택하세요:")
    print("1. 자동 데모")
    print("2. 대화형 모드")
    
    choice = input("선택 (1/2): ").strip()
    
    if choice == "2":
        asyncio.run(interactive())
    else:
        asyncio.run(demo())
