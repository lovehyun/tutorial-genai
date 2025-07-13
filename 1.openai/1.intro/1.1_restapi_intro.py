# pip install python-dotenv
import requests
from time import sleep
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='../.env')

openai_api_key = os.getenv('OPENAI_API_KEY')

def ask_chatgpt(user_input):
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            json={
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'system', 'content': 'You are a helpful assistant.'},
                    {'role': 'user', 'content': user_input},
                ],
                # 다양한 변수 적용
                'max_tokens': 100,          # 응답의 최대 토큰 수
                'temperature': 0.7,         # 창의성 제어
                'top_p': 0.9,               # 확률 기반 토큰 선택 범위
                'frequency_penalty': 0.5,   # 반복 억제
                'presence_penalty': 0.6     # 새로운 주제 장려
            },
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {openai_api_key}',
            }
        )

        response.raise_for_status()  # Raise an error for bad HTTP status codes
        response_data = response.json()
        print('-'*20)
        print('Response JSON:', response_data)  # Print the entire response for debugging
        print('-'*20)

        return response.json()['choices'][0]['message']['content']
    except Exception as error:
        print('ChatGPT API 요청 중 오류 발생:', str(error))
        return '챗봇 응답을 가져오는 도중에 오류가 발생했습니다.'

def chat_with_user():
    user_input = '안녕, 챗봇!'
    chat_gpt_response = ask_chatgpt(user_input)
    print('챗봇 응답:', chat_gpt_response)

# 챗봇과 대화 시작
chat_with_user()

# 2초 간격으로 요청 보내기
# while True:
#     chat_with_user()
#     sleep(2)
