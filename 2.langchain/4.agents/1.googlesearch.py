# Google Custom Search API 키 발급 방법
# 1. Google Cloud Platform 계정 생성
#  - 먼저 Google Cloud Platform 계정이 필요합니다. 없다면 https://console.cloud.google.com에 접속하여 계정을 만드세요.
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

from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType

# 환경 변수 로드
load_dotenv()

# OpenAI 모델 초기화 
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)

# Google Search 도구 로드
# 참고: GOOGLE_API_KEY와 GOOGLE_CSE_ID 환경 변수 필요
tools = load_tools(["google-search"])

# 에이전트 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 에이전트에게 검색 요청
result = agent.invoke({"input": "서울의 오늘 날씨는 어때?"})
print(result["output"])
