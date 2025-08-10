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
                
                print(f"사용자: {user_message}")
                
                # 1. 서버에서 도구 스키마 자동 가져오기
                tools_response = await session.list_tools()
                openai_tools = []
                
                for tool in tools_response.tools:
                    # 2. MCP 스키마를 OpenAI 형식으로 자동 변환
                    openai_tool = {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema
                        }
                    }
                    openai_tools.append(openai_tool)
                
                # 3. LLM에게 자동 생성된 도구 정보 전달
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
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
                    tools=openai_tools,
                    tool_choice="auto"
                )
                
                message = response.choices[0].message
                
                # 도구 사용이 필요한 경우
                if message.tool_calls:
                    print(f"선택된 도구: {[call.function.name for call in message.tool_calls]}")
                    
                    tool_results = []
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        
                        # 4. MCP 도구 자동 실행
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
                    
                    # 도구 결과를 바탕으로 최종 응답 생성
                    final_messages = [
                        {"role": "system", "content": "도구 실행 결과를 바탕으로 사용자에게 도움이 되는 응답을 해주세요."},
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": None, "tool_calls": message.tool_calls}
                    ] + tool_results
                    
                    final_response = await self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=final_messages
                    )

                    return final_response.choices[0].message.content
                
                else:
                    # 도구 사용 없이 직접 응답
                    return message.content

async def main():
    """간단한 테스트"""
    agent = SimpleMCPAgent()
    
    test_cases = [
        "안녕하세요! 저는 Alice입니다.",
        "15 더하기 25는 얼마야?",
        "지금 시간 알려주세요"
    ]
    
    print("GPT 기반 MCP 에이전트 테스트")
    print("=" * 40)
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n테스트 {i}: {test_input}")
        try:
            response = await agent.chat_with_tools(test_input)
            print(f"AI: {response}")
        except Exception as e:
            print(f"오류: {e}")
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(main())


# # MCP 서버의 도구 정보
# tool.name = "add"
# tool.description = "두 정수의 덧셈을 수행하는 계산기 도구"
# tool.inputSchema = {
#     "type": "object",
#     "properties": {
#         "a": {"type": "integer", "description": "첫 번째 숫자"},
#         "b": {"type": "integer", "description": "두 번째 숫자"}
#     },
#     "required": ["a", "b"]
# }
#
# # ↓ 변환 ↓
#
# # OpenAI Function Calling 형식
# openai_tool = {
#     "type": "function",
#     "function": {
#         "name": "add",
#         "description": "두 정수의 덧셈을 수행하는 계산기 도구",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "a": {"type": "integer", "description": "첫 번째 숫자"},
#                 "b": {"type": "integer", "description": "두 번째 숫자"}
#             },
#             "required": ["a", "b"]
#         }
#     }
# }
