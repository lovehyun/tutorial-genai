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

class SimpleAIAgent:
    def __init__(self, session):
        self.session = session
        self.tools = {}
        self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def load_tools(self):
        """서버에서 사용 가능한 도구 목록 가져오기"""
        tools_response = await self.session.list_tools()
        for tool in tools_response.tools:
            self.tools[tool.name] = tool
        print(f"로드된 도구: {list(self.tools.keys())}")
    
    def _convert_tools_to_openai_format(self):
        """MCP 도구를 OpenAI Function Calling 형식으로 변환"""
        openai_tools = []
        for tool_name, tool in self.tools.items():
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
            openai_tools.append(openai_tool)
        return openai_tools
    
    async def analyze_and_select_tool(self, user_input):
        """ChatGPT API를 사용하여 사용자 입력 분석 후 도구 선택"""
        if not self.tools:
            return None, {}
        
        # OpenAI Function Calling 형식으로 변환
        openai_tools = self._convert_tools_to_openai_format()
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "사용자의 요청에 따라 적절한 도구를 선택하세요. 도구가 필요하지 않다면 도구를 호출하지 마세요."
                },
                {
                    "role": "user", 
                    "content": user_input
                }
            ],
            tools=openai_tools,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        # 도구 호출이 있는 경우
        if message.tool_calls:
            tool_call = message.tool_calls[0]  # 첫 번째 도구 호출만 사용
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            return tool_name, tool_args
        else:
            # 도구 호출 없음
            return None, {}
                
    async def process_request(self, user_input):
        """사용자 요청 처리"""
        print(f"\n사용자: {user_input}")
        
        # 1. GPT로 도구 선택
        tool_name, params = await self.analyze_and_select_tool(user_input)
        
        if not tool_name or tool_name not in self.tools:
            # GPT가 직접 응답하게 하기
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "사용자와 자연스럽게 대화하세요. 도구가 필요하지 않은 일반적인 대화에 응답하세요."
                    },
                    {
                        "role": "user", 
                        "content": user_input
                    }
                ]
            )
            return response.choices[0].message.content
        
        print(f"선택된 도구: {tool_name}, 매개변수: {params}")
        
        # 2. 도구 실행
        if params:
            result = await self.session.call_tool(tool_name, params)
        else:
            result = await self.session.call_tool(tool_name)
        
        # 3. 도구 결과를 GPT로 자연스럽게 포맷팅
        formatted_response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"도구 '{tool_name}'의 실행 결과를 사용자에게 자연스럽고 도움이 되도록 설명해주세요."
                },
                {
                    "role": "user", 
                    "content": f"사용자 요청: {user_input}\n도구 실행 결과: {result.content[0].text}"
                }
            ]
        )
        return formatted_response.choices[0].message.content
                
async def main():
    """메인 실행 함수"""
    # server_params = StdioServerParameters(command="python", args=["server.py"])
    server_params = StdioServerParameters(command="python", args=["server2.py"])
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # AI 에이전트 생성 및 초기화
            agent = SimpleAIAgent(session)
            await agent.load_tools()
            
            print("\n" + "=" * 40)
            print("GPT 기반 AI 에이전트 테스트")
            print("=" * 40)
            
            # 테스트 케이스
            test_cases = [
                "안녕하세요 Alice!",
                "안녕하세요 저는 홍길동 입니다.",
                "5 더하기 3은 얼마야?",
                "지금 몇 시야?",
                "이해할 수 없는 요청",
                "오늘 날씨는 어때요?",  # 도구 없는 일반 대화
                "15 곱하기 7은?"  # 새로운 계산
            ]
            
            for user_input in test_cases:
                response = await agent.process_request(user_input)
                print(f"AI: {response}")
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
