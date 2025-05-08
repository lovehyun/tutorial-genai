from dotenv import load_dotenv

from langchain_openai import OpenAI

from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

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

# 번역 체인 설정
template = "Translate the following English text into Korean:\n\n{text}"
prompt = PromptTemplate(input_variables=["text"], template=template)
translator = OpenAI(temperature=0.3, max_tokens=1024)  # 긴 문장을 위해 max_tokens 증가
translate_chain = prompt | translator | RunnableLambda(lambda x: x.strip())

# 검색 및 번역 실행
# user_query = input("검색할 내용을 입력하세요: ")
user_query = "서울의 오늘 날씨는 어때?"

# 검색 실행
search_result = agent.invoke({"input": user_query})
print("\n[검색 결과 (원문)]:\n", search_result["output"])

# 번역 실행
translated = translate_chain.invoke({"text": search_result["output"]})
print("\n[번역 결과]:\n", translated)
