import asyncio
import json
from typing import List, Dict, Any, Callable
from langchain_core.tools import Tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from concurrent.futures import ThreadPoolExecutor

class MCPBridge:
    """MCP 서버와 LangChain을 연결하는 브리지"""
    
    def __init__(self, server_script: str = "server.py"):
        self.server_script = server_script
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """MCP 서버에서 사용 가능한 도구들을 자동 발견"""
        server_params = StdioServerParameters(command="python", args=[self.server_script])
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                tools_response = await session.list_tools()
                
                discovered_tools = []
                for tool in tools_response.tools:
                    tool_info = {
                        'name': tool.name,
                        'description': tool.description,
                        'input_schema': tool.inputSchema
                    }
                    discovered_tools.append(tool_info)
                    
                return discovered_tools
    
    def _parse_input(self, tool_name: str, args: tuple) -> Dict[str, Any]:
        """입력 매개변수를 파싱하여 MCP 형식으로 변환"""
        if not args:
            return {}
            
        if len(args) == 1 and isinstance(args[0], str):
            input_str = args[0].strip("'\"")
            
            # 도구별 파싱 로직
            if tool_name in ["add", "multiply"]:
                try:
                    if ',' in input_str:
                        parts = input_str.split(',')
                        if tool_name == "add":
                            return {"a": int(parts[0].strip()), "b": int(parts[1].strip())}
                        else:  # multiply
                            return {"a": float(parts[0].strip()), "b": float(parts[1].strip())}
                    else:
                        parts = input_str.split()
                        if len(parts) >= 2:
                            if tool_name == "add":
                                return {"a": int(parts[0]), "b": int(parts[1])}
                            else:  # multiply
                                return {"a": float(parts[0]), "b": float(parts[1])}
                except (ValueError, IndexError):
                    pass
                    
            elif tool_name == "say_hello":
                return {"name": input_str}
                
            elif tool_name in ["square_root", "factorial"]:
                try:
                    if tool_name == "square_root":
                        return {"number": float(input_str)}
                    else:  # factorial
                        return {"n": int(input_str)}
                except ValueError:
                    pass
        
        return {}
    
    def _run_in_new_loop(self, coro):
        """새로운 이벤트 루프에서 코루틴 실행"""
        def run_in_thread():
            # 새 이벤트 루프 생성 및 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
        
        # 별도 스레드에서 실행
        future = self.executor.submit(run_in_thread)
        return future.result()
    
    def _create_mcp_caller(self, tool_name: str, input_schema: Dict) -> Callable:
        """개별 MCP 도구를 호출하는 함수 생성"""
        
        def mcp_tool_caller(*args, **kwargs) -> str:
            # 입력 파싱
            if kwargs:
                params = kwargs
            else:
                params = self._parse_input(tool_name, args)
            
            # 비동기 MCP 도구 호출
            async def call_tool():
                server_params = StdioServerParameters(command="python", args=[self.server_script])
                
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        
                        try:
                            if params:
                                result = await session.call_tool(tool_name, params)
                            else:
                                result = await session.call_tool(tool_name)
                            
                            content = result.content[0].text
                            
                            # JSON 파싱 시도
                            try:
                                parsed = json.loads(content)
                                if isinstance(parsed, dict) and "greeting" in parsed:
                                    return parsed["greeting"]
                                else:
                                    return str(parsed)
                            except json.JSONDecodeError:
                                return content
                                
                        except Exception as e:
                            return f"도구 실행 오류: {str(e)}"
            
            # 새로운 이벤트 루프에서 실행
            return self._run_in_new_loop(call_tool())
        
        return mcp_tool_caller
    
    async def create_langchain_tools(self) -> List[Tool]:
        """MCP 도구들을 LangChain Tool로 변환"""
        discovered_tools = await self.discover_tools()
        
        print(f"발견된 MCP 도구: {len(discovered_tools)}개")
        
        langchain_tools = []
        for tool_info in discovered_tools:
            tool_name = tool_info['name']
            description = tool_info['description']
            input_schema = tool_info['input_schema']
            
            print(f"  - {tool_name}: {description}")
            
            # MCP 도구 호출 함수 생성
            caller = self._create_mcp_caller(tool_name, input_schema)
            
            # LangChain Tool 생성
            langchain_tool = Tool(
                name=tool_name,
                func=caller,
                description=description
            )
            
            langchain_tools.append(langchain_tool)
            
        return langchain_tools
