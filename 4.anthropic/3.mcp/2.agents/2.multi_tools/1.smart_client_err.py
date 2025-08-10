import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def get_tools_from_server(server_file):
    """서버에서 도구 목록 가져오기"""
    server_params = StdioServerParameters(command="python", args=[server_file])
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            tools_result = await session.list_tools()
            tools = {}
            for tool in tools_result.tools:
                tools[tool.name] = tool.description
            
            return session, tools

def find_best_tool(question, all_tools):
    """질문에 가장 적합한 도구 찾기"""
    question = question.lower()
    
    for tool_name, description in all_tools.items():
        # 도구 이름이나 설명에서 키워드 매칭
        if any(word in question for word in ["안녕", "hello"]) and "hello" in tool_name:
            return tool_name
        if any(word in question for word in ["더하기", "계산", "+"]) and "add" in tool_name:
            return tool_name
        if any(word in question for word in ["시간", "몇 시"]) and "time" in tool_name:
            return tool_name
        if any(word in question for word in ["날씨"]) and "weather" in tool_name:
            return tool_name
    
    return None

def extract_params(question, tool_name):
    """질문에서 매개변수 추출"""
    params = {}
    
    if "hello" in tool_name:
        words = question.split()
        for word in words:
            if word.istitle():
                params["name"] = word
                break
    
    elif "add" in tool_name:
        import re
        numbers = re.findall(r'\d+', question)
        if len(numbers) >= 2:
            params["a"] = float(numbers[0])
            params["b"] = float(numbers[1])
    
    elif "weather" in tool_name:
        cities = ["서울", "부산", "대구"]
        for city in cities:
            if city in question:
                params["city"] = city
                break
    
    return params

async def main():
    """메인 실행"""
    # 1. 서버들에서 도구 목록 수집
    servers = ["math_server.py", "utility_server.py"]
    all_sessions = []
    all_tools = {}
    
    for server_file in servers:
        try:
            session, tools = await get_tools_from_server(server_file)
            all_sessions.append(session)
            all_tools.update(tools)
            print(f"{server_file}: {list(tools.keys())}")
        except:
            print(f"{server_file}: 연결 실패")
    
    print(f"전체 도구: {list(all_tools.keys())}")
    print("-" * 30)
    
    # 2. 질문들 처리
    questions = [
        "안녕하세요 Alice!",
        "5 더하기 7은?",
        "지금 몇 시야?", 
        "서울 날씨는?",
        "파일 삭제해줘"
    ]
    
    for question in questions:
        print(f"질문: {question}")
        
        # 3. 적합한 도구 찾기
        tool_name = find_best_tool(question, all_tools)
        
        if tool_name:
            # 4. 매개변수 추출하고 실행
            params = extract_params(question, tool_name)
            
            # 어느 서버에서든 실행 시도
            for session in all_sessions:
                try:
                    result = await session.call_tool(tool_name, params)
                    print(f"답변: {result.content[0].text}")
                    break
                except:
                    continue
            else:
                print("답변: 실행 실패")
        else:
            print("답변: 적합한 도구 없음")
        
        print()

if __name__ == "__main__":
    asyncio.run(main())
