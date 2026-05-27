from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory


# 0. API 키 불러오기
load_dotenv()

# 1. LLM 구성
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 2. 메모리 구성 (최근 3턴만 기억)
memory = ConversationBufferWindowMemory( # - v0.2.7부터 사용 중단(deprecated)
    memory_key="history",
    return_messages=True,
    k=3  # 최근 대화 3개만 유지
)

# 3. 프롬프트 정의
# prompt = ChatPromptTemplate.from_messages([
#     ("system", "너는 기억력이 좋은 챗봇이야."),
#     MessagesPlaceholder(variable_name="history"),
#     ("human", "{input}")
# ])

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("너는 기억력이 좋은 챗봇이야."),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

# 4. 체인 정의
chain = prompt | llm | StrOutputParser()

# 5. 대화 진행 (수동으로 memory 호출)
conversation = [
    "안녕, 나는 홍길동이야.",
    "내 나이는 35살이야.",
    "내 취미는 등산이야.",
    "나는 몇살이고 무슨 취미를 좋아한다고 했더라?"
]

for question in conversation:
    # 메모리에서 이전 기록 불러오기
    history_vars = memory.load_memory_variables({})
    print(history_vars) # 대화 내용은 전부 기억되지만, history 에서 사용되는건 k개만큼 사용
    
    # 체인 실행
    output = chain.invoke({**history_vars, "input": question})
    
    # 출력
    print(f"\nHuman: {question}")
    print(f"AI: {output}")
    
    # 결과를 메모리에 저장
    memory.save_context({"input": question}, {"output": output})

print("총 누적 메시지:", len(memory.chat_memory.messages))
print("윈도우 메시지:", len(memory.load_memory_variables({})["history"]))
