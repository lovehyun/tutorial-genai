import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_prompt(code):
    return (
        "다음 소스코드에서 보안 취약점을 분석해줘.\n"
        "각 취약점에 대해 해당 코드의 라인 번호, 코드 스니펫, 취약점 설명과 "
        "개선 방안을 마크다운 형식의 리스트로 출력해줘.\n"
        "단 '#' 으로 시작하는 주석코드는 무시해도 돼.\n\n"
        "소스코드:\n"
        "------------------------------\n"
        f"{code}\n"
        "------------------------------"
    )

def build_prompt2(code):
    return (
        "다음은 Python 소스코드입니다.\n\n"
        "이 코드에서 **보안 취약점이 존재하는 부분**을 찾아주세요.\n"
        "각 취약점에 대해 다음 정보를 명확하게 정리해주세요:\n\n"
        "1. **라인 번호**는 반드시 `라인 번호: 숫자` 또는 `라인 번호: 숫자-숫자` 형태로 명시해주세요.\n"
        "2. **취약한 코드 스니펫** (간단하게 한두 줄로)\n"
        "3. **취약점 설명**\n"
        "4. **개선 방안**\n\n"
        "결과는 아래 형식의 마크다운 리스트로 정리해주세요:\n\n"
        "- 라인 번호: 12-14\n"
          "  - 코드: ...\n"
          "  - 설명: ...\n"
          "  - 개선 방안: ...\n\n"
        "※ 주석(`#`)으로 시작하는 줄은 무시해도 됩니다.\n\n"
        "소스코드:\n"
        "------------------------------\n"
        f"{code}\n"
        "------------------------------"
    )

def analyze(code_with_line_numbers):
    # prompt = build_prompt(code_with_line_numbers)
    prompt = build_prompt2(code_with_line_numbers)
    messages = [
        {"role": "system", "content": "당신은 보안 코드 분석 전문가입니다."},
        {"role": "user", "content": prompt}
    ]
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.2
    )
    return response.choices[0].message.content
