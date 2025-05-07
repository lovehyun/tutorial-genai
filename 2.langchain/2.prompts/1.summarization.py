from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()

template = "Summarize the following article in 3 sentences:\n\n{article}"
prompt = PromptTemplate(input_variables=["article"], template=template)
llm = OpenAI(temperature=0.5)

chain = prompt | llm | RunnableLambda(lambda x: {"summary": x.strip()})

input_text = {
    "article": "Artificial intelligence is transforming industries by automating tasks..."
}
result = chain.invoke(input_text)

print("Summary:", result["summary"])
