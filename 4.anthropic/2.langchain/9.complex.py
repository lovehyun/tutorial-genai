import os
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# Claude 모델 초기화
llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0.7
)
parser = StrOutputParser()

# 첫 번째 체인: 주제 → 질문 생성
questions_prompt = PromptTemplate.from_template(
    "다음 주제와 관련된 5가지 중요한 질문을 생성해주세요: {topic}"
)
questions_chain = questions_prompt | llm | parser

# 두 번째 체인: 질문 → 답변
answers_prompt = PromptTemplate.from_template(
    "다음 질문들에 대한 답변을 제공해주세요:\n\n{questions}"
)
answers_chain = answers_prompt | llm | parser

# 세 번째 체인: 질문 + 답변 → 최종 요약
summary_prompt = PromptTemplate.from_template(
    "다음 질문들과 답변을 바탕으로 종합적인 요약을 작성해주세요:\n\n"
    "질문들:\n{questions}\n\n답변들:\n{answers}"
)
summary_chain = summary_prompt | llm | parser

# LCEL 순차 파이프라인: 중간 결과를 다음 단계로 전달
overall_chain = (
    {"topic": RunnablePassthrough()}
    | RunnablePassthrough.assign(questions=questions_chain)
    | RunnablePassthrough.assign(answers=answers_chain)
    | summary_chain
)

# 실행
result = overall_chain.invoke("인공지능과 교육의 미래")
print("\n최종 요약:")
print(result)
