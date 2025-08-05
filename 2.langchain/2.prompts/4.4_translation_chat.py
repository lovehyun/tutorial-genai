from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()

# 프롬프트 템플릿 (Chat 메시지 형식)
chat_prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(
        "Translate the following English sentence into Korean:\n\n{sentence}"
    )
])

# gpt-4o 모델 사용
llm = ChatOpenAI(model="gpt-4o", temperature=0.3, max_tokens=1024)

# 체인 구성
chain = chat_prompt | llm | RunnableLambda(lambda x: {"translated": x.content.strip()})

# 실행 예시
print('--- 1 ---')
short_sentence = "The weather is nice today."
result = chain.invoke({"sentence": short_sentence})

print("Korean Translation:", result["translated"])


print('--- 2 ---')
long_sentence = (
    "Despite the ongoing economic uncertainties around the world, "
    "many experts believe that the adoption of green energy solutions "
    "will continue to grow rapidly in the next decade, particularly "
    "as governments invest more in sustainable infrastructure."
)

result = chain.invoke({"sentence": long_sentence})

print("Korean Translation:", result["translated"])
