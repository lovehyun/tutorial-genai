import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')

CONVO_FILE = "conversation.txt"
MODEL = "gpt-3.5-turbo"  # 사용할 OpenAI 모델
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)

def get_response(prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50
    )
    return response.choices[0].message.content

def main():
    while True:
        # bot1이 응답할 때까지 기다림
        time.sleep(5)

        # 최신 응답 읽기
        with open(CONVO_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        if len(lines) % 2 == 1:  # bot2 차례 (홀수 줄)
            last_response = lines[-1].strip()
            print("[Bot1] 응답: ", last_response)
            
            # 새로운 질문 생성
            new_prompt = get_response(last_response)
            print("[Bot2] 응답: ", new_prompt)

            # 파일에 추가
            with open(CONVO_FILE, "a", encoding="utf-8") as f:
                f.write(new_prompt + "\n")

if __name__ == "__main__":
    main()
