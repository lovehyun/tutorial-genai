# pip install langchain_experimental

from dotenv import load_dotenv

from langchain_openai.llms import OpenAI
from langchain_openai.chat_models import ChatOpenAI
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from langchain_community.utilities import GoogleSerperAPIWrapper, WikipediaAPIWrapper
from langchain.chains import LLMMathChain
from langchain.agents.tools import Tool

load_dotenv()

llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.1)
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)
search = GoogleSerperAPIWrapper()
wikipedia = WikipediaAPIWrapper()

tools = [
    Tool(
        name="Search",
        func=search.run,
        description = "userful for when you need to answer questions about current events"
    ),
    Tool(
        name="Wikipedia",
        func=wikipedia.run,
        description = "useful for when you need to look up facts and statistics"
    ),
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description = "useful for when you need to answer questions about math"
    ),
]

prompt = "Where are the next summer olympics going to be hosted? What is the population of that country divided by 2?"

# 기본적으로 openai 는 memory 기능이 없어 이전 대화 내용을 기억하지 않음.
# 그래서 chatopenai 기능을 통해 대화 내용을 기억하도록 구성.
# planner and executor 를 사용해서 최종 답변을 구하기까지 필요한 부분들을 구성.
model = ChatOpenAI(temperature=0.1)

planner = load_chat_planner(model)
executor = load_agent_executor(model, tools, verbose=True)
agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)

agent.invoke(prompt)
