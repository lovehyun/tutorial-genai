from langchain_core.prompts import PromptTemplate

template = "You are a naming consultant. Suggest a name for a company that makes {product}."
prompt = PromptTemplate(
    input_variables=["product"],
    template=template
)

from langchain_openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
llm = OpenAI(temperature=0.8)  # gpt-3.5-turbo-instruct 기본 사용됨

print("새 회사 이름 생성기입니다. 종료하려면 'quit', 'exit', 또는 'q'를 입력하세요.\n")

while True:
    # 3. 사용자 입력 받기
    product = input("제품/서비스를 입력하세요: ").strip()
    if product.lower() in {"quit", "exit", "q"}:
        print("프로그램을 종료합니다.")
        break

    if not product:
        print("빈 값은 처리할 수 없습니다. 다시 입력해주세요.\n")
        continue

    # 4. 프롬프트 채우기 및 LLM 호출
    filled_prompt = prompt.format(product=product)
    try:
        response = llm.invoke(filled_prompt)
        print(f"추천 회사 이름: {response.strip()}\n")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}\n")
