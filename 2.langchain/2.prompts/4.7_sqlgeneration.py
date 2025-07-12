from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()

template = "Generate a SQL query for the following request:\n\n{query}"
prompt = PromptTemplate(input_variables=["query"], template=template)
llm = OpenAI(temperature=0.3)

chain = prompt | llm | RunnableLambda(lambda x: {"sql": x.strip()})

example_input = {
    "query": "List the names and emails of users who signed up after January 1, 2023."
}
result = chain.invoke(example_input)

print("Generated SQL:", result["sql"])
