from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool

# 환경 변수 로드
load_dotenv()

# OpenAI 모델 초기화
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)

# 사용자 정의 도구 생성
@tool
def get_current_weather(location: str) -> str:
    """특정 위치의 현재 날씨 정보를 가져옵니다."""
    # 실제로는 날씨 API를 호출해야 하지만, 예시이므로 가상 데이터 반환
    weather_data = {
        "서울": "맑음, 기온 22도",
        "부산": "흐림, 기온 25도",
        "제주": "비, 기온 20도"
    }
    return weather_data.get(location, f"{location}의 날씨 정보가 없습니다.")

@tool
def get_population(city: str) -> str:
    """특정 도시의 인구 정보를 가져옵니다."""
    # 가상 데이터
    population_data = {
        "서울": "약 970만 명",
        "부산": "약 340만 명",
        "인천": "약 300만 명",
        "대구": "약 240만 명"
    }
    return population_data.get(city, f"{city}의 인구 정보가 없습니다.")

# 도구 목록 생성
tools = [get_current_weather, get_population]

# 에이전트 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 에이전트 실행
result = agent.invoke({"input": "서울의 날씨는 어때? 그리고 인구는 몇 명이야?"})
print(result["output"])
