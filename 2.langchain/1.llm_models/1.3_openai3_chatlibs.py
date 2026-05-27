# https://python.langchain.com/docs/get_started/introduction
# https://python.langchain.com/docs/integrations/llms/openai

# pip install langchain langchain-openai
# 현재 시점의 버전
# langchain                 1.2.15
# langchain-community       0.4.1
# langchain-core            1.3.2
# langchain-openai          1.2.1

import os
from dotenv import load_dotenv

from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


# os.environ['OPENAI_API_KEY'] = 'OPENAI_API_KEY'
load_dotenv(dotenv_path='../.env')
openai_api_key = os.environ.get("OPENAI_API_KEY")

# temperature: 0~1 (0=deterministic, 1=randomness/creativity)
# default model: text-davinci-003 (deprecated - 2024.01)
#                gpt-3.5-turbo-instruct 가 기본값임.

# 모델: 문장완성모델(completion-model) vs 챗모델(chat-model)


# 1. Legacy Completion 모델 인스턴스 생성 — `OpenAI` 클래스 + gpt-3.5-turbo-instruct (/v1/completions 엔드포인트)
print('--- 1 ---')
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.9)


# 2. Completion 방식으로 호출 — 입력은 단일 문자열, 출력도 그냥 문자열 (.content 불필요)
print('--- 2 ---')
prompt = "What's a good company name that makes arcade games?"
result = llm.invoke(prompt)
print(result)


# 3. `ChatOpenAI` 로 전환 — 문자열만 넣어도 동작(내부적으로 HumanMessage 변환)하지만, 결과는 AIMessage 객체라서 .content 로 꺼내야 함
print('--- 3 ---')
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.9)
print(llm)

prompt = "What's a good company name that makes arcade games?"
result = llm.invoke(prompt) # 바로 문자열(str) 을 넣어도 내부적으로는 HumanMessage() 로 변환됨
print(result.content)


# 4. Chat 모델의 본래 입력 형식 보여주기 — [HumanMessage(...)] 형태로 명시적 메시지 리스트 구성
print('--- 4 ---')
messages = [HumanMessage(content="안녕!")]
print(messages)

result = llm.invoke(messages)
print(result.content)


# 5. Chat 모델의 진가 — System/Human/AI 메시지를 교차 배치해 멀티턴 대화 컨텍스트를 시뮬레이션 ("하나만 더!"가 앞 맥락 덕에 해석됨)
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
