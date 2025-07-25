from dotenv import load_dotenv
import os
from langchain_openai import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper

# 환경 변수 로드
load_dotenv()

# OpenAI 모델 초기화
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.1)

# 1. Google Serper 검색 도구 설정
serper_api_key = os.getenv("SERPER_API_KEY")
if not serper_api_key:
    raise ValueError("SERPER_API_KEY가 환경 변수에 설정되어 있지 않습니다. .env 파일에 추가해주세요.")

search = GoogleSerperAPIWrapper()
google_tool = Tool(
    name="Google Search",
    func=search.run,
    description="최신 정보, 뉴스, 최근 사건, 현재 상태, 실시간 데이터 또는 트렌드에 관한 질문에 사용합니다. 구체적인 검색어를 입력하세요."
)

# 2. 위키피디아 검색 도구 설정
wikipedia = WikipediaAPIWrapper(lang="ko")
wiki_tool = Tool(
    name="Wikipedia",
    func=wikipedia.run,
    description="역사적 사실, 개념 설명, 유명인, 장소, 과학 지식 등 잘 정립된 지식이나 백과사전적 정보를 얻을 때 사용합니다. 정의가 필요한 주제나 용어를 입력하세요."
)

# 3. 도구 선택 지침을 포함하는 시스템 메시지
system_message = """질문에 따라 가장 적절한 도구를 선택하세요:
1. 역사적 사실, 개념 설명, 용어 정의, 유명인 정보, 학문적 주제에는 'Wikipedia' 도구를 사용하세요.
2. 최신 뉴스, 현재 이벤트, 실시간 정보, 최근 트렌드에는 'Google Search' 도구를 사용하세요.
3. 모호한 경우에는 먼저 Wikipedia로 기본 개념을 확인한 후, 필요하면 Google Search로 최신 정보를 찾으세요."""

# 4. 에이전트 초기화
agent_chain = initialize_agent(
    tools=[google_tool, wiki_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={"system_message": system_message}
)

# 5. 실행
user_question = input("질문을 입력하세요: ")
result = agent_chain.invoke({"input": user_question})
print("\n최종 결과:", result["output"])
