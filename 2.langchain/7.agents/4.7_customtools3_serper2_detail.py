from dotenv import load_dotenv

from langchain_openai import OpenAI, ChatOpenAI
from langchain.schema import SystemMessage

from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

import os


# 0. 환경 변수 로드
load_dotenv()

# 환경 변수 확인
serper_api_key = os.getenv("SERPER_API_KEY")
if not serper_api_key:
    print("SERPER_API_KEY 환경 변수가 설정되어 있지 않습니다.")
    print("Serper.dev에서 API 키를 발급받아 .env 파일에 추가하세요.")
    exit(1)

# 1. OpenAI 모델 초기화 
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. Serper 검색 초기화
# search = GoogleSerperAPIWrapper()  # 간단 버전
search = GoogleSerperAPIWrapper(
    k=5,           # 상위 5건
    gl="kr",       # 국가
    hl="ko",       # 언어
    location="Seoul, South Korea"  # 위치 바이어스
)


# 검색 도구 생성
tools = [
    Tool(
        name="GoogleSerperSearch",
        func=search.run,
        description="최신 정보 (날짜, 정보) 검색용. 사용자가 묻는 한국어 쿼리를 그대로 입력해 결과를 받아 요약한다."
    )
]

# 3. 에이전트 초기화
# agent = initialize_agent(
#     tools=tools,
#     llm=llm,
#     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True,
# )

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    max_iterations=3,            # 반복 억제
    early_stopping_method="force",  # 실패 시 '생성으로 마무리' 금지
    verbose=True,
    agent_kwargs={"system_message": SystemMessage(content=
        "검색 결과에 근거해 한국어로 간단히 답하라. "
        "확실한 수치·시간이 없으면 '정보 부족'이라고 말하고 추정하지 마라."
    )}
)


# 4. 에이전트에게 검색 요청
result = agent.invoke({"input": "오늘은 며칠이고, 서울의 오늘 날씨는 어때?"})
print(result["output"])
