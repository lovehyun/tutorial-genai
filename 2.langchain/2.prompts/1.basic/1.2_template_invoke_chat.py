from langchain_core.prompts import ChatPromptTemplate

# Chat 버전: ChatPromptTemplate + ChatOpenAI 로 .invoke() 호출

# 1. 프롬프트 템플릿 정의 (system + user)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a naming consultant for new companies."),
    ("user",   "Suggest a name for a company that makes {product}."),
])

filled_messages = prompt.format_messages(product="robot toys")

print("Prompt 결과:")
for m in filled_messages:
    print(f"  [{m.type}] {m.content}")

# 2. 프롬프트 템플릿 반복 활용
print("\n-----\n")
test_products = [
    "mobile games",
    "robot toys",
    "eco-friendly packaging",
    "language learning platforms",
    "electric bikes"
]

# 3. 프롬프트 확인
for product in test_products:
    msgs = prompt.format_messages(product=product)
    print(f"[{product}]")
    for m in msgs:
        print(f"  [{m.type}] {m.content}")
    print()

print("\n-----\n")


# 4. ChatOpenAI 초기화
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)

# 5. 추론 — chat 모델은 메시지 리스트를 입력으로 받고 AIMessage 객체를 반환
for product in test_products:
    msgs = prompt.format_messages(product=product)
    print(f"[{product}] {msgs[-1].content}\n")

    response = llm.invoke(msgs)        # AIMessage 반환
    print(f"Response: {response.content.strip()}\n")
