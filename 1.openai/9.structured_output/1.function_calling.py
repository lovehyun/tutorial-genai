# pip install openai

import openai
from dotenv import load_dotenv
import os
import json

load_dotenv(dotenv_path='../../.env')

openai_api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=openai_api_key)

print("=" * 50)
print("Function Calling & Structured Output")
print("=" * 50)

# 1. 기본 Function Calling
print("\n[1] 기본 Function Calling")
print("-" * 40)

# 함수 정의 (도구 스키마)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "특정 도시의 현재 날씨 정보를 가져옵니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "도시 이름 (예: 서울, 부산)"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "온도 단위"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_restaurants",
            "description": "특정 지역의 맛집을 검색합니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "검색할 지역"
                    },
                    "cuisine": {
                        "type": "string",
                        "description": "음식 종류 (예: 한식, 일식, 양식)"
                    },
                    "price_range": {
                        "type": "string",
                        "enum": ["저렴", "보통", "고급"],
                        "description": "가격대"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

# 실제 함수 구현 (시뮬레이션)
def get_weather(city, unit="celsius"):
    weather_data = {
        "서울": {"temp": 22, "condition": "맑음", "humidity": 45},
        "부산": {"temp": 25, "condition": "흐림", "humidity": 60},
        "제주": {"temp": 27, "condition": "비", "humidity": 80},
    }
    data = weather_data.get(city, {"temp": 20, "condition": "알 수 없음", "humidity": 50})
    return json.dumps({"city": city, "temperature": data["temp"], "unit": unit, "condition": data["condition"], "humidity": data["humidity"]}, ensure_ascii=False)

def search_restaurants(location, cuisine=None, price_range=None):
    return json.dumps({"location": location, "cuisine": cuisine or "전체", "restaurants": [
        {"name": f"{location} 맛집 1", "rating": 4.5, "cuisine": cuisine or "한식"},
        {"name": f"{location} 맛집 2", "rating": 4.2, "cuisine": cuisine or "양식"},
    ]}, ensure_ascii=False)

# Function Calling 실행
user_message = "서울 날씨가 어때? 그리고 강남에 맛있는 일식집 추천해줘"
print(f"사용자: {user_message}\n")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "당신은 유용한 AI 도우미입니다. 필요한 경우 도구를 사용하세요."},
        {"role": "user", "content": user_message}
    ],
    tools=tools,
    tool_choice="auto",
    temperature=0,
)

# 도구 호출 처리
message = response.choices[0].message
print(f"모델 응답 유형: {'도구 호출' if message.tool_calls else '텍스트'}")

if message.tool_calls:
    # 도구 호출 결과 수집
    messages = [
        {"role": "system", "content": "당신은 유용한 AI 도우미입니다. 도구 결과를 바탕으로 한국어로 답변하세요."},
        {"role": "user", "content": user_message},
        message,
    ]

    available_functions = {
        "get_weather": get_weather,
        "search_restaurants": search_restaurants,
    }

    for tool_call in message.tool_calls:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        print(f"  호출: {func_name}({func_args})")

        func = available_functions[func_name]
        result = func(**func_args)
        print(f"  결과: {result}")

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })

    # 도구 결과를 포함한 최종 응답
    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
    )
    print(f"\nAI 응답: {final_response.choices[0].message.content}")

# 2. Structured Output (response_format)
print("\n" + "=" * 50)
print("[2] Structured Output (JSON 모드)")
print("-" * 40)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "당신은 영화 정보를 JSON 형식으로 제공하는 도우미입니다. 반드시 JSON 형식으로 응답하세요."},
        {"role": "user", "content": "최근 인기 있는 한국 영화 3편의 제목, 감독, 장르, 평점을 알려줘"}
    ],
    response_format={"type": "json_object"},
    temperature=0,
)

json_response = response.choices[0].message.content
print(f"JSON 응답:\n{json_response}")

# JSON 파싱 및 활용
try:
    data = json.loads(json_response)
    print(f"\n파싱된 데이터 (키): {list(data.keys())}")
except json.JSONDecodeError as e:
    print(f"JSON 파싱 오류: {e}")

# 3. 데이터 추출 활용 예제
print("\n" + "=" * 50)
print("[3] 구조화된 데이터 추출")
print("-" * 40)

extract_tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_contact_info",
            "description": "텍스트에서 연락처 정보를 추출합니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "이름"},
                    "email": {"type": "string", "description": "이메일 주소"},
                    "phone": {"type": "string", "description": "전화번호"},
                    "company": {"type": "string", "description": "회사명"},
                    "position": {"type": "string", "description": "직책"},
                },
                "required": ["name"]
            }
        }
    }
]

text = "안녕하세요, 저는 테크스타트 주식회사의 CTO 김민수입니다. 이메일은 minsu.kim@techstart.co.kr이고, 연락처는 010-1234-5678입니다."
print(f"입력 텍스트: {text}\n")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "텍스트에서 연락처 정보를 추출하세요."},
        {"role": "user", "content": text}
    ],
    tools=extract_tools,
    tool_choice={"type": "function", "function": {"name": "extract_contact_info"}},
    temperature=0,
)

if response.choices[0].message.tool_calls:
    extracted = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
    print("추출된 연락처 정보:")
    for key, value in extracted.items():
        print(f"  {key}: {value}")

print("\n" + "=" * 50)
print("설명:")
print("1. Function Calling: LLM이 언제 어떤 함수를 호출할지 자동으로 결정합니다")
print("2. tool_choice='auto': 모델이 필요에 따라 도구 사용 여부를 판단합니다")
print("3. response_format: JSON 모드로 구조화된 응답을 강제합니다")
print("4. 구조화된 데이터 추출: Function Calling을 활용한 정보 추출 패턴입니다")
