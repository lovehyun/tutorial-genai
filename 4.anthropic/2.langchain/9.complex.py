import os
from dotenv import load_dotenv

from langchain.chains import SequentialChain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain.memory import ConversationBufferMemory

load_dotenv()

# Claude 모델 초기화
llm = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0.7
)

# 첫 번째 체인: 주제 확장
first_prompt = PromptTemplate(
    input_variables=["topic"],
    template="다음 주제와 관련된 5가지 중요한 질문을 생성해주세요: {topic}"
)

questions_chain = LLMChain(
    llm=llm,
    prompt=first_prompt,
    output_key="questions",  # 출력 키 정의
    verbose=True
)

# 두 번째 체인: 질문에 대한 답변
second_prompt = PromptTemplate(
    input_variables=["questions"],
    template="다음 질문들에 대한 답변을 제공해주세요:\n\n{questions}"
)

answers_chain = LLMChain(
    llm=llm,
    prompt=second_prompt,
    output_key="answers",
    verbose=True
)

# 세 번째 체인: 최종 요약
third_prompt = PromptTemplate(
    input_variables=["questions", "answers"],
    template="다음 질문들과 답변을 바탕으로 종합적인 요약을 작성해주세요:\n\n질문들:\n{questions}\n\n답변들:\n{answers}"
)

summary_chain = LLMChain(
    llm=llm,
    prompt=third_prompt,
    output_key="summary",
    verbose=True
)

# 순차적 체인 구성
overall_chain = SequentialChain(
    chains=[questions_chain, answers_chain, summary_chain],
    input_variables=["topic"],
    output_variables=["questions", "answers", "summary"],
    verbose=True
)

# 체인 실행
result = overall_chain.invoke({"topic": "인공지능과 교육의 미래"})

print("\n최종 요약:")
print(result["summary"])
