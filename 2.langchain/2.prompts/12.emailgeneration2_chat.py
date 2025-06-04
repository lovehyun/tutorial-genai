from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()

# 메시지 프롬프트 구성
chat_prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(
        "Write a formal email to {recipient} requesting a meeting regarding {topic}."
    )
])

# gpt-4o 모델 사용
llm = ChatOpenAI(model="gpt-4o", temperature=0.6, max_tokens=1024)

# 체인 구성
chain = chat_prompt | llm | RunnableLambda(lambda x: {"email": x.content.strip()})

# 예시 데이터
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

# 일대일 매칭 실행
for recipient, topic in zip(recipients, topics):
    print(f"\nTo: {recipient} | Topic: {topic}")
    result = chain.invoke({"recipient": recipient, "topic": topic})
    print(result["email"])
    print("-" * 60)
