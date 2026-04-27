# OpenAI Structured Output — JSON Schema (strict mode)
# response_format을 사용하여 모델 출력을 JSON 스키마에 맞게 강제

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()
client = OpenAI()


# ─────────────────────────────────────────────
# 1. response_format=json_object (기본 JSON 모드)
# ─────────────────────────────────────────────
print("=== 1. JSON Object 모드 ===")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "JSON 형식으로만 응답하세요."},
        {"role": "user", "content": "서울, 도쿄, 뉴욕의 인구와 면적을 알려주세요."},
    ],
    response_format={"type": "json_object"},
)

data = json.loads(response.choices[0].message.content)
print(json.dumps(data, ensure_ascii=False, indent=2))


# ─────────────────────────────────────────────
# 2. response_format=json_schema (strict mode)
#    모델이 정의된 스키마를 100% 준수
# ─────────────────────────────────────────────
print("\n=== 2. JSON Schema (strict) 모드 ===")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "파이썬, 자바스크립트, Go 언어를 비교해주세요."},
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "language_comparison",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "languages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "언어 이름"},
                                "paradigm": {"type": "string", "description": "프로그래밍 패러다임"},
                                "use_cases": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "주요 사용 분야",
                                },
                                "difficulty": {
                                    "type": "string",
                                    "enum": ["쉬움", "보통", "어려움"],
                                    "description": "학습 난이도",
                                },
                            },
                            "required": ["name", "paradigm", "use_cases", "difficulty"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["languages"],
                "additionalProperties": False,
            },
        },
    },
)

data = json.loads(response.choices[0].message.content)
for lang in data["languages"]:
    print(f"\n{lang['name']} ({lang['paradigm']}) — 난이도: {lang['difficulty']}")
    print(f"  용도: {', '.join(lang['use_cases'])}")


# ─────────────────────────────────────────────
# 3. Pydantic + client.beta.chat.completions.parse()
#    Pydantic 모델로 더 간결하게 구조화 출력
# ─────────────────────────────────────────────
print("\n\n=== 3. Pydantic + parse() ===")


class Step(BaseModel):
    explanation: str
    output: str


class MathSolution(BaseModel):
    steps: list[Step]
    final_answer: str


response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "수학 문제를 단계별로 풀어주세요."},
        {"role": "user", "content": "연립방정식을 풀어주세요: 2x + 3y = 12, x - y = 1"},
    ],
    response_format=MathSolution,
)

solution = response.choices[0].message.parsed
for i, step in enumerate(solution.steps, 1):
    print(f"  Step {i}: {step.explanation}")
    print(f"          → {step.output}")
print(f"\n  최종 답: {solution.final_answer}")
