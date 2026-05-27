from langchain_core.prompts import ChatPromptTemplate

# Chat 버전: 사용자 입력을 받아 ChatOpenAI 호출

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a naming consultant for new companies."),
    ("user",   "Suggest a name for a company that makes {product}."),
])

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)

print("새 회사 이름 생성기입니다 (Chat 버전). 종료하려면 'quit', 'exit', 또는 'q'를 입력하세요.\n")

while True:
    # 1. 사용자 입력 받기
    product = input("제품/서비스를 입력하세요: ").strip()
    if product.lower() in {"quit", "exit", "q"}:
        print("프로그램을 종료합니다.")
        break

    if not product:
        print("빈 값은 처리할 수 없습니다. 다시 입력해주세요.\n")
        continue

    # 2. 메시지 만들고 LLM 호출 (AIMessage 반환)
    msgs = prompt.format_messages(product=product)
    try:
        response = llm.invoke(msgs)
        print(f"추천 회사 이름: {response.content.strip()}\n")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}\n")
