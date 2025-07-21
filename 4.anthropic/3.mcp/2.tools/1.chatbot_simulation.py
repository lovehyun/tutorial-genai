# AI 에이전트가 자동으로 도구를 선택하고 실행하는 시스템

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class AIAgent:
    def __init__(self, session):
        self.session = session
        self.available_tools = {}
        
    async def initialize(self):
        """서버로부터 사용 가능한 도구 목록을 가져옴"""
        # 실제로는 session.list_tools() 같은 메서드로 도구 목록 조회
        self.available_tools = {
            "hello": "인사말 생성 (매개변수: name)",
            "add": "두 숫자 덧셈 (매개변수: a, b)", 
            "now": "현재 시간 조회 (매개변수 없음)",
            "weather": "날씨 정보 조회 (매개변수: city)",
            "calculate": "복잡한 수학 계산 (매개변수: expression)",
            "search_web": "웹 검색 (매개변수: query)",
            "send_email": "이메일 발송 (매개변수: to, subject, body)"
        }
    
    def analyze_user_intent(self, user_input: str) -> dict:
        """사용자 입력을 분석하여 필요한 도구와 매개변수 결정"""
        user_input = user_input.lower()
        
        # 실제로는 LLM이나 NLP 모델을 사용하여 의도 분석
        if any(word in user_input for word in ["안녕", "hello", "hi", "인사"]):
            # "안녕하세요 John!" → hello 도구 필요
            name = self._extract_name(user_input)
            return {"tool": "hello", "params": {"name": name}}
            
        elif any(word in user_input for word in ["더하기", "+", "덧셈", "합계", "계산"]):
            # "5 더하기 7은?" → add 도구 필요
            numbers = self._extract_numbers(user_input)
            if len(numbers) >= 2:
                return {"tool": "add", "params": {"a": numbers[0], "b": numbers[1]}}
                
        elif any(word in user_input for word in ["시간", "몇 시", "현재", "지금"]):
            # "지금 몇 시야?" → now 도구 필요
            return {"tool": "now", "params": {}}
            
        elif any(word in user_input for word in ["날씨", "기온", "weather"]):
            # "서울 날씨 어때?" → weather 도구 필요
            city = self._extract_city(user_input)
            return {"tool": "weather", "params": {"city": city}}
            
        elif any(word in user_input for word in ["검색", "찾아", "search"]):
            # "파이썬 튜토리얼 검색해줘" → search_web 도구 필요
            query = self._extract_search_query(user_input)
            return {"tool": "search_web", "params": {"query": query}}
            
        return {"tool": None, "params": {}}
    
    def _extract_name(self, text: str) -> str:
        # 간단한 이름 추출 로직 (실제로는 더 정교한 NER 사용)
        words = text.split()
        for word in words:
            if word.istitle() and word.isalpha():
                return word
        return "World"
    
    def _extract_numbers(self, text: str) -> list:
        # 숫자 추출 로직
        import re
        numbers = re.findall(r'\d+', text)
        return [int(n) for n in numbers]
    
    def _extract_city(self, text: str) -> str:
        # 도시명 추출 로직
        cities = ["서울", "부산", "대구", "인천", "대전", "광주", "울산", "제주"]
        for city in cities:
            if city in text:
                return city
        return "서울"
    
    def _extract_search_query(self, text: str) -> str:
        # 검색 쿼리 추출 로직
        stop_words = ["검색해줘", "찾아줘", "알려줘", "검색", "찾아"]
        for stop_word in stop_words:
            text = text.replace(stop_word, "").strip()
        return text
    
    async def process_user_input(self, user_input: str) -> str:
        """사용자 입력을 처리하여 적절한 응답 생성"""
        print(f"[ChatBot] 사용자 입력 분석 중: '{user_input}'")
        
        # 1. 사용자 의도 분석
        intent = self.analyze_user_intent(user_input)
        
        if intent["tool"] is None:
            return "죄송합니다. 요청을 이해하지 못했습니다."
        
        tool_name = intent["tool"]
        params = intent["params"]
        
        print(f"선택된 도구: {tool_name}")
        print(f"매개변수: {params}")
        
        try:
            # 2. 선택된 도구 자동 실행
            if params:
                result = await self.session.call_tool(tool_name, params)
            else:
                result = await self.session.call_tool(tool_name)
            
            # 3. 결과를 자연어로 변환
            tool_output = result.content[0].text
            response = self.format_response(user_input, tool_name, tool_output)
            
            return response
            
        except Exception as e:
            return f"도구 실행 중 오류가 발생했습니다: {e}"
    
    def format_response(self, user_input: str, tool_name: str, tool_output: str) -> str:
        """도구 실행 결과를 자연스러운 응답으로 변환"""
        if tool_name == "hello":
            return f"{tool_output} 만나서 반가워요!"
        elif tool_name == "add":
            return f"계산 결과는 {tool_output}입니다."
        elif tool_name == "now":
            return tool_output
        elif tool_name == "weather":
            return f"요청하신 날씨 정보입니다: {tool_output}"
        elif tool_name == "search_web":
            return f"검색 결과를 찾았습니다: {tool_output}"
        else:
            return tool_output

async def simulate_conversation():
    """실제 대화 시뮬레이션"""
    server_params = StdioServerParameters(command="python", args=["server.py"])
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # AI 에이전트 초기화
            agent = AIAgent(session)
            await agent.initialize()
            
            print("[ChatBot] AI 에이전트가 준비되었습니다!")
            print("=" * 50)
            
            # 다양한 사용자 입력 시뮬레이션
            test_inputs = [
                "안녕하세요 Alice!",
                "5 더하기 3은 얼마야?", 
                "지금 몇 시야?",
                "25 곱하기 4는?",  # 현재 서버에 없는 도구
            ]
            
            for user_input in test_inputs:
                print(f"\n[User] 사용자: {user_input}")
                response = await agent.process_user_input(user_input)
                print(f"[ChatBot] AI: {response}")
                print("-" * 30)

if __name__ == "__main__":
    asyncio.run(simulate_conversation())
