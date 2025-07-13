# pip install openai==1.0
# https://platform.openai.com/docs/api-reference/introduction

import openai
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='../.env')

openai_api_key = os.getenv('OPENAI_API_KEY')

# Create a client instance
client = openai.OpenAI(api_key=openai_api_key)

def ask_chatgpt(user_input):
    try:
        # Use the updated method for chat completions
        response = client.chat.completions.create(
            model='gpt-3.5-turbo', # gpt-3.5-turbo, gpt-3.5-turbo-16k, gpt-4, gpt-4-32k
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': user_input},
            ],
            # 다양한 변수 추가
            max_tokens=100,          # 응답의 최대 토큰 수
            temperature=0.7,         # 창의성 제어 (0.0 ~ 2.0: 0.2 정확, 0.7 창의)
            top_p=0.9,               # 확률 기반 토큰 선택 범위 (0.0 ~ 1.0: 1.0 모든 토큰, 0.1 상위 토큰만 선택)
            frequency_penalty=0.5,   # 반복 억제 (-2.0 ~ 2.0: 동일한 단어의 반복을 억제, -1.0 반복, 1.0 억제)
            presence_penalty=0.6     # 새로운 주제 도입 장려 (1.0 장려)
        )
        print('-'*20)
        print('Response JSON:', response)  # Print the entire response for debugging
        print('-'*20)

        return response.choices[0].message.content
    except Exception as error:
        print('ChatGPT API 요청 중 오류 발생:', str(error))
        return '챗봇 응답을 가져오는 도중에 오류가 발생했습니다.'

def chat_with_user():
    user_input = '안녕, 챗봇!'
    # user_input = input("\n당신: ").strip()
    
    chat_gpt_response = ask_chatgpt(user_input)
    print('챗봇 응답:', chat_gpt_response)

if __name__ == "__main__":
    chat_with_user()
