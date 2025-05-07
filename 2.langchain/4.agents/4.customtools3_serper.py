from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
import os

# 환경 변수 로드
load_dotenv()

# 환경 변수 확인
serper_api_key = os.getenv("SERPER_API_KEY")
if not serper_api_key:
    print("SERPER_API_KEY 환경 변수가 설정되어 있지 않습니다.")
    print("Serper.dev에서 API 키를 발급받아 .env 파일에 추가하세요.")
    exit(1)

# OpenAI 모델 초기화 
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)

# Serper 검색 초기화
search = GoogleSerperAPIWrapper()

# 검색 도구 생성
tools = [
    Tool(
        name="GoogleSerperSearch",
        func=search.run,
        description="최신 정보나 실시간 데이터를 검색할 때 유용합니다. 질문을 그대로 입력하세요."
    )
]

# 에이전트 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    # verbose=False  # 중간 과정을 출력하지 않음
)

# 에이전트에게 검색 요청
result = agent.invoke({"input": "서울의 오늘 날씨는 어때?"})
print(result["output"])
