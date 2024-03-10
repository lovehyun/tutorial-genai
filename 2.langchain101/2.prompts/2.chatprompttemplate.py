from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai.llms import OpenAI
from langchain.chains import LLMChain

# https://python.langchain.com/docs/modules/model_io/output_parsers/types/structured
from langchain_core.output_parsers import CommaSeparatedListOutputParser


load_dotenv(dotenv_path='../.env')

# 1-1. 템플릿 셋업
template = "You are a cook. Answer the following question. <Q>: {input}?"
chat_prompt1 = ChatPromptTemplate.from_template(template)

print(chat_prompt1)
print(chat_prompt1.format(input='How is Kimchi made'))

# 1-2. 템플릿 셋업
system_template = "You are a professional language translator who translates {input_language} to {output_language}"
system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
human_message_prompt = HumanMessagePromptTemplate.from_template("{text}")

chat_prompt2 = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)
print(chat_prompt2.format_messages(input_language="영어", output_language="한국어", text="Hello"))

# 2. 모델 생성 및 연동
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.5)
llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.5)
chain1 = LLMChain(llm=llm, prompt=chat_prompt1)
chain2 = LLMChain(llm=llm, prompt=chat_prompt2)
chain3 = LLMChain(llm=llm, prompt=chat_prompt2, output_parser=CommaSeparatedListOutputParser())

# 3. 모델 실행
print(chain1.invoke({'input':'How is Kimchi made'}))
print(chain2.invoke({'input_language':'영어', 'output_language':'한국어', 'text':'Hello, Nice to meet you.'}))
print(chain3.invoke(dict(input_language='영어', output_language='한국어', text='Hello, Nice to meet you.')))
