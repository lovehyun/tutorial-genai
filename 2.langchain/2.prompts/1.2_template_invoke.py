from langchain_core.prompts import PromptTemplate

# You are a naming consultant for new companies. What is a good name for a High Tech Startup that makes Web Game?
# You are a naming consultant for new companies. What is a good name for a luxury brand that sells eco-friendly skincare products?
# You are a naming consultant for new companies. What is a good name for a robotics company that builds AI-powered home assistants?

# 1. 프롬프트 템플릿 정의
template = "You are a naming consultant. Suggest a name for a company that makes {product}."
prompt = PromptTemplate(
    input_variables=["product"],
    template=template
)

filled_prompt = prompt.format(product="robot toys")

print("Prompt 결과:")
print(filled_prompt)

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
    result = prompt.format(product=product)
    print(f"[{product}]\n{result}\n")

print("\n-----\n")


# 4. OpenAI LLM 초기화
from langchain_openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
llm = OpenAI(temperature=0.8)  # gpt-3.5-turbo-instruct 기본 사용됨

# 5. 추론
for product in test_products:
    final_prompt = prompt.format(product=product)
    print(f"[{product}] {final_prompt}\n")

    response = llm.invoke(filled_prompt)
    print(f"Response: {response.strip()}\n")
