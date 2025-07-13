from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate

from langchain_openai import OpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()

template = "Translate the following English sentence into Korean:\n\n{sentence}"
prompt = PromptTemplate(input_variables=["sentence"], template=template)
# llm = OpenAI(temperature=0.3)
llm = OpenAI(temperature=0.3, max_tokens=1024)  # 긴 문장이 짤리면, 기본값은 보통 256 이하일 수 있음

chain = prompt | llm | RunnableLambda(lambda x: {"translated": x.strip()})

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
