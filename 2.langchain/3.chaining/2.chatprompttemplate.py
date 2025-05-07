from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.runnables import RunnableLambda

# 환경 변수 로드 (경로 없이 실행하면 자동으로 .env 검색)
load_dotenv()

# 목적
# Chain1. 역할 기반 프롬프트 체인 예시 (요리사 역할)
# Chain2. 시스템 메시지와 사용자 메시지를 조합한 다국어 번역된 문자열 반환
# Chain3. Comma로 구분된 응답을 자동으로 리스트 형태로 반환하는 체인
# 즉, LangChain에서 다양한 ChatPrompt 구성 방식과 응답 후처리 방법을 학습하는 예제

# 1-1. 요리사 역할 프롬프트 설정
chat_prompt1 = ChatPromptTemplate.from_template(
    "You are a cook. Answer the following question. <Q>: {input}?"
)

# 1-2. OpenAI 모델 생성 및 연동
llm = ChatOpenAI(model="gpt-3.5-turbo-instruct", temperature=0.5)

# 1-3. 최신 LangChain 방식 적용 (RunnableSequence)
chain1 = chat_prompt1 | llm | RunnableLambda(lambda x: {"response": x.content})

# 1-4. 모델 실행
print(chain1.invoke({"input": "How is Kimchi made"})["response"])


# 2-1. 번역 프롬프트 설정 (시스템 메시지 + 사용자 입력)
system_template = "You are a professional language translator who translates {input_language} to {output_language}"
system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
human_message_prompt = HumanMessagePromptTemplate.from_template("{text}")

# 2-2. 시스템 + 사용자 메시지를 ChatPrompt로 묶기
chat_prompt2 = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)

# 2-3. 최신 LangChain 방식 적용 (RunnableSequence)
chain2 = chat_prompt2 | llm | RunnableLambda(lambda x: {"response": x.content})
chain3 = chat_prompt2 | llm | CommaSeparatedListOutputParser()

# 2-4. 모델 실행
print(chain2.invoke({"input_language": "영어", "output_language": "한국어", "text": "Hello, Nice to meet you."})["response"])
print(chain3.invoke({"input_language": "영어", "output_language": "한국어", "text": "Hello, Nice to meet you."}))
