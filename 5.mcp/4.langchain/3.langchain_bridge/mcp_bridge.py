import asyncio
import json
import logging
from typing import List, Dict, Any, Callable

from langchain_core.tools import Tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 로깅을 파일로 설정
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
        self._tools: List[Dict[str, Any]] = []
        logger.info(f"MCPBridge 초기화 완료: server_script={server_script}")

    async def discover_tools(self) -> List[Dict[str, Any]]:
        """MCP 서버에서 도구들을 발견"""
        logger.info("MCP 서버에서 도구 발견 시작")
        
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_response = await session.list_tools()
                
                self._tools = []
                for tool in tools_response.tools:
                    tool_info = {
                        'name': tool.name,
                        'description': tool.description,
                        'schema': tool.inputSchema
                    }
                    self._tools.append(tool_info)
                    logger.info(f"도구 발견: {tool.name} - {tool.description}")
                    logger.debug(f"도구 스키마: {tool.inputSchema}")

                logger.info(f"도구 발견 완료: 총 {len(self._tools)}개")
                return self._tools
    
    def _parse_input(self, tool_name: str, input_str: str) -> Dict[str, Any]:
        """입력 문자열을 파라미터로 파싱"""
        logger.debug(f"입력 파싱 시작: tool={tool_name}, input='{input_str}'")

        if not input_str.strip():
            return {}
        
        # JSON 형태인지 확인
        try:
            result = json.loads(input_str)
            logger.debug(f"JSON 형태 입력 파싱 성공: {result}")
            return result
        except json.JSONDecodeError:
            logger.debug("JSON 형태 아님, 스키마 기반 파싱 시도")
            pass
        
        # 스키마에서 파라미터 정보 가져오기
        tool_schema = None
        for tool in self._tools:
            if tool['name'] == tool_name:
                tool_schema = tool['schema']
                break
        
        if not tool_schema or 'properties' not in tool_schema:
            logger.warning(f"도구 '{tool_name}'의 스키마를 찾을 수 없음")
            return {}
        
        properties = tool_schema['properties']
        result = {}
        input_str = input_str.strip("'\"")
        
        logger.debug(f"스키마 정보: properties={list(properties.keys())}")

        # 단일 파라미터
        if len(properties) == 1:
            param_name = list(properties.keys())[0]
            param_type = properties[param_name].get('type', 'string')
            
            logger.debug(f"단일 파라미터 처리: {param_name} ({param_type})")

            if param_type == 'integer':
                try:
                    result[param_name] = int(input_str)
                    logger.debug(f"정수 변환 성공: {result[param_name]}")
                except ValueError:
                    result[param_name] = input_str
                    logger.debug("정수 변환 실패, 문자열로 처리")
            elif param_type == 'number':
                try:
                    result[param_name] = float(input_str)
                    logger.debug(f"실수 변환 성공: {result[param_name]}")
                except ValueError:
                    result[param_name] = input_str
                    logger.debug("실수 변환 실패, 문자열로 처리")
            else:
                result[param_name] = input_str
                logger.debug(f"문자열로 처리: {result[param_name]}")
        
        # 복수 파라미터 (콤마로 분리)
        elif len(properties) > 1:
            parts = [p.strip() for p in input_str.split(',')]
            param_names = list(properties.keys())
            
            logger.debug(f"복수 파라미터 처리: {param_names}, 입력 부분: {parts}")

            for i, part in enumerate(parts):
                if i < len(param_names):
                    param_name = param_names[i]
                    param_type = properties[param_name].get('type', 'string')
                    
                    logger.debug(f"파라미터 {i+1}: {param_name} ({param_type}) = '{part}'")

                    if param_type == 'integer':
                        try:
                            result[param_name] = int(part)
                            logger.debug("정수 변환 성공")
                        except ValueError:
                            result[param_name] = part
                            logger.debug("정수 변환 실패, 문자열로 처리")
                    elif param_type == 'number':
                        try:
                            result[param_name] = float(part)
                            logger.debug("실수 변환 성공")
                        except ValueError:
                            result[param_name] = part
                            logger.debug("실수 변환 실패, 문자열로 처리")
                    else:
                        result[param_name] = part
                        logger.debug("문자열로 처리")
        
        logger.info(f"입력 파싱 완료: {result}")
        return result
    
    async def _call_tool(self, tool_name: str, params: Dict[str, Any]) -> str:
        """MCP 도구 호출"""
        
        logger.info(f"MCP 도구 '{tool_name}' 호출 시작")
        logger.debug(f"호출 파라미터: {params}")
        
        async with stdio_client(self.server_params) as (read, write):
            logger.debug("MCP 서버 연결 시작")
            async with ClientSession(read, write) as session:
                logger.debug("MCP 세션 초기화 중")
                await session.initialize()
                
                logger.debug(f"MCP 도구 '{tool_name}' 실행 중")
                result = await session.call_tool(tool_name, params)
                
                logger.debug("MCP 서버 응답 수신")
                
                if result.content and len(result.content) > 0:
                    content = result.content[0].text          # 먼저 할당 후 로깅 (NameError 방지)
                    logger.debug(f"응답 내용: {content}")
                    
                    # JSON 파싱 시도
                    try:
                        parsed = json.loads(content)
                        if isinstance(parsed, dict) and "greeting" in parsed:
                            final_result = parsed["greeting"]
                            logger.info(f"인사말 추출: {final_result}")
                            return final_result
                        else:
                            final_result = str(parsed)
                            logger.info(f"JSON 파싱 결과: {final_result}")
                            return final_result
                    except json.JSONDecodeError:
                        logger.info(f"텍스트 응답: {content}")
                        return content
                else:
                    logger.warning("빈 응답 수신")
                    return "완료"
    
    def _create_tool_caller(self, tool_name: str) -> Callable:
        """도구 호출 함수 생성"""
        logger.debug(f"도구 호출 함수 생성: {tool_name}")
        
        def tool_caller(input_str: str = "") -> str:
            logger.info(f"도구 '{tool_name}' 호출 요청 수신")
            logger.debug(f"입력: '{input_str}'")
            
            params = self._parse_input(tool_name, input_str)
            
            try:
                # 이벤트 루프 확인 후 실행
                try:
                    loop = asyncio.get_running_loop()
                    logger.debug("기존 이벤트 루프 감지, 새 스레드에서 실행")

                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._call_tool(tool_name, params))
                        result = future.result(timeout=10)
                        logger.info(f"도구 '{tool_name}' 실행 완료: {result}")
                        return result
                except RuntimeError:
                    logger.debug("새 이벤트 루프에서 실행")
                    return asyncio.run(self._call_tool(tool_name, params))
            except Exception as e:
                logger.error(f"{tool_name} 호출 오류: {e}")
                return f"오류: {str(e)}"
        
        return tool_caller
    
    async def create_langchain_tools(self) -> List[Tool]:
        """LangChain Tool 생성"""
        logger.info("LangChain 도구 생성 시작")
        
        if not self._tools:
            logger.debug("캐시된 도구가 없음, 도구 발견 시작")
            try:
                await self.discover_tools()
            except Exception as e:
                logger.error(f"도구 발견 실패: {e}")
                return []
        
        tools = []
        for tool_info in self._tools:
            tool_name = tool_info['name']
            logger.debug(f"LangChain 도구 생성 중: {tool_name}")
            
            caller = self._create_tool_caller(tool_name)
            
            langchain_tool = Tool(
                name=tool_name,
                func=caller,
                description=tool_info['description']
            )
            
            tools.append(langchain_tool)
            logger.info(f"LangChain 도구 생성 완료: {tool_name}")
        
        logger.info(f"전체 LangChain 도구 생성 완료: {len(tools)}개")
        return tools

# 간단한 테스트
async def test():
    """간단한 테스트"""
    print("MCP Bridge 테스트")
    
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
    asyncio.run(test())
