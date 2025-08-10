# 원격 MCP 서버 (HTTP 기반)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn
from datetime import datetime

app = FastAPI(title="Simple Remote MCP Server")

# CORS 설정 (클라이언트에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청/응답 모델
class ToolCallRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = {}

class ToolResponse(BaseModel):
    success: bool
    result: Any
    error: str = None

class ToolInfo(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

# 사용 가능한 도구들 정의
AVAILABLE_TOOLS = {
    "hello": {
        "description": "인사말을 생성합니다",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "인사할 대상의 이름"}
            },
            "required": []
        }
    },
    "add": {
        "description": "두 숫자를 더합니다",
        "parameters": {
            "type": "object", 
            "properties": {
                "a": {"type": "number", "description": "첫 번째 숫자"},
                "b": {"type": "number", "description": "두 번째 숫자"}
            },
            "required": ["a", "b"]
        }
    },
    "current_time": {
        "description": "현재 시간을 조회합니다",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "weather": {
        "description": "도시의 날씨 정보를 조회합니다 (가상)",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "도시 이름"}
            },
            "required": ["city"]
        }
    }
}

# 실제 도구 구현
def execute_hello(name: str = "World") -> str:
    return f"Hello, {name}! (from remote server)"

def execute_add(a: float, b: float) -> float:
    return a + b

def execute_current_time() -> str:
    return f"Remote server time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

def execute_weather(city: str) -> Dict[str, Any]:
    # 가상 날씨 데이터
    return {
        "city": city,
        "temperature": "22°C",
        "condition": "맑음",
        "humidity": "60%",
        "source": "remote_server"
    }

# API 엔드포인트들

@app.get("/")
async def root():
    return {"message": "Simple Remote MCP Server", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/tools")
async def list_tools() -> List[ToolInfo]:
    """사용 가능한 도구 목록 반환"""
    tools = []
    for name, info in AVAILABLE_TOOLS.items():
        tools.append(ToolInfo(
            name=name,
            description=info["description"],
            parameters=info["parameters"]
        ))
    return tools

@app.post("/execute")
async def execute_tool(request: ToolCallRequest) -> ToolResponse:
    """도구 실행"""
    tool_name = request.tool_name
    params = request.parameters
    
    try:
        if tool_name == "hello":
            result = execute_hello(params.get("name", "World"))
        elif tool_name == "add":
            if "a" not in params or "b" not in params:
                raise ValueError("a와 b 매개변수가 필요합니다")
            result = execute_add(params["a"], params["b"])
        elif tool_name == "current_time":
            result = execute_current_time()
        elif tool_name == "weather":
            if "city" not in params:
                raise ValueError("city 매개변수가 필요합니다")
            result = execute_weather(params["city"])
        else:
            raise ValueError(f"알 수 없는 도구: {tool_name}")
        
        return ToolResponse(success=True, result=result)
        
    except Exception as e:
        return ToolResponse(success=False, result=None, error=str(e))

@app.get("/tools/{tool_name}")
async def get_tool_info(tool_name: str):
    """특정 도구 정보 조회"""
    if tool_name not in AVAILABLE_TOOLS:
        raise HTTPException(status_code=404, detail="도구를 찾을 수 없습니다")
    
    return {
        "name": tool_name,
        **AVAILABLE_TOOLS[tool_name]
    }

# 서버 시작 함수들
def start_server(host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
    """서버 시작 """
    print("원격 MCP 서버 시작...")
    print(f"서버 주소: http://localhost:{port}")
    print(f"도구 목록: http://localhost:{port}/tools")
    print(f"헬스 체크: http://localhost:{port}/health")
    print("=" * 50)
    
    if debug:
        # 개발 모드 (reload 사용)
        uvicorn.run(
            "server:app",  # import string 형태
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )
    else:
        # 프로덕션 모드 (경고 없음)
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )

def start_production_server():
    """프로덕션 서버 시작"""
    start_server(debug=False)

def start_dev_server():
    """개발 서버 시작 (auto-reload)"""
    start_server(debug=True)

if __name__ == "__main__":
    import sys
    
    # 명령행 인자로 모드 선택
    if len(sys.argv) > 1 and sys.argv[1] == "--dev":
        start_dev_server()
    else:
        start_production_server()
