# pip install openai==1.0
# https://platform.openai.com/docs/api-reference/introduction

import openai
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
openai_api_key = os.getenv('OPENAI_API_KEY')

# OpenAI 클라이언트 객체 생성
client = openai.OpenAI(api_key=openai_api_key)

def ask_chatgpt(messages: list) -> str:
    """
    대화 메시지 히스토리를 기반으로 GPT 응답 생성
    """
    try:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=messages,
            max_tokens=150,
            temperature=0.7,
            top_p=0.9,
            frequency_penalty=0.5,
            presence_penalty=0.6
        )

        return response.choices[0].message.content
    except Exception as error:
        print('ChatGPT API 요청 중 오류 발생:', str(error))
        return '챗봇 응답을 가져오는 도중에 오류가 발생했습니다.'

def chat_with_user():
    print("챗봇과의 대화를 시작합니다. 종료하려면 'exit', 'quit' 등을 입력하세요.")
    print("=" * 50)

    # 시스템 메시지 포함한 히스토리 초기화
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

    while True:
        user_input = input("\n당신: ").strip()

        if user_input.lower() in {"exit", "quit", "종료", "끝"}:
            print("대화를 종료합니다. 안녕히 가세요!")
            break

        if not user_input:
            print("메시지를 입력해주세요.")
            continue

        # 사용자 메시지 히스토리에 추가
        messages.append({"role": "user", "content": user_input})

        print("챗봇이 응답을 생성중입니다...")

        # GPT 응답 받아오기
        bot_response = ask_chatgpt(messages)

        # 챗봇 응답 히스토리에 추가
        messages.append({"role": "assistant", "content": bot_response})

        print(f"\n챗봇: {bot_response}")
        print("-" * 30)

if __name__ == "__main__":
    chat_with_user()
