"""
기본 체인 + 결과 후처리 RunnableLambda

체인 끝에 RunnableLambda 를 붙여서 결과를 가공할 수 있습니다.
여기서는 문자열 답변을 {"response": ...} 형태의 dict 로 감싸봅니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 어시스턴트입니다."),
    ("user", "{question}"),
])

chain = (
    prompt
    | llm
    | StrOutputParser()
    | RunnableLambda(lambda x: {"response": x.strip()})  # 추가된 한 줄
)

result = chain.invoke({"question": "파이썬이 뭐야? 한 줄로 답해줘."})
print(type(result))
print(result)
print(result["response"])
