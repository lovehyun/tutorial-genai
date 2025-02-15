from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.runnables import RunnableLambda

# 환경 변수 로드 (경로 없이 실행하면 자동으로 .env 검색)
load_dotenv()

# 1. 요리사 역할 프롬프트 설정
chat_prompt1 = ChatPromptTemplate.from_template(
    "You are a cook. Answer the following question. <Q>: {input}?"
)

# 2. OpenAI 모델 생성 및 연동
llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.5)

# 3. 최신 LangChain 방식 적용 (RunnableSequence)
chain1 = chat_prompt1 | llm | RunnableLambda(lambda x: {"response": x.content})

# 4. 모델 실행
print(chain1.invoke({"input": "How is Kimchi made"})["response"])


# 1-2. 번역 프롬프트 설정 (시스템 메시지 + 사용자 입력)
system_template = "You are a professional language translator who translates {input_language} to {output_language}"
system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
human_message_prompt = HumanMessagePromptTemplate.from_template("{text}")

chat_prompt2 = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)

# 3-2. 최신 LangChain 방식 적용 (RunnableSequence)
chain2 = chat_prompt2 | llm | RunnableLambda(lambda x: {"response": x.content})
chain3 = chat_prompt2 | llm | CommaSeparatedListOutputParser()

# 4-2. 모델 실행
print(chain2.invoke({"input_language": "영어", "output_language": "한국어", "text": "Hello, Nice to meet you."})["response"])
print(chain3.invoke({"input_language": "영어", "output_language": "한국어", "text": "Hello, Nice to meet you."}))
