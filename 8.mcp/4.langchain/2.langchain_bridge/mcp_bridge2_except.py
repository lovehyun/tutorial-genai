import asyncio
import json
import logging
from typing import List, Dict, Any, Callable, Optional

from langchain_core.tools import Tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 로깅을 파일로 설정 (UTF-8 인코딩)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_bridge.log', encoding='utf-8'),
        logging.StreamHandler()  # 콘솔에도 출력
    ]
)
logger = logging.getLogger(__name__)

class MCPBridge:
    """MCP 서버와 LangChain을 연결하는 간단한 브리지"""
    
    def __init__(self, server_script: str = "server.py"):
        self.server_script = server_script
        self.server_params = StdioServerParameters(command="python", args=[self.server_script])
        self._discovered_tools: List[Dict[str, Any]] = []  # 기존 파일 스타일로 변경
        self._tool_schemas: Dict[str, Dict] = {}           # 스키마 분리 저장
        
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """MCP 서버에서 도구들을 발견"""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_response = await session.list_tools()
                
                self._discovered_tools = []
                for tool in tools_response.tools:
                    tool_info = {
                        'name': tool.name,
                        'description': tool.description,
                        'input_schema': tool.inputSchema  # 기존 파일 스타일
                    }
                    self._discovered_tools.append(tool_info)
                    
                    # 스키마 분리 저장 (기존 파일 방식)
                    self._tool_schemas[tool.name] = tool.inputSchema
                    
                    logger.info(f"도구 발견: {tool.name} - {tool.description}")
                
                return self._discovered_tools
    
    def _parse_input_from_schema(self, tool_name: str, input_str: str) -> Dict[str, Any]:
        """스키마 기반 동적 입력 파싱 (기존 파일 방식)"""
        schema = self._tool_schemas.get(tool_name, {})
        properties = schema.get('properties', {})
        if not input_str.strip():
            return {}
        
        # JSON 형태인지 확인
        try:
            return json.loads(input_str)
        except json.JSONDecodeError:
            pass
        
        # 스키마에서 파라미터 정보 가져오기
        tool_schema = None
        for tool in self._tools:
            if tool['name'] == tool_name:
                tool_schema = tool['schema']
                break
        
        if not tool_schema or 'properties' not in tool_schema:
            return {}
        
        properties = tool_schema['properties']
        result = {}
        input_str = input_str.strip("'\"")
        
        # 단일 파라미터
        if len(properties) == 1:
            param_name = list(properties.keys())[0]
            param_type = properties[param_name].get('type', 'string')
            
            if param_type == 'integer':
                try:
                    result[param_name] = int(input_str)
                except ValueError:
                    result[param_name] = input_str
            elif param_type == 'number':
                try:
                    result[param_name] = float(input_str)
                except ValueError:
                    result[param_name] = input_str
            else:
                result[param_name] = input_str
        
        # 복수 파라미터 (콤마로 분리)
        elif len(properties) > 1:
            parts = [p.strip() for p in input_str.split(',')]
            param_names = list(properties.keys())
            
            for i, part in enumerate(parts):
                if i < len(param_names):
                    param_name = param_names[i]
                    param_type = properties[param_name].get('type', 'string')
                    
                    if param_type == 'integer':
                        try:
                            result[param_name] = int(part)
                        except ValueError:
                            result[param_name] = part
                    elif param_type == 'number':
                        try:
                            result[param_name] = float(part)
                        except ValueError:
                            result[param_name] = part
                    else:
                        result[param_name] = part
        
        return result
    
    async def _call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> str:
        """MCP 도구 호출 (기존 파일 방식)"""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # 도구 호출
                if params:
                    result = await session.call_tool(tool_name, params)
                else:
                    result = await session.call_tool(tool_name)
                
                if result.content and len(result.content) > 0:
                    content = result.content[0].text
                    
                    # JSON 파싱 시도
                    try:
                        parsed = json.loads(content)
                        if isinstance(parsed, dict) and "greeting" in parsed:
                            return parsed["greeting"]
                        return str(parsed)
                    except json.JSONDecodeError:
                        return content
                
                return "도구 실행 완료 (결과 없음)"
    
    def _create_tool_caller(self, tool_name: str) -> Callable:
        """도구 호출 함수 생성"""
        def tool_caller(input_str: str = "") -> str:
            params = self._parse_input(tool_name, input_str)
            logger.debug(f"{tool_name} 호출: {params}")
            
            try:
                # 이벤트 루프 확인 후 실행
                try:
                    loop = asyncio.get_running_loop()
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._call_tool(tool_name, params))
                        return future.result(timeout=10)
                except RuntimeError:
                    return asyncio.run(self._call_tool(tool_name, params))
            except Exception as e:
                logger.error(f"{tool_name} 호출 오류: {e}")
                return f"오류: {str(e)}"
        
        return tool_caller
    
    async def create_langchain_tools(self) -> List[Tool]:
        """LangChain Tool 생성"""
        if not self._discovered_tools:
            await self.discover_tools()
        
        if not self._discovered_tools:
            logger.warning("발견된 MCP 도구가 없습니다.")
            return []
        
        tools = []
        for tool_info in self._discovered_tools:
            tool_name = tool_info['name']
            description = tool_info['description']
            input_schema = tool_info['input_schema']
            
            caller = self._create_mcp_caller(tool_name, input_schema)
            
            langchain_tool = Tool(
                name=tool_name,
                func=caller,
                description=description
            )
            
            tools.append(langchain_tool)
            logger.info(f"LangChain 도구 생성 완료: {tool_name}")
        
        return tools
    
    # 유틸리티 메서드 추가 (기존 파일에 있던 기능들)
    async def test_connection(self) -> bool:
        """MCP 서버 연결 테스트"""
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    logger.info("MCP 서버 연결 테스트 성공")
                    return True
        except Exception as e:
            logger.error(f"MCP 서버 연결 실패: {e}")
            return False
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """특정 도구의 정보 반환"""
        for tool in self._discovered_tools:
            if tool['name'] == tool_name:
                return tool
        return None
    
    def list_available_tools(self) -> List[str]:
        """사용 가능한 도구 목록 반환"""
        return [tool['name'] for tool in self._discovered_tools]

# 확장된 테스트 (기존 파일 스타일)
async def test_bridge():
    """확장된 브리지 테스트"""
    print("=== MCP Bridge 확장 테스트 ===")
    
    bridge = MCPBridge("server.py")
    
    # 1. 연결 테스트
    print("1. MCP 서버 연결 테스트...")
    if await bridge.test_connection():
        print("연결 성공")
    else:
        print("연결 실패")
        return
    
    # 2. 도구 발견
    print("\n2. 도구 발견 테스트...")
    tools = await bridge.discover_tools()
    print(f"발견된 도구 수: {len(tools)}")
    
    # 3. 도구 정보 출력
    print("\n3. 발견된 도구들:")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
        print(f"    스키마: {tool['input_schema']}")
    
    # 4. LangChain 도구 변환
    print("\n4. LangChain 도구 변환...")
    langchain_tools = await bridge.create_langchain_tools()
    print(f"변환된 도구 수: {len(langchain_tools)}")
    
    # 5. 개별 도구 테스트
    print("\n5. 개별 도구 테스트:")
    for tool in langchain_tools:
        if tool.name == "add":
            result = tool.func("5, 3")
            print(f"  add(5, 3) = {result}")
        elif tool.name == "say_hello":
            result = tool.func("Alice")
            print(f"  say_hello('Alice') = {result}")
    
    # 6. 유틸리티 메서드 테스트
    print("\n6. 유틸리티 테스트:")
    available_tools = bridge.list_available_tools()
    print(f"사용 가능한 도구: {available_tools}")
    
    add_info = bridge.get_tool_info("add")
    if add_info:
        print(f"add 도구 정보: {add_info['description']}")

# 간단한 테스트도 유지
async def simple_test():
    """간단한 테스트"""
    print("MCP Bridge 간단 테스트")
    
    bridge = MCPBridge("server.py")
    tools = await bridge.create_langchain_tools()
    
    print(f"생성된 도구 수: {len(tools)}")
    
    # 간단한 테스트
    for tool in tools:
        if tool.name == "add":
            result = tool.func("5, 3")
            print(f"add(5, 3) = {result}")
            break

if __name__ == "__main__":
    print("테스트 모드를 선택하세요:")
    print("1. 간단한 테스트")
    print("2. 확장된 테스트")
    
    choice = input("선택 (1/2): ").strip()
    
    if choice == "1":
        asyncio.run(simple_test())
    elif choice == "2":
        asyncio.run(test_bridge())
    else:
        print("1 또는 2를 선택해주세요.")
