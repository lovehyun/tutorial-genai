from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()

# ChatPromptTemplate 사용
chat_prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template("Summarize the following article in 3 sentences:\n\n{article}")
])

# ChatOpenAI로 gpt-4o 모델 설정
llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

# 체인 구성
chain = chat_prompt | llm | RunnableLambda(lambda x: {"summary": x.content.strip()})

input_text = {
    "article": "Artificial intelligence is transforming industries by automating tasks..."
}
result = chain.invoke(input_text)

print("Summary:", result["summary"])
