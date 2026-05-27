from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# MessagesPlaceholder: 프롬프트 안에 "이 자리에는 대화 이력 메시지들이 끼워질 것" 이라는
# 슬롯(빈 자리)을 만들어 두는 도구. 이후 Memory / Agent 패턴으로 가는 다리.

load_dotenv()

# 1. 프롬프트 정의 — history 자리를 비워둔다
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Answer concisely in Korean."),
    MessagesPlaceholder(variable_name="history"),    # ← 여기 빈 자리
    ("human", "{input}"),
])

# 2. 호출할 때 history 자리에 메시지 리스트를 넘긴다
history = [
    HumanMessage(content="내 이름은 홍길동이야."),
    AIMessage(content="안녕하세요 홍길동님!"),
    HumanMessage(content="나는 서울에 살아."),
    AIMessage(content="서울에 사시는군요!"),
]

# 3. 펼쳐진 메시지 시퀀스 확인 — system + (history 4개) + 새 human
print("== 실제로 모델에 들어가는 메시지 시퀀스 ==")
formatted = prompt.format_messages(history=history, input="내 이름이랑 사는 곳이 뭐였지?")
for m in formatted:
    print(f"  [{m.type}] {m.content}")

# 4. LLM + 체인
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = prompt | llm | StrOutputParser()

# 5. 실행
result = chain.invoke({
    "history": history,
    "input": "내 이름이랑 사는 곳이 뭐였지?",
})
print(f"\n[모델 답변] {result}")

# 6. history 가 비어있을 때도 동작 (placeholder 는 빈 리스트 허용)
print("\n== history 가 빈 경우 ==")
result2 = chain.invoke({"history": [], "input": "안녕!"})
print(f"[모델 답변] {result2}")
