from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# 1. 환경 변수 로드
load_dotenv()

# 2. 메시지 기반 프롬프트 템플릿
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a naming consultant for new companies."),
    ("human", "What is a good name for a {company} that makes {product}?")
])

# 3. Chat LLM 모델 설정
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.9)
llm = ChatOpenAI(model="gpt-4o", temperature=0.9)

# 4. 후처리 파서 설정
parser = StrOutputParser()

# 5. 입력값 정의
inputs = {"company": "High Tech Startup", "product": "Web Game"}

# 6. 프롬프트 생성 (메시지 리스트 반환)
messages = prompt.format_messages(**inputs)  # ChatPromptTemplate 전용 메서드 (PromptTemplate에는 없음)

# 7. LLM 호출 (ChatOpenAI는 메시지 리스트를 받음)
response = llm.invoke(messages)

# 8. 후처리 (AIMessage 객체 → 문자열 파싱)
cleaned_output = parser.invoke(response)

# 9. 딕셔너리로 감싸기 (원래 RunnableLambda 했던 역할)
final_result = {"response": cleaned_output}

# 10. 출력
print("\nFinal Response:")
print(final_result["response"])

