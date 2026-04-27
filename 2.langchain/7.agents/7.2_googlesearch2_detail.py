# Google Custom Search API 키 발급 방법
# 1. Google Cloud Platform 계정 생성
#  - 먼저 Google Cloud Platform 계정이 필요합니다. 없다면 https://console.cloud.google.com 에 접속하여 계정을 만드세요.
# 2. 프로젝트 생성
#  - Google Cloud Console에 로그인합니다
#  - 상단의 프로젝트 선택 드롭다운에서 "새 프로젝트"를 클릭합니다
#  - 프로젝트 이름을 입력하고 "만들기"를 클릭합니다
# 3. Custom Search API 활성화
#  - 왼쪽 메뉴에서 "API 및 서비스" > "라이브러리"로 이동합니다
#  - 검색창에 "Custom Search API"를 입력합니다
#  - 검색 결과에서 "Custom Search API"를 클릭합니다
#  - "사용 설정" 버튼을 클릭합니다
# 4. API 키 생성
#  - 왼쪽 메뉴에서 "API 및 서비스" > "사용자 인증 정보"로 이동합니다
#  - 상단의 "사용자 인증 정보 만들기" 버튼을 클릭합니다
#  - 드롭다운 메뉴에서 "API 키"를 선택합니다
#  - 생성된 API 키를 복사해두세요 (이 키가 GOOGLE_API_KEY로 사용됩니다)
#  - 필요하다면 "API 키 제한"을 설정하여 키의 보안을 강화할 수 있습니다
# 5. Programmable Search Engine 설정
#  - https://programmablesearchengine.google.com/에 접속합니다
#  - "검색 엔진 만들기" 버튼을 클릭합니다
#  - 검색 엔진 설정:
#    - 검색 대상: "전체 웹 검색"을 선택합니다
#    - 엔진 이름: 원하는 이름을 입력합니다
#    - 기타 설정: 필요에 따라 조정합니다
#  - "만들기" 버튼을 클릭합니다
#  - 생성 후 "검색 엔진 수정" 화면으로 이동합니다
#  - "설정" > "기본" 메뉴에서 "검색 엔진 ID"를 찾아 복사합니다 (이 ID가 GOOGLE_CSE_ID로 사용됩니다)
# 6. 환경 변수 설정
#  - 환경 변수를 설정하거나 .env 파일에 다음과 같이 추가합니다:
#    - GOOGLE_API_KEY=발급받은_API_키
#    - GOOGLE_CSE_ID=검색_엔진_ID

# pip install google-api-python-client

import os
from dotenv import load_dotenv

from langchain_openai import OpenAI, ChatOpenAI

from langchain.agents import AgentType, initialize_agent
from langchain.tools import Tool
from langchain_community.utilities import GoogleSearchAPIWrapper

# 0. 환경 변수 로드
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID  = os.getenv("GOOGLE_CSE_ID")

if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
    raise RuntimeError(
        "GOOGLE_API_KEY/GOOGLE_CSE_ID가 없습니다. .env 설정을 확인하세요."
    )
    
# 1. OpenAI 모델 초기화 
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)

# LLM 세팅: 타임아웃/재시도/토큰 상한
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    timeout=30,
    max_retries=2,
)

# 2. Google Search 도구 로드
# 참고: GOOGLE_API_KEY와 GOOGLE_CSE_ID 환경 변수 필요

# Google Search 도구를 명시적으로 구성
google = GoogleSearchAPIWrapper(
    google_api_key=GOOGLE_API_KEY,
    google_cse_id=GOOGLE_CSE_ID,
    k=5,                 # 상위 5개만
    # gl="kr",           # (지원되는 버전에 한해) 지역 힌트
    # lr="lang_ko"       # (지원되는 버전에 한해) 언어 힌트
)

google_tool = Tool(
    name="google_search",
    func=google.run,
    description="일반 웹검색/뉴스 요약이 필요할 때 사용"
)

# 3. 간단한 규칙 기반 라우팅(날씨 키워드이면 직접 답)
WEATHER_KEYWORDS = ("날씨", "기온", "우산", "강수", "미세먼지", "대기질")

def router_tool(query: str) -> str:
    # 매우 러프한 라우팅: '오늘 날씨' 류는 검색 대신 직접 안내
    if any(k in query for k in WEATHER_KEYWORDS):
        return (
            "날씨 질의는 검색보다 날씨 API가 더 정확합니다. "
            "예: Open-Meteo, KMA, OpenWeather 등.\n"
            "데모로는 '서울 현재 날씨는 ○○이고 최고/최저는 ○○/○○°C 예상'처럼 "
            "날씨 API 연동으로 처리하세요."
        )
    # 그 외엔 구글 검색으로
    return google.run(query)

router = Tool(
    name="smart_router",
    func=router_tool,
    description="날씨/일반검색을 간단히 라우팅하는 유틸리티"
)

# 4. 에이전트 초기화
agent = initialize_agent(
    tools=[router, google_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
    # verbose=False,  # 개발 중에만 True
)

# 5. 에이전트에게 검색 요청
# result = agent.invoke({"input": "서울의 오늘 날씨는 어때?"})
result = agent.invoke({"input": "삼성전자의 최근 주가 동향은 어때?"})
print(result["output"])
