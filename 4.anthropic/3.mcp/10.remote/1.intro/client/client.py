# 원격 MCP 클라이언트

import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class RemoteTool:
    name: str
    description: str
    parameters: Dict[str, Any]

class RemoteMCPClient:
    """원격 MCP 서버 클라이언트"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip('/')
        self.tools: List[RemoteTool] = []
        
    async def connect(self) -> bool:
        """서버 연결 테스트"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"서버 연결 성공: {data.get('status')}")
                        return True
                    else:
                        print(f"[Error] 서버 응답 오류: {response.status}")
                        return False
        except Exception as e:
            print(f"[Error] 서버 연결 실패: {e}")
            return False
    
    async def discover_tools(self) -> List[RemoteTool]:
        """원격 서버에서 도구 목록 조회"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/tools") as response:
                    if response.status == 200:
                        tools_data = await response.json()
                        
                        self.tools = []
                        for tool_data in tools_data:
                            tool = RemoteTool(
                                name=tool_data["name"],
                                description=tool_data["description"],
                                parameters=tool_data["parameters"]
                            )
                            self.tools.append(tool)
                        
                        print(f"원격 도구 {len(self.tools)}개 발견:")
                        for tool in self.tools:
                            print(f" - {tool.name}: {tool.description}")
                        
                        return self.tools
                    else:
                        print(f"[Error] 도구 목록 조회 실패: {response.status}")
                        return []
        except Exception as e:
            print(f"[Error] 도구 발견 오류: {e}")
            return []
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any] = None) -> Any:
        """원격 도구 실행"""
        if parameters is None:
            parameters = {}
            
        try:
            payload = {
                "tool_name": tool_name,
                "parameters": parameters
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.server_url}/execute",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if result["success"]:
                            return result["result"]
                        else:
                            raise Exception(f"도구 실행 오류: {result['error']}")
                    else:
                        error_text = await response.text()
                        raise Exception(f"HTTP 오류 {response.status}: {error_text}")
                        
        except Exception as e:
            print(f"[Error] 도구 실행 실패 ({tool_name}): {e}")
            raise

# 사용 예제
async def main():
    """원격 MCP 클라이언트 데모"""
    
    # 서버 주소 설정 (환경변수 또는 기본값)
    server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
    
    print(f"원격 MCP 서버에 연결: {server_url}")
    
    # 클라이언트 생성 및 연결
    client = RemoteMCPClient(server_url)
    
    # 연결 테스트
    if not await client.connect():
        print("서버 연결에 실패했습니다. 서버가 실행 중인지 확인하세요.")
        return
    
    # 도구 목록 조회
    tools = await client.discover_tools()
    if not tools:
        print("사용 가능한 도구가 없습니다.")
        return
    
    print("\n" + "="*50)
    print("원격 도구 테스트 시작")
    print("="*50)
    
    # 각 도구 테스트
    test_cases = [
        ("hello", {"name": "Remote User"}),
        ("add", {"a": 15, "b": 25}),
        ("current_time", {}),
        ("weather", {"city": "Seoul"}),
        ("hello", {}),  # 기본값 테스트
    ]
    
    for i, (tool_name, params) in enumerate(test_cases, 1):
        print(f"\n테스트 {i}/{len(test_cases)}")
        print(f"도구: {tool_name}")
        print(f"매개변수: {params}")
        
        try:
            result = await client.call_tool(tool_name, params)
            print(f"결과: {result}")
        except Exception as e:
            print(f"[Error] 오류: {e}")
        
        print("-" * 40)

# 대화형 테스트
async def interactive_test():
    """대화형 원격 도구 테스트"""
    server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
    client = RemoteMCPClient(server_url)
    
    if not await client.connect():
        return
    
    tools = await client.discover_tools()
    if not tools:
        return
    
    print("\n대화형 원격 도구 테스트")
    print("사용 가능한 도구:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    print("\n명령어:")
    print(" - hello Alice")
    print(" - add 10 20") 
    print(" - time")
    print(" - weather Seoul")
    print(" - quit")
    print("-" * 40)
    
    while True:
        try:
            user_input = input("\n[User] 명령어: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '종료']:
                print("[Server] 테스트를 종료합니다!")
                break
            
            if not user_input:
                continue
            
            # 간단한 명령어 파싱
            parts = user_input.split()
            if not parts:
                continue
                
            cmd = parts[0].lower()
            
            if cmd == "hello":
                name = parts[1] if len(parts) > 1 else "World"
                result = await client.call_tool("hello", {"name": name})
                print(f"[ChatBot] {result}")
                
            elif cmd == "add":
                if len(parts) >= 3:
                    try:
                        a, b = float(parts[1]), float(parts[2])
                        result = await client.call_tool("add", {"a": a, "b": b})
                        print(f"[ChatBot] {a} + {b} = {result}")
                    except ValueError:
                        print("[Error] 숫자를 입력해주세요")
                else:
                    print("[Error] 사용법: add 숫자1 숫자2")
                    
            elif cmd == "time":
                result = await client.call_tool("current_time")
                print(f"[ChatBot] {result}")
                
            elif cmd == "weather":
                city = parts[1] if len(parts) > 1 else "Seoul"
                result = await client.call_tool("weather", {"city": city})
                print(f"[ChatBot] {city} 날씨: {result}")
                
            else:
                print(f"[Error] 알 수 없는 명령어: {cmd}")
                
        except KeyboardInterrupt:
            print("\n[Server] 테스트를 종료합니다!")
            break
        except Exception as e:
            print(f"[Error] 오류: {e}")

if __name__ == "__main__":
    print("테스트 모드를 선택하세요:")
    print("1. 자동 테스트")
    print("2. 대화형 테스트")
    
    choice = input("선택 (1/2): ").strip()
    
    if choice == "2":
        asyncio.run(interactive_test())
    else:
        asyncio.run(main())
