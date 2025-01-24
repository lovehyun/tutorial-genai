from dotenv import load_dotenv

from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain, SimpleSequentialChain


load_dotenv(dotenv_path='../.env')

llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.9)

template1 = "You are a naming consultant for new companies. What is a good name for a company that makes {product}?"
prompt1 = PromptTemplate.from_template(template1)
chain1 = LLMChain(llm=llm, prompt=prompt1)

template2 = "Write a catch phrase for the following company: {company_name}"
prompt2 = PromptTemplate.from_template(template2)
chain2 = LLMChain(llm=llm, prompt=prompt2)

chains = SimpleSequentialChain(chains=
                               [chain1, chain2], verbose=True)

catch_phrase = chains.invoke("웹게임")
print(catch_phrase)
