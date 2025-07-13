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

        response.raise_for_status()
        response_data = response.json()
        print('-'*20)
        print('Response JSON:', response_data)
        print('-'*20)

        return response.json()['choices'][0]['message']['content']
    except Exception as error:
        print('ChatGPT API 요청 중 오류 발생:', str(error))
        return '챗봇 응답을 가져오는 도중에 오류가 발생했습니다.'

def chat_with_user():
    print("챗봇과 대화를 시작합니다. 종료하려면 'quit' 또는 'exit'를 입력하세요.")
    print("="*50)
    
    while True:
        # 사용자 입력 받기
        user_input = input("\n당신: ").strip()
        
        # 종료 조건
        if user_input.lower() in ['quit', 'exit', '종료', '끝']:
            print("대화를 종료합니다. 안녕히 가세요!")
            break
        
        # 빈 입력 체크
        if not user_input:
            print("메시지를 입력해주세요.")
            continue
        
        # ChatGPT 응답 받기
        print("\n챗봇이 응답을 생성중입니다...")
        chat_gpt_response = ask_chatgpt(user_input)
        print(f"\n챗봇: {chat_gpt_response}")
        print("-"*30)

if __name__ == "__main__":
    # 기본 버전 실행
    chat_with_user()
