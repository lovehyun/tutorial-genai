from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai.llms import OpenAI

load_dotenv()

# template = "너는 회사 이름을 짓기 위한 작명가야. {product}를 하기 위해 좋은 회사명은?"
# template = "You are a naming consultant for new companies. What is a good name for a company that makes {product}?"
template = "You are a naming consultant for new companies. What is a good name for a {company} that makes {product}?"

prompt = PromptTemplate.from_template(template)
# print(prompt.format(product="웹게임개발"))

llm = OpenAI(temperature=0.9)
chain = LLMChain(llm=llm, prompt=prompt)

# print(chain.run("웹게임개발"))
# print(chain.run({'company':'High Tech Startup', 'product':'Web Game'}))
print(chain.invoke({'company':'High Tech Startup', 'product':'Web Game'}))
