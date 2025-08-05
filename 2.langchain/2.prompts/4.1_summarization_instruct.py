from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate

from langchain_openai import OpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()

template = "Summarize the following article in 3 sentences:\n\n{article}"
prompt = PromptTemplate(input_variables=["article"], template=template)
llm = OpenAI(temperature=0.5)
# llm = OpenAI(model="gpt-4o-mini", temperature=0.5)
print(llm)

# 줄 단위 정리 함수 (람다)
process_lines = RunnableLambda(
    lambda x: {
        "summary": [line.strip() for line in x.strip().split('\n') if line.strip()]
    }
)

# chain = prompt | llm | process_lines
chain = prompt | llm | RunnableLambda(lambda x: {"summary": x.strip()})

input_text = {
    "article": "Artificial intelligence is transforming industries by automating tasks..."
}
result = chain.invoke(input_text)

print("Summary:", result)
# print("Summary:", result["summary"])

# lines = result["summary"].split('\n')
# for line in lines:
#     cleaned = line.strip()
#     if cleaned:  # 빈 줄 무시
#         print(cleaned)
