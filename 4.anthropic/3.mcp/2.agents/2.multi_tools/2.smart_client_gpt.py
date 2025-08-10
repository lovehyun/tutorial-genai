import asyncio
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# .env 파일 로드
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def format_tool_info_detailed(tool, show_params=True):
    """도구 정보를 상세하게 포맷팅하여 반환"""
    result = f"  - {tool.name}: {tool.description or '설명 없음'}"
    
    if not show_params:
        return result
    
    # 매개변수 정보 추가
    if tool.inputSchema and 'properties' in tool.inputSchema:
        properties = tool.inputSchema['properties']
        required = tool.inputSchema.get('required', [])
        result += "\n    매개변수:"
        
        for param_name, param_info in properties.items():
            param_type = param_info.get('type', 'unknown')
            param_desc = param_info.get('description', '')
            is_required = param_name in required
            required_mark = "(필수)" if is_required else "(선택)"
            desc_text = f" - {param_desc}" if param_desc else ""
            result += f"\n      {param_name}: {param_type} {required_mark}{desc_text}"
    else:
        result += "\n    매개변수: 없음"
    
    return result

def format_tool_info_simple(name, tool_info):
    """도구 정보를 간단하게 포맷팅하여 반환 (GPT 프롬프트용)"""
    # 매개변수 목록 추출
    param_list = []
    if tool_info['schema'] and 'properties' in tool_info['schema']:
        param_list = list(tool_info['schema']['properties'].keys())
    
    param_text = f"매개변수: {param_list}" if param_list else "매개변수: 없음"
    return f"- {name}: {tool_info['description']} ({param_text})"

async def get_tools_from_servers(server_files):
    """서버들에서 도구 정보 수집"""
    tools = {}
    for server_file in server_files:
        try:
            server_params = StdioServerParameters(command="python", args=[server_file])
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_result = await session.list_tools()
                    
                    print(f"\n{server_file}에서 발견된 도구들:")
                    for tool in tools_result.tools:
                        tools[tool.name] = {
                            "description": tool.description or "",
                            "schema": tool.inputSchema,
                            "server": server_file
                        }
                        
                        # 상세한 도구 정보 출력
                        print(format_tool_info_detailed(tool))
                        
                    # 요약된 정보만...
                    # print(f"{server_file}: {[t.name for t in tools_result.tools]}")
                    
        except Exception as e:
            print(f"{server_file} 실패: {e}")
    return tools

async def ask_gpt(user_request, tools):
    """GPT에게 도구 선택 요청"""
    # GPT 프롬프트용 도구 정보 생성
    tools_info = "\n".join([
        format_tool_info_simple(name, info) 
        for name, info in tools.items()
    ])
    
    prompt = f"""사용 가능한 도구:
{tools_info}

사용자 요청: {user_request}

적절한 도구와 매개변수를 JSON으로 반환하세요:
{{"tool": "도구명", "params": {{"매개변수": "값"}}, "reason": "이유"}}
적합한 도구가 없으면: {{"tool": null, "params": {{}}, "reason": "이유"}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content.strip())
    
    except Exception as e:
        return {"tool": None, "params": {}, "reason": f"GPT 오류: {e}"}

async def execute_tool(tool_name, params, tools):
    """도구 실행"""
    if tool_name not in tools:
        return "도구를 찾을 수 없습니다"
    
    server_file = tools[tool_name]["server"]
    try:
        server_params = StdioServerParameters(command="python", args=[server_file])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, params)
                return result.content[0].text
    except Exception as e:
        return f"실행 실패: {e}"

async def process_request(user_request, tools):
    """요청 처리"""
    print(f"\n---\n[요청] {user_request}")
    
    # GPT 분석
    analysis = await ask_gpt(user_request, tools)
    print(f"[GPT 분석중] 도구: {analysis['tool']}, 인자: {analysis['params']}, 이유: {analysis['reason']}")
    
    # 도구 실행
    if analysis['tool']:
        result = await execute_tool(analysis['tool'], analysis['params'], tools)
        print(f"[실행 결과] {result}")
    else:
        print(f"[실행 결과] {analysis['reason']}")

async def main():
    """메인 실행"""
    print("GPT-MCP 클라이언트 시작")
    
    # 도구 수집
    tools = await get_tools_from_servers(["math_server.py", "utility_server.py"])
    print(f"\n총 {len(tools)}개 도구 발견")
    
    # 테스트 요청들
    requests = [
        "안녕하세요 Alice!",  # math 서버의 hello
        "15 더하기 25는?",    # math 서버의 add
        "지금 몇 시?",        # utility 서버의 current_time
        "부산 날씨는?",       # utility 서버의 weather
        "제주 날씨는?",       # utility 서버의 weather
        "파일 삭제해줘"       # 도구 없음
    ]
    
    for request in requests:
        await process_request(request, tools)

if __name__ == "__main__":
    asyncio.run(main())
