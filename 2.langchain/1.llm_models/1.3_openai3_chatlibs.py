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

from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage


# os.environ['OPENAI_API_KEY'] = 'OPENAI_API_KEY'
load_dotenv(dotenv_path='../.env')
openai_api_key = os.environ.get("OPENAI_API_KEY")

# temperature: 0~1 (0=deterministic, 1=randomness/creativity)
# default model: text-davinci-003 (deprecated - 2024.01)
#                gpt-3.5-turbo-instruct 가 기본값임.

# 모델: 문장완성모델(completion-model) vs 챗모델(chat-model)
print('--- 1 ---')
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.9)

print('--- 2 ---')
prompt = "What's a good company name that makes arcade games?"
result = llm.invoke(prompt)
print(result)


print('--- 3 ---')
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.9)
print(llm)

prompt = "What's a good company name that makes arcade games?"
result = llm.invoke(prompt) # 바로 문자열(str) 을 넣어도 내부적으로는 HumanMessage() 로 변환됨
print(result.content)


print('--- 4 ---')
messages = [HumanMessage(content="안녕!")]
print(messages)

result = llm.invoke(messages)
print(result.content)


print('--- 5 ---')
# 메시지 구성
messages = [
    SystemMessage(content="너는 매우 유쾌한 농담을 잘하는 AI야."),
    HumanMessage(content="재미있는 회사 이름 하나만 지어줘."),
    AIMessage(content="그럼... '퍼니컴퍼니' 어때?"),
    HumanMessage(content="하나만 더!")
]

result = llm.invoke(messages)
print(result.content)
