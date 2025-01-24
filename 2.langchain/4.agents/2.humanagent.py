from dotenv import load_dotenv

from langchain_openai.llms import OpenAI
from langchain.agents import load_tools, initialize_agent, AgentType


load_dotenv(dotenv_path='../.env')

llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.1)
tools = load_tools(['human'])

agent_chain = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

agent_chain.run("What's my nickname?")
