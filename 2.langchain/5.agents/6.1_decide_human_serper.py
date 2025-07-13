from dotenv import load_dotenv
import os
from langchain_openai import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper

# 환경 변수 로드
load_dotenv()

# OpenAI 모델 초기화
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.1)

# 1. 커스텀 human 도구 정의
def custom_human_input(prompt):
    print(f"\n👤 사용자에게 질문합니다: {prompt}")
    return input("당신의 답변을 입력해주세요: ")

human_tool = Tool(
    name="Human Input",
    func=custom_human_input,
    description="사용자의 개인 정보나 선호도에 관한 질문에 답변이 필요할 때만 사용합니다. 예: 이름, 나이, 취향, 직업 등 사용자만 알 수 있는 정보."
)

# 2. Google Serper 검색 도구 설정
serper_api_key = os.getenv("SERPER_API_KEY")
if not serper_api_key:
    raise ValueError("SERPER_API_KEY가 환경 변수에 설정되어 있지 않습니다. .env 파일에 추가해주세요.")

search = GoogleSerperAPIWrapper()
search_tool = Tool(
    name="Google Search",
    func=search.run,
    description="최신 정보, 뉴스, 일반적인 질문, 사실 확인 등이 필요할 때 사용합니다. 검색어를 입력하세요."
)

# 3. 도구 선택 지침을 포함하는 시스템 메시지
system_message = """질문에 따라 적절한 도구를 선택하세요:
1. 사용자의 개인정보(이름, 취향, 직업 등)는 반드시 'Human Input' 도구를 사용하세요.
2. 사실 확인, 뉴스, 일반 지식에는 'Google Search' 도구를 사용하세요.
3. 가능하면 사용자에게 불필요하게 질문하지 마세요."""

# 4. 에이전트 초기화 - 모든 도구 제공
agent_chain = initialize_agent(
    tools=[human_tool, search_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={"system_message": system_message}
)

# 5. 실행
user_question = input("질문을 입력하세요: ")
result = agent_chain.invoke({"input": user_question})
print("\n최종 결과:", result["output"])
