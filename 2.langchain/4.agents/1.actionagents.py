# https://python.langchain.com/docs/modules/agents/

# 필요한 패키지 설치 (최신 업데이트 적용)
# pip install langchain_openai wikipedia numexpr

from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.agents import load_tools, initialize_agent, AgentType

# 환경 변수 로드
load_dotenv()

# 프롬프트 설정
prompt = "대한민국의 공휴일 날짜들은? 그리고 이 날짜들의 월과 일의 숫자들의 합산은?"

# OpenAI 모델 초기화
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.9)

# 툴 로드
tools = load_tools(["wikipedia", "llm-math"], llm=llm)

# LangChain 에이전트 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 모델 실행
result = agent.invoke({"input": prompt})
print(result)


# 사용 가능한 LangChain의 모든 도구 확인
from langchain.agents import get_all_tool_names

# print(get_all_tool_names())

"""
[   'requests',
    'requests_get',
    'requests_post',
    'requests_patch',
    'requests_put',
    'requests_delete',
    'terminal',
    'sleep',
    'wolfram-alpha',
    'google-search',
    'google-search-results-json',
    'searx-search-results-json',
    'bing-search',
    'metaphor-search',
    'ddg-search',
    'google-lens',
    'google-serper',
    'google-scholar',
    'google-finance',
    'google-trends',
    'google-jobs',
    'google-serper-results-json',
    'searchapi',
    'searchapi-results-json',
    'serpapi',
    'dalle-image-generator',
    'twilio',
    'searx-search',
    'merriam-webster',
    'wikipedia',
    'arxiv',
    'golden-query',
    'pubmed',
    'human',
    'awslambda',
    'stackexchange',
    'sceneXplain',
    'graphql',
    'openweathermap-api',
    'dataforseo-api-search',
    'dataforseo-api-search-json',
    'eleven_labs_text2speech',
    'google_cloud_texttospeech',
    'reddit_search',
    'news-api',
    'tmdb-api',
    'podcast-api',
    'memorize',
    'llm-math',
    'open-meteo-api']
"""
