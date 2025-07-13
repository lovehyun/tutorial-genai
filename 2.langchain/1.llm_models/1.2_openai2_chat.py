# https://python.langchain.com/docs/get_started/introduction
# https://python.langchain.com/docs/integrations/llms/openai

# pip install langchain langchain-openai
# 현재 시점의 버전
# langchain                 0.3.15
# langchain-community       0.3.15
# langchain-core            0.3.31
# langchain-openai          0.2.14

# | 클래스        | 모델 타입                  | 입력 타입                                                              | 설명                                             |
# | ------------ | -------------------------- | --------------------------------------------------------------------- | ------------------------------------------------ |
# | `OpenAI`     | Completion 모델 (문장 완성) | `str` (프롬프트)                                                       | 예: `text-davinci-003`, `gpt-3.5-turbo-instruct` |
# | `ChatOpenAI` | Chat 모델 (대화형)          | `List[BaseMessage]` (`HumanMessage`, `SystemMessage`, `AIMessage` 등) | 예: `gpt-3.5-turbo`, `gpt-4`, `gpt-4o`           |

import os
from dotenv import load_dotenv

from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage


# os.environ['OPENAI_API_KEY'] = 'OPENAI_API_KEY'
load_dotenv(dotenv_path='../.env')
openai_api_key = os.environ.get("OPENAI_API_KEY")

# temperature: 0~1 (0=deterministic, 1=randomness/creativity)
# default model: text-davinci-003 (deprecated - 2024.01)
#                gpt-3.5-turbo-instruct 가 기본값임.

# 모델: 문장완성모델(completion-model) vs 챗모델(chat-model)
print('--- 1 ---')
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.9)
print(llm)

prompt = "What's a good company name that makes arcade games?"
result = llm.invoke(prompt)
print(result)


# ChatOpenAI.invoke()는 내부적으로 문자열 입력을 HumanMessage로 자동 변환해줍니다.
print('--- 2 ---')
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.9)
print(llm)

# 즉, 아래 두개의 코드는 결과적으로 동일하게 처리 되지만 "명시적으로 작성" 하는 것이 더 좋은 형태입니다.
prompt = "What's a good company name that makes arcade games?"
result = llm.invoke(prompt)
print(result.content)

print('--- 3 ---')
prompt = [HumanMessage(content="What's a good company name that makes arcade games?")]
result = llm.invoke(prompt)
print(result.content)
