import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')

CONVO_FILE = "conversation.txt"
MODEL = "gpt-3.5-turbo"
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)

# Bot1은 질문을 생성하는 역할 (user)
SYSTEM_PROMPT = "당신은 대화의 흐름을 유지하면서 자연스럽고 논리적인 후속 질문을 만드는 역할을 합니다."

# 2. 시스템 프롬프트 수정 (질문을 명확하게 생성하도록 지시)
SYSTEM_PROMPT = """당신은 대화의 흐름을 유지하면서 논리적이고 명확한 질문을 만드는 역할을 합니다.
질문자는 시큐어 코딩, 해킹 기법, 보안 취약점, 보안 대책 등에 대해 배우고 싶어 합니다.
답변자의 응답을 기반으로 추가적인 정보나 심층적인 설명을 요구하는 질문을 만들어 주세요.
중복되지 않고 자연스럽게 이어지는 질문을 작성해야 합니다.
절대 응원이나 일반적인 인사말을 하지 마세요! 오직 질문만 하세요."""

# 3. 학생이 교수님께 질문하는 방식으로 변경
SYSTEM_PROMPT = """당신은 정보 보안 및 시큐어 코딩을 배우고 있는 학생입니다. 
1. 당신은 교수님께 궁금한 점을 질문해야 합니다. 
2. 답변자의 응답을 기반으로 논리적으로 연결되는 후속 질문을 작성하세요.
3. 절대 정보를 제공하거나 설명하지 마세요! 불필요한 인사말이나 응원도 하지 마세요. 오직 질문만 해야 합니다.
4. 질문은 명확하고 구체적으로 작성하고, 교수님께 배우고자 하는 자세를 유지하세요.
5. 예를 들면, "교수님, 시큐어 코딩에서 입력 검증이 중요한 이유는 무엇인가요?" 처럼 기술적인 질문을 만들어 주세요."""

def get_next_question():
    with open(CONVO_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 최근 5개의 대화만 사용 (질문+답변 = 10줄줄)
    last_n_lines = lines[-10:] if len(lines) > 10 else lines

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # 기존 대화 내용을 user(질문) → assistant(답변) 순서로 추가
    for i, line in enumerate(last_n_lines):
        role = "user" if i % 2 == 0 else "assistant"
        messages.append({"role": role, "content": line.strip()})

    # 새로운 질문 생성 요청
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=100,
        stop=["\n"] # 문장이 완전히 끝난 후 멈추도록 설정
    )
    return response.choices[0].message.content

def main():
    initial_question = "안녕! 나는 시큐어 코딩에 대해서 공부하고 있어."  # 첫 질문
    initial_question = "교수님, 시큐어 코딩이 중요한 이유는 무엇인가요?"  # 첫 질문을 교수님께 묻는 형식으로 변경

    with open(CONVO_FILE, "w", encoding="utf-8") as f:
        f.write(initial_question + "\n")

    print("[Bot1] 질문: ", initial_question)

    while True:
        time.sleep(5)

        # bot2가 응답할 때까지 대기 후 파일 읽기
        with open(CONVO_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) % 2 == 0:  # bot1 차례 (짝수 줄 = 질문)
            last_response = lines[-1].strip()
            print("[Bot2] 응답: ", last_response)

            # Bot1이 새로운 질문 생성
            next_question = get_next_question()
            print("[Bot1] 질문: ", next_question)

            # 파일에 추가
            with open(CONVO_FILE, "a", encoding="utf-8") as f:
                f.write(next_question + "\n")

        time.sleep(5)

if __name__ == "__main__":
    main()
