import asyncio
import re
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class SimpleAIAgent:
    def __init__(self, session):
        self.session = session
        self.tools = {}
    
    async def load_tools(self):
        """서버에서 사용 가능한 도구 목록 가져오기"""
        tools_response = await self.session.list_tools()
        for tool in tools_response.tools:
            self.tools[tool.name] = tool
        print(f"로드된 도구: {list(self.tools.keys())}")
    
    def analyze_and_select_tool(self, user_input):
        """사용자 입력 분석해서 도구 선택"""
        # 인사 패턴
        if any(word in user_input for word in ["안녕", "hello", "hi"]):
            # 이름 추출 (대문자로 시작하는 단어)
            name_match = re.search(r'([A-Z][a-z]+)', user_input)
            name = name_match.group(1) if name_match else "None"  # group(0) 은 전체, group(1)은 첫번째 ()매치, group(2)는 두번째 ()매치 등
            return "hello", {"name": name}
        
        # 덧셈 패턴
        elif any(word in user_input for word in ["더하기", "+", "덧셈"]):
            # 숫자 추출
            numbers = re.findall(r'\d+', user_input)  # 숫자 문자열 리스트를 반환함 ['5', '10']
            if len(numbers) >= 2:
                return "add", {"a": int(numbers[0]), "b": int(numbers[1])}
        
        # 시간 패턴
        elif any(word in user_input for word in ["시간", "몇 시", "지금"]):
            return "now", {}
        
        return None, {}
    
    async def process_request(self, user_input):
        """사용자 요청 처리"""
        print(f"\n사용자: {user_input}")
        
        # 1. 도구 선택
        tool_name, params = self.analyze_and_select_tool(user_input)
        
        if not tool_name or tool_name not in self.tools:
            return "요청을 이해하지 못했습니다."
        
        print(f"선택된 도구: {tool_name}, 매개변수: {params}")
        
        # 2. 도구 실행
        if params:
            result = await self.session.call_tool(tool_name, params)
        else:
            result = await self.session.call_tool(tool_name)
        
        return result.content[0].text
            
async def main():
    """메인 실행 함수"""
    server_params = StdioServerParameters(command="python", args=["server.py"])
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # AI 에이전트 생성 및 초기화
            agent = SimpleAIAgent(session)
            await agent.load_tools()
            
            print("\n" + "=" * 40)
            print("간단한 AI 에이전트 테스트")
            print("=" * 40)
            
            # 테스트 케이스
            test_cases = [
                "안녕하세요 Alice!",
                "안녕하세요 저는 홍길동 입니다.",
                "5 더하기 3은 얼마야?",
                "지금 몇 시야?",
                "이해할 수 없는 요청"
            ]
            
            for user_input in test_cases:
                response = await agent.process_request(user_input)
                print(f"AI: {response}")
                print("-" * 30)

if __name__ == "__main__":
    asyncio.run(main())
