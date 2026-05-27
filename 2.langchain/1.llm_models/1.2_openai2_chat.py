# https://python.langchain.com/docs/get_started/introduction
# https://python.langchain.com/docs/integrations/llms/openai

# pip install langchain langchain-openai
# 현재 시점의 버전
# langchain                 1.2.15
# langchain-community       0.4.1
# langchain-core            1.3.2
# langchain-openai          1.2.1

# | 클래스        | 모델 타입                  | 입력 타입                                                              | 설명                                             |
# | ------------ | -------------------------- | --------------------------------------------------------------------- | ------------------------------------------------ |
# | `OpenAI`     | Completion 모델 (문장 완성) | `str` (프롬프트)                                                       | 예: `text-davinci-003`, `gpt-3.5-turbo-instruct` |
# | `ChatOpenAI` | Chat 모델 (대화형)          | `List[BaseMessage]` (`HumanMessage`, `SystemMessage`, `AIMessage` 등) | 예: `gpt-4o-mini`, `gpt-4`, `gpt-4o`           |

import os
from dotenv import load_dotenv

from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI


# os.environ['OPENAI_API_KEY'] = 'OPENAI_API_KEY'
load_dotenv(dotenv_path='../.env')
openai_api_key = os.environ.get("OPENAI_API_KEY")

# temperature: 0~1 (0=deterministic, 1=randomness/creativity)
# default model: text-davinci-003 (deprecated - 2024.01)
#                gpt-3.5-turbo-instruct 가 기본값임.

# 모델: 문장완성모델(completion-model) vs 챗모델(chat-model)


# 1. Legacy Completion 방식 — `OpenAI` 클래스 + gpt-3.5-turbo-instruct 로 단일 문자열 prompt → 문자열 결과
print('--- 1 ---')
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.9, api_key=openai_api_key)
print(llm)

prompt = "What's a good company name that makes arcade games?"
result = llm.invoke(prompt)
print(result)


# 2. `ChatOpenAI`에 문자열을 그대로 넣어 호출 — 내부적으로 HumanMessage 로 자동 변환되고, 반환은 AIMessage 객체(.content 로 꺼내야 함)
print('--- 2 ---')
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.9)
print(llm)

# 즉, 아래 두개의 코드는 결과적으로 동일하게 처리 되지만 "명시적으로 작성" 하는 것이 더 좋은 형태입니다.
prompt = "What's a good company name that makes arcade games?"
result = llm.invoke(prompt)
print(result.content)


# 3. 메시지 객체(HumanMessage / SystemMessage)로 명시적으로 입력 구성 — Chat 모델의 본래 입력 형식 보여주기
print('--- 3 ---')
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

prompt1 = [
    HumanMessage(content="What's a good company name that makes arcade games?")
    # HumanMessage(content="아케이드 게임을 만드는 좋은 회사 이름을 지어줘.")
]
prompt2 = [
    SystemMessage(content="You are a creative branding expert for game companies."),
    HumanMessage(content="What's a good company name that makes arcade games?")
    # SystemMessage(content="당신은 창의적인 게임 회사 작명 전문가입니다."),
    # HumanMessage(content="아케이드 게임을 만드는 좋은 회사 이름을 지어줘.")
]

result = llm.invoke(prompt1)
print(result.content)
