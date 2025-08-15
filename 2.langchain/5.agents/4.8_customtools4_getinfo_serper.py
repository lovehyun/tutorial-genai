from dotenv import load_dotenv
import re

from langchain_openai import OpenAI, ChatOpenAI
from langchain.schema import SystemMessage

from langchain.tools import tool
from langchain.agents import initialize_agent, AgentType

from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
from langchain.tools import Tool


# 0. 환경 변수 로드
load_dotenv()

# 1. 언어 모델 생성
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.0)
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

# 2-1. 사용자 정의 도구 생성
# 예, 날씨 검색
@tool
def get_current_weather(location: str) -> str:
    """특정 위치의 현재 날씨 정보를 가져옵니다. 위치는 한국어로 입력합니다."""
    # 실제로 여기에 날씨 요청 구현하면 됨.
    weather_data = {
        "서울": "맑음, 기온 22도",
        "부산": "흐림, 기온 25도",
        "제주": "비, 기온 20도"
    }
    return weather_data.get(location, f"{location}의 날씨 정보가 없습니다.")

# 예, 인구 검색
@tool
def get_population(city: str) -> str:
    """특정 도시의 인구 정보를 가져옵니다."""
    # 가상 데이터...
    population_data = {
        "서울": "약 970만 명",
        "부산": "약 340만 명",
        "인천": "약 300만 명",
        "대구": "약 240만 명"
    }
    return population_data.get(city, f"{city}의 인구 정보가 없습니다.")

# 2-2. 검색 도구 설정
# search = GoogleSerperAPIWrapper()
search = GoogleSerperAPIWrapper(k=5, gl="kr", hl="ko", location="Seoul, South Korea")

# 2-3. 도구 설정
tools = [
    get_current_weather, 
    get_population,
    Tool(
        name="GoogleSerperSearch",
        func=search.run,
        description="최신 정보(예: 오늘 날짜/뉴스/날씨/인구)를 한국어 질문 그대로 검색"
    )
]

# 3. 에이전트 정의

rules = SystemMessage(content=
    "도시 관련 답변은 도구 결과에만 근거해 한국어로 간결히 답하라. "
    "값이 없으면 '없음(이유)'라고 말하고 추정하지 마라."
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    # agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    agent_kwargs={"system_message": rules},
    max_iterations=5,  # 에이전트가 최대 5번까지만 도구를 실행하도록 제한
    handle_parsing_errors=True,  # LLM 응답 파싱 실패 시 에러를 무시하고 계속 실행
    early_stopping_method="force",  # 지금까지 모은 정보로 바로 종료 (정리 과정 없이)
    return_intermediate_steps=True,  # 폴백 판단용
    verbose=True,
)

# 4. 질의 실행
# result = agent.invoke({"input": "서울의 날씨는 어때? 그리고 인구는?"})
# result = agent.invoke({"input": "제주의 날씨는 어때? 그리고 인구는?"})
# result = agent.invoke({"input": "인천의 날씨는 어때? 그리고 인구는?"})
result = agent.invoke({"input": "대전의 날씨는 어때? 그리고 인구는?"})
print(result["output"])
