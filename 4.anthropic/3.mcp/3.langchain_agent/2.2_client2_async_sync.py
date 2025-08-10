# agent2.py
import asyncio
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

# 개선된 프롬프트 (Hub 없이)
REACT_PROMPT = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

# 개선된 MCP 도구 호출 함수들
def call_mcp_hello(name: str) -> str:
    """인사말 생성 도구"""
    async def run():
        server_params = StdioServerParameters(command="python", args=["server2.py"])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("say_hello", {"name": name})
                # JSON 파싱 제거 - 직접 텍스트 반환
                return result.content[0].text
    
    try:
        return asyncio.run(run())
    except Exception as e:
        return f"인사 생성 오류: {str(e)}"

def call_mcp_add(input_str: str) -> str:
    """덧셈 계산 도구"""
    async def run(a: int, b: int):
        server_params = StdioServerParameters(command="python", args=["server2.py"])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("add", {"a": a, "b": b})
                return result.content[0].text
    
    try:
        # 더 안정적인 숫자 추출
        import re
        numbers = re.findall(r'-?\d+', input_str)
        
        if len(numbers) >= 2:
            a, b = int(numbers[0]), int(numbers[1])
            return asyncio.run(run(a, b))
        else:
            return "두 개의 숫자를 찾을 수 없습니다. 예: '10과 25를 더해주세요'"
            
    except Exception as e:
        return f"계산 오류: {str(e)}"

def call_mcp_now(query: str = "") -> str:
    """현재 시간 조회 도구"""
    async def run():
        server_params = StdioServerParameters(command="python", args=["server2.py"])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("now")
                return result.content[0].text
    
    try:
        return asyncio.run(run())
    except Exception as e:
        return f"시간 조회 오류: {str(e)}"

# 최신 방식으로 도구 생성
def create_tools():
    """MCP 도구들을 LangChain 도구로 변환"""
    return [
        Tool(
            name="say_hello",
            func=call_mcp_hello,
            description="사람의 이름을 받아서 인사말을 생성합니다. 입력: 이름"
        ),
        Tool(
            name="add_numbers", 
            func=call_mcp_add,
            description="두 숫자를 더합니다. 자연어로 '10과 25를 더해주세요' 형태로 입력하세요"
        ),
        Tool(
            name="get_current_time",
            func=call_mcp_now,
            description="현재 시간과 날짜를 알려줍니다. 매개변수 불필요"
        )
    ]

def create_agent():
    """최신 방식으로 Agent 생성"""
    # 도구 설정
    tools = create_tools()
    
    # LLM 설정
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-3.5-turbo"
    )
    
    # 프롬프트 설정 (Hub 없이)
    prompt = PromptTemplate.from_template(REACT_PROMPT)
    
    # 최신 방식으로 Agent 생성
    agent = create_react_agent(llm, tools, prompt)
    
    # AgentExecutor로 감싸기
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3,  # 무한 루프 방지
        early_stopping_method="generate"  # 조기 종료 설정
    )
    
    return agent_executor

# 비동기 실행을 위한 래퍼
async def run_agent_async(agent_executor, query):
    """Agent를 비동기로 실행"""
    try:
        response = await agent_executor.ainvoke({"input": query})
        return response["output"]
    except Exception as e:
        return f"Agent 실행 오류: {str(e)}"

def main():
    """메인 실행 함수"""
    print("개선된 LangChain + MCP Agent")
    print("=" * 50)
    
    # Agent 생성
    agent_executor = create_agent()
    
    # 테스트 케이스
    test_cases = [
        "Alice에게 인사해줘",
        "10과 25를 더해주세요", 
        "지금 몇 시야?",
        "Bob에게 안녕하세요 라고 말해줘",
        "100 더하기 200은?"
    ]
    
    print("테스트 시작:")
    print("-" * 30)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[테스트 {i}] {test}")
        print("-" * 40)
        
        try:
            # 동기 방식으로 실행 - Blocking
            response = agent_executor.invoke({"input": test})
            print(f"[결과] {response['output']}")
        except Exception as e:
            print(f"[오류] {str(e)}")
        
        print("=" * 50)

# 비동기 버전 메인 함수
async def main_async():
    """비동기 메인 함수 (권장)"""
    print("개선된 LangChain + MCP Agent (비동기)")
    print("=" * 50)
    
    # Agent 생성
    agent_executor = create_agent()
    
    # 테스트 케이스
    test_cases = [
        "Charlie에게 인사해주세요",
        "50과 75를 더해주세요", 
        "현재 시간을 알려주세요"
    ]
    
    print("비동기 테스트 시작:")
    print("-" * 30)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[비동기 테스트 {i}] {test}")
        print("-" * 40)
        
        # 비동기적으로 실행 - Non-blocking (내부적으로 reponse = await agent_executor.ainvoke({"input": query}))
        result = await run_agent_async(agent_executor, test)
        print(f"[결과] {result}")
        print("=" * 50)

if __name__ == "__main__":
    print("실행 방식을 선택하세요:")
    print("1. 동기 방식 (기본)")
    print("2. 비동기 방식 (권장)")
    
    choice = input("선택 (1 또는 2): ").strip()
    
    if choice == "2":
        asyncio.run(main_async())
    else:
        main()


# 1. 동기 방식 실행 흐름
# 테스트 1 시작
# ├── MCP 도구 1 호출
# │   ├── 새 이벤트 루프 생성
# │   ├── MCP 서버 프로세스 시작
# │   ├── 통신 완료
# │   └── 이벤트 루프 종료
# ├── MCP 도구 2 호출  
# │   ├── 또 새 이벤트 루프 생성
# │   └── ...
# └── 테스트 1 완료
# 테스트 2 시작 (위 과정 반복)

# 2. 비동기 방식 실행 흐름
# 이벤트 루프 시작
# ├── 테스트 1 시작
# │   ├── MCP 도구 1 호출 (기존 루프 사용)
# │   ├── MCP 도구 2 호출 (기존 루프 사용)
# │   └── 테스트 1 완료
# ├── 테스트 2 시작
# │   └── ... (모두 같은 루프 사용)
# └── 이벤트 루프 종료

# 성능 테스트 예상 결과
# 동기 방식 (예상 소요 시간)
# 테스트 1: 2.5초
# 테스트 2: 2.5초  
# 테스트 3: 2.5초
# 총 소요 시간: 7.5초
#
# 비동기 방식 (예상 소요 시간)  
# 테스트 1: 2.0초
# 테스트 2: 2.0초
# 테스트 3: 2.0초  
# 총 소요 시간: 6.0초 (약 20% 빠름)
