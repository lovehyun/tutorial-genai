import os
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 환경 변수 로드
load_dotenv()

# Claude 모델 초기화
llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0.7
)

# 프롬프트 템플릿 정의
prompt = PromptTemplate.from_template(
    "다음 주제에 대한 블로그 포스트의 개요를 5가지 항목으로 작성해주세요: {topic}"
)

# LCEL 체인 구성 (prompt | llm | parser)
chain = prompt | llm | StrOutputParser()

# 체인 실행
result = chain.invoke({"topic": "인공지능과 미래 직업"})
print(result)
