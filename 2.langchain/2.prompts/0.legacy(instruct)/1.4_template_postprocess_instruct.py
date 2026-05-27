from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate

from langchain_openai import OpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import CommaSeparatedListOutputParser

# 환경 변수 로드 (경로 없이 실행하면 자동으로 .env 검색)
load_dotenv()

# 1. 프롬프트 템플릿 설정 (결과 5개 요청)
template = """
You are a naming consultant for new companies.
List 5 creative and catchy company names for a {company} that makes {product}.
"""

template2 = """
You are a naming consultant for new companies.
List 5 creative and catchy company names for a {company} that makes {product}.
Return the names as a comma-separated list.
"""

prompt = PromptTemplate(
    input_variables=["company", "product"],
    template=template
)

# 2. OpenAI LLM 모델 정의
llm = OpenAI(temperature=0.9) # temperature=0.9로 설정되어 있어 창의적인 결과를 유도함
# llm = OpenAI(model="gpt-4o-mini", temperature=0.7) # 4o-mini 도 completion 형태 지원

# 3. 출력 파서 정의
parser = StrOutputParser()
parser2 = CommaSeparatedListOutputParser()

# 4. 입력 예제
inputs = {"company": "High Tech Startup", "product": "Web Game"}

# 5. LLM 실행 (프롬프트 → LLM → 후처리)
formatted_prompt = prompt.format(**inputs)
llm_output = llm.invoke(formatted_prompt)
result_str = parser.invoke(llm_output)
result_csv = parser2.invoke(llm_output)

# 6. 출력
print("\nRaw Output (String):")
print(result_str)

print("\nParsed Output (CSV to List):")
print(result_csv)
