import os
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# 환경 변수 로드
load_dotenv()

# Claude 모델 초기화
llm = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0.7
)

# 프롬프트 템플릿 정의
prompt_template = PromptTemplate(
    input_variables=["topic"],
    template="다음 주제에 대한 블로그 포스트의 개요를 5가지 항목으로 작성해주세요: {topic}"
)

# 체인 생성
blog_outline_chain = LLMChain(
    llm=llm,
    prompt=prompt_template,
    verbose=True  # 실행 과정을 출력
)

# 체인 실행
result = blog_outline_chain.invoke({"topic": "인공지능과 미래 직업"})
print(result["text"])  # 결과 출력
