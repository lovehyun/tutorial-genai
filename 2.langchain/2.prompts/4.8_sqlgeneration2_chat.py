from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()

# Chat 형식 프롬프트 구성
chat_prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(
        "Generate a SQL query for the following request:\n\n{query}"
    )
])

# gpt-4o 모델 지정
llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

# 체인 구성
chain = chat_prompt | llm | RunnableLambda(lambda x: {"sql": x.content.strip()})

# 예시 입력
example_input = {
    "query": "List the names and emails of users who signed up after January 1, 2023."
}

# 실행
result = chain.invoke(example_input)

print("Generated SQL:", result["sql"])
