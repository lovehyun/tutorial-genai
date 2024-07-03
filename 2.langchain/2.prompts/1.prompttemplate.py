from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai.llms import OpenAI


load_dotenv(dotenv_path='../.env')

# 1-1. 템플릿 셋업
template = "Tell me about {input}"
prompt = PromptTemplate.from_template(template)
print(prompt.format(input='Seoul'))
print(prompt.format(input='Busan'))

# 1-2. 템플릿 셋업
template = "너는 회사 이름을 짓기 위한 작명가야. {product}를 하기 위해 좋은 회사명은?"
template = "You are a naming consultant for new companies. What is a good name for a company that makes {product}?"
template = "You are a naming consultant for new companies. What is a good name for a {company} that makes {product}?"

prompt = PromptTemplate.from_template(template)
# print(prompt.format(product="웹게임개발"))

# 2. 모델 생성 및 연동
llm = OpenAI(temperature=0.9)
chain = LLMChain(llm=llm, prompt=prompt)

# 3. 모델 실행
# print(chain.run("웹게임개발"))
# print(chain.run({'company':'High Tech Startup', 'product':'Web Game'}))
# chain.run is deprecated -> use chain.invoke
# print(chain.invoke('Seoul'))
# print(chain.invoke({'input':'Busan'}))
print(chain.invoke({'company':'High Tech Startup', 'product':'Web Game'}))
print(chain.invoke({'company':'High Tech Startup', 'product':'Web Game'})['text'].strip())
