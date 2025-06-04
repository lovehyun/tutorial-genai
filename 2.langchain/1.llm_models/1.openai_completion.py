# https://python.langchain.com/docs/get_started/introduction
# https://python.langchain.com/docs/integrations/llms/openai

# pip install langchain langchain-openai
# 현재 시점의 버전
# langchain                 0.3.15
# langchain-community       0.3.15
# langchain-core            0.3.31
# langchain-openai          0.2.14

import os
from dotenv import load_dotenv

# from langchain.llms import OpenAI  # 구버전
from langchain_openai import OpenAI  # 신버전


# os.environ['OPENAI_API_KEY'] = 'OPENAI_API_KEY'

load_dotenv(dotenv_path='../.env')
openai_api_key = os.environ.get("OPENAI_API_KEY")


# temperature: 0~1 (0=deterministic, 1=randomness/creativity)
# default model: text-davinci-003 (deprecated - 2024.01)
#                gpt-3.5-turbo-instruct 가 기본값임.

# 모델: 문장완성모델(completion-model) vs 챗모델(chat-model)
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.9)
llm = OpenAI(temperature=0.9)
print(llm)

prompt = "What's a good company name that makes arcade games?"
result = llm.invoke(prompt) # 단일건 처리 = invoke
print(result)

# result = llm.generate([prompt]*5) # 다중건(batch) 처리 = generate
# for company_name in result.generations:
#     print(company_name[0].text)
