import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 인코딩 환경변수 설정 (한글 이슈)
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUNBUFFERED'] = '1'

async def main():
    # 프록시를 통해 서버에 연결
    server_params = StdioServerParameters(
        command="python", 
        # args=["simple_server2.py"]
        args=["debug_proxy.py", "simple_server2.py"],
        env={  # 한글 이슈
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1"
        }
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 서버 연결 및 초기화
            print("서버 연결 중...")
            init_result = await session.initialize()
            print(f"연결 완료: {init_result.serverInfo.name}")
            
            # 1. 서버에 어떤 도구들이 있는지 확인
            print("\n=== 사용 가능한 도구들 ===")
            tools = await session.list_tools()
            if tools.tools:
                for tool in tools.tools:
                    print(f" - {tool.name}: {tool.description}")
            else:
                print("도구가 없습니다.")
            
            # 2. 서버에 어떤 리소스들이 있는지 확인  
            print("\n=== 사용 가능한 리소스들 ===")
            resources = await session.list_resources()
            if resources.resources:
                for resource in resources.resources:
                    print(f" - {resource.name}: {resource.description}")
            else:
                print("리소스가 없습니다.")
            
            # 3. 서버에 어떤 프롬프트들이 있는지 확인
            print("\n=== 사용 가능한 프롬프트들 ===")
            prompts = await session.list_prompts()
            if prompts.prompts:
                for prompt in prompts.prompts:
                    print(f" - {prompt.name}: {prompt.description}")
            else:
                print("프롬프트가 없습니다.")

            # 4. 첫 번째 도구가 있다면 한 번 호출해보기
            print("\n=== 도구 테스트 ===")
            tools = await session.list_tools()
            if tools.tools:
                first_tool = tools.tools[0]
                print(f"'{first_tool.name}' 도구 테스트 중...")
                
                # 간단한 테스트 인자로 호출
                test_args = {"name": "테스트"} if "name" in str(first_tool.inputSchema) else {}
                result = await session.call_tool(first_tool.name, test_args)
                print(f"결과: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
