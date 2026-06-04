# pip install anthropic python-dotenv pydantic
#
# 중급 5: 구조화 출력 — 응답을 정해진 스키마(JSON)로 강제해 바로 파싱한다.
# messages.parse() + Pydantic 모델이 가장 간단. parsed_output 으로 검증된 객체를 받는다.
# (지원: Opus 4.8 / Sonnet 4.6 / Haiku 4.5)

import os
import anthropic
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 원하는 출력 형태를 클래스로 정의
class Person(BaseModel):
    name: str
    age: int
    city: str

resp = client.messages.parse(
    model="claude-sonnet-4-6",
    max_tokens=500,
    messages=[{"role": "user", "content": "다음에서 정보 추출: 김철수, 30세, 서울 거주."}],
    output_format=Person,
)

person = resp.parsed_output      # 검증된 Person 인스턴스 (문자열 파싱 불필요)
print("이름:", person.name)
print("나이:", person.age)
print("도시:", person.city)
print("타입:", type(person))
