# pip install llm-math
# 윈도우 기준 260글자 이상의 경로가 생성되면 오류날수 있음
# Windows 키 + R → gpedit.msc 실행
# 컴퓨터 구성 > 관리 템플릿 > 시스템 > 파일 시스템 경로로 이동
# Win32 긴 경로 사용 허용 → 사용 으로 변경
# 시스템 재시작 후 재시도
#
# 또는 오류가 나는 vllm 제외하고 llm-math 만 설치
# pip install llm-math --no-deps

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType

# from langchain.agents import load_tools 는 예전 방식이고,
# from langchain_community.agent_toolkits.load_tools import load_tools 가 LangChain 최신 버전(v0.2~v0.3 이후) 에서 권장되는 방식


# 0. 환경 변수 로드
load_dotenv()

# 1. LLM 설정
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. llm-math 도구 로드
tools = load_tools(["llm-math"], llm=llm)

# tools 로드 시 llm 인자가 필요한 경우
# 일부 도구는 자체적으로 LLM을 호출해야 합니다.
# 예: "llm-math", "serpapi", "python_repl" 같은 툴은 내부 동작에 LLM이 필요합니다.
# 이런 툴을 load_tools()로 불러올 때 어떤 LLM을 쓸지 지정해야 합니다.


# 3. 에이전트 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 4. 수학 문제 입력
result = agent.invoke({"input": "What is the result of (53 * 7 + 2) / 5?"})
# result = agent.invoke({"input": "53 * 7 + 2 / 5 는?"})
# result = agent.invoke({"input": "삼각형의 높이가 5이고 밑변이 10이면 넓이는 얼마야?"})
print(result["output"])


# question = """
# 기차가 시속 80km로 2.5시간 동안 달리고, 이후 시속 100km로 1.5시간 동안 달렸습니다.
# 이 기차가 이동한 총 거리는 얼마이며, 평균 속도는 얼마인가요?
# """
# # 실행
# result = agent.invoke({"input": question})

# # 출력
# print("\n문제:\n", question)
# print("\n결과:\n", result["output"])
