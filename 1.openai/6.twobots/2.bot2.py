import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')

CONVO_FILE = "conversation.txt"
MODEL = "gpt-3.5-turbo"
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)

# Bot2는 질문에 답변하는 역할 (assistant)
SYSTEM_PROMPT = "당신은 친절하고 유익한 답변을 제공하는 AI입니다. 간결하면서도 충분한 정보를 포함한 답변을 제공하세요."

# 3. 교수님이 학생에게 가르치는 방식으로 답변하도록 변경
SYSTEM_PROMPT = """당신은 정보 보안 및 시큐어 코딩을 가르치는 교수님입니다.
1. 학생이 질문을 하면, 명확하고 자세한 설명을 제공하세요.
2. 학생이 쉽게 이해할 수 있도록, 개념을 설명한 후 코드 예제나 실제 사례를 들어 설명해 주세요.
3. 전문적인 용어를 사용하되, 학생이 이해할 수 있도록 쉽게 풀어서 설명하세요.
4. 강의하는 교수님처럼 친절하고 논리적으로 답변하고 불필요한 응원 메세지나 인사말은 삼가하세요."""

def get_response():
    with open(CONVO_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # 기존 대화 내용을 추가 (user = 질문, assistant = 답변)
    for i, line in enumerate(lines):
        role = "user" if i % 2 == 0 else "assistant"
        messages.append({"role": role, "content": line.strip()})

    # 새로운 응답 생성 요청
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=250,
        stop=["\n"] # 문장이 완전히 끝난 후 멈추도록 설정
    )
    return response.choices[0].message.content

def main():
    print("[Bot2] 응답 시작!")

    while True:
        time.sleep(5)

        # bot1이 질문할 때까지 대기 후 파일 읽기
        with open(CONVO_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) % 2 == 1:  # bot2 차례 (홀수 줄 = 답변)
            last_question = lines[-1].strip()
            print("[Bot1] 질문: ", last_question)

            # Bot2가 새로운 답변 생성
            response = get_response()
            print("[Bot2] 응답: ", response)

            # 파일에 추가
            with open(CONVO_FILE, "a", encoding="utf-8") as f:
                f.write(response + "\n")

if __name__ == "__main__":
    main()
