import os
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage, AIMessage

# 환경 변수 로드
load_dotenv()

# Claude 모델 초기화
llm = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0.7
)

# 단순 텍스트 프롬프트 템플릿
template = PromptTemplate.from_template("다음 주제에 대해 설명해주세요: {topic}")
formatted_prompt = template.format(topic="블록체인 기술")

response = llm.invoke(formatted_prompt)
print(response.content)

# 새로운 방식 (파이프)
# chain = template | llm
# response = chain.invoke({"topic": "블록체인 기술"})


# 채팅 프롬프트 템플릿
chat_template = ChatPromptTemplate.from_messages([
    SystemMessage(content="당신은 {role} 전문가입니다. 질문에 자세히 답변해주세요."),
    HumanMessage(content="다음 개념에 대해 설명해주세요: {concept}")
])

formatted_chat_prompt = chat_template.format_messages(
    role="인공지능",
    concept="강화학습"
)

response = llm.invoke(formatted_chat_prompt)
print(response.content)
