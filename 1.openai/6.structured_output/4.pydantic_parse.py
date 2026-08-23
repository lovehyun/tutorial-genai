# 구조화 출력 - 4단계: Pydantic으로 스키마 정의 + parse()
# pip install openai pydantic python-dotenv
#
# 3단계 문제: JSON 스키마를 손으로 쓰면 길고 번거롭다 (type, properties, required...).
#
# 이 단계 해결: 파이썬 Pydantic 클래스로 구조를 정의하고,
#   client.beta.chat.completions.parse() 를 쓴다.
#   → SDK가 클래스를 JSON 스키마로 자동 변환하고, 응답도 클래스 객체로 돌려준다.
#   → json.loads조차 필요 없이 city.population 처럼 바로 접근한다.
#
# 3단계와 결과는 같지만 코드가 훨씬 읽기 쉽다 — 실무에서 가장 많이 쓰는 방식.

import os
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# [관전 포인트 1] 3단계의 JSON 스키마를 파이썬 클래스로 — 이 클래스가 곧 출력 구조다.
class CityInfo(BaseModel):
    name: str
    population: int
    area_km2: float

response = client.beta.chat.completions.parse(
    model='gpt-4o-mini',
    messages=[
        {'role': 'user', 'content': '서울의 인구와 면적을 알려줘.'},
    ],
    response_format=CityInfo,   # 클래스를 그대로 넘긴다
)

# [관전 포인트 2] .parsed 는 이미 CityInfo 객체다 — json.loads가 필요 없다.
city = response.choices[0].message.parsed
print(f"{city.name} — 인구 {city.population:,}명, 면적 {city.area_km2}㎢")
