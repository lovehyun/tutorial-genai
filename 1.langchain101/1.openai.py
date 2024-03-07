# https://python.langchain.com/docs/integrations/llms/openai

# pip install langchain langchain-openai
# 현재 시점의 버전
# langchain                0.1.11
# langchain-community      0.0.27
# langchain-core           0.1.30

import os
from dotenv import load_dotenv

# from langchain.llms import OpenAI
from langchain_openai import OpenAI

load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")

# temperature: 0~1 (0=deterministic, 1=randomness/creativity)
# default model: text-davinci-003 (deprecated - 2024.01)
#                gpt-3.5-turbo-instruct 가 기본값임.

llm = OpenAI(temperature=0.9)
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.9)
print(llm)

prompt = "What's a good company name that makes arcade games?"
# print(llm(prompt))

result = llm.generate([prompt]*5)
for company_name in result.generations:
    print(company_name[0].text)
