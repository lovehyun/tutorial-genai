# 필요한 패키지 설치
# pip install -U langchain_openai langchain_experimental langchain_community

from dotenv import load_dotenv
from langchain_openai import OpenAI, ChatOpenAI
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from langchain_community.utilities import GoogleSerperAPIWrapper, WikipediaAPIWrapper
from langchain.chains import LLMMathChain
from langchain.tools import Tool

# 환경 변수 로드
load_dotenv()

# 1. OpenAI 모델 설정
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.1)
chat_model = ChatOpenAI(temperature=0.1)  # 메모리 기능을 위해 ChatOpenAI 사용

# 2. 검색 및 계산 도구 설정
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)
search = GoogleSerperAPIWrapper()
wikipedia = WikipediaAPIWrapper()

# 3. LangChain 도구 설정
tools = [
    Tool(
        name="Search",
        func=search.run,
        description="Useful for answering questions about current events."
    ),
    Tool(
        name="Wikipedia",
        func=wikipedia.run,
        description="Useful for looking up facts and statistics."
    ),
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="Useful for answering math-related questions."
    ),
]

# 4. LangChain 에이전트 설정
planner = load_chat_planner(chat_model) 
executor = load_agent_executor(chat_model, tools, verbose=True)
agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)

# 5. 프롬프트 실행
prompt = "Where are the next summer olympics going to be hosted? What is the population of that country divided by 2?"
result = agent.invoke(prompt)

# 6. 결과 출력
print(result)
