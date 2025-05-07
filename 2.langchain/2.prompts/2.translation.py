from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()

template = "Translate the following English sentence into Korean:\n\n{sentence}"
prompt = PromptTemplate(input_variables=["sentence"], template=template)
llm = OpenAI(temperature=0.3)

chain = prompt | llm | RunnableLambda(lambda x: {"translated": x.strip()})

result = chain.invoke({"sentence": "The weather is nice today."})

print("Korean Translation:", result["translated"])
