from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import CommaSeparatedListOutputParser

# Chat 버전: ChatPromptTemplate + ChatOpenAI + 출력 파서

load_dotenv()

# 1. 프롬프트 템플릿 설정 (결과 5개 요청)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a naming consultant for new companies."),
    ("user",
     "List 5 creative and catchy company names for a {company} that makes {product}.\n"
     "Return the names as a comma-separated list."),
])

# 2. ChatOpenAI 모델 정의
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.9)

# 3. 출력 파서 정의
parser = StrOutputParser()                       # AIMessage → 그냥 문자열
parser2 = CommaSeparatedListOutputParser()       # 문자열 → 리스트 (콤마 기준 split)

# 4. 입력 예제
inputs = {"company": "High Tech Startup", "product": "Web Game"}

# 5. LLM 실행 (프롬프트 → LLM → 후처리)
msgs = prompt.format_messages(**inputs)
ai_message = llm.invoke(msgs)            # AIMessage 객체
result_str = parser.invoke(ai_message)   # AIMessage → 문자열
result_csv = parser2.invoke(ai_message.content)  # 콤마 분리 리스트

# 6. 출력
print("\nRaw Output (String):")
print(result_str)

print("\nParsed Output (CSV to List):")
print(result_csv)
