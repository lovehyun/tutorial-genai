from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()

template = "Write a formal email to {recipient} requesting a meeting regarding {topic}."
prompt = PromptTemplate(input_variables=["recipient", "topic"], template=template)
llm = OpenAI(temperature=0.6)

chain = prompt | llm | RunnableLambda(lambda x: {"email": x.strip()})

result = chain.invoke({"recipient": "the marketing team", "topic": "product launch strategy"})

print("Generated Email:\n", result["email"])
