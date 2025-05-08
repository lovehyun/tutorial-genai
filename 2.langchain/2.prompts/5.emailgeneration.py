from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()

template = "Write a formal email to {recipient} requesting a meeting regarding {topic}."
prompt = PromptTemplate(input_variables=["recipient", "topic"], template=template)
llm = OpenAI(temperature=0.6, max_tokens=1024)

chain = prompt | llm | RunnableLambda(lambda x: {"email": x.strip()})

result = chain.invoke({"recipient": "the marketing team", "topic": "product launch strategy"})

print("Generated Email:\n", result["email"])


# 테스트용 팀 부서 및 주제 목록
recipients = [
    "the marketing team",
    "the product development team",
    "the HR department",
    "the finance team",
    "the executive board"
]

topics = [
    "product launch strategy",
    "quarterly performance review",
    "recruitment planning",
    "budget allocation for Q3",
    "company-wide policy update"
]

# 각 조합에 대해 이메일 생성
# for recipient in recipients:
#     for topic in topics:
#         print(f"\nTo: {recipient} | Topic: {topic}")
#         result = chain.invoke({"recipient": recipient, "topic": topic})
#         print(result["email"])
#         print("-" * 60)

# 일대일 매칭 실행
for recipient, topic in zip(recipients, topics):
    print(f"\nTo: {recipient} | Topic: {topic}")
    result = chain.invoke({"recipient": recipient, "topic": topic})
    print(result["email"])
    print("-" * 60)
