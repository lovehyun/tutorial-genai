# https://python.langchain.com/docs/modules/agents/

# pip install wikipedia numexpr

from dotenv import load_dotenv

import pprint

from langchain_openai.llms import OpenAI
# from langchain.agents import get_all_tool_names
from langchain.agents import load_tools, initialize_agent, AgentType

load_dotenv()

# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(get_all_tool_names())

prompt = "대한민국의 공휴일 날짜들은? 그리고 이 날짜들의 월과 일의 숫자들의 합산은?"

llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.9)
tools = load_tools(['wikipedia', 'llm-math'], llm=llm)

agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

agent.run(prompt)


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
