# OpenAI REST API - 4단계: 함수화 + 예외 처리 + 대화형 입력
#
# 3단계 대비 추가:
#   ① API 호출을 함수(ask_chatgpt)로 분리 → 재사용 가능
#   ② try/except 로 네트워크·인증 오류 대비
#   ③ input()으로 직접 질문을 입력하는 대화 루프
#
# 여기까지가 REST API 방식의 완성형. 5단계부터는 같은 일을 SDK로 더 간결하게.
# 참고: 매 호출이 독립적이라 아직 '대화 기억'은 없다 → 8단계에서 해결.

import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
openai_api_key = os.getenv('OPENAI_API_KEY')

# 챗봇 성격 — 한 줄만 활성화해 바꿔보세요
system_prompt = '당신은 친절한 AI 도우미입니다.'
# system_prompt = '당신은 여행 가이드입니다. 여행 정보를 제공하세요.'
# system_prompt = '당신은 초등학생도 이해하도록 쉽게 설명하는 선생님입니다.'

def ask_chatgpt(user_input):
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {openai_api_key}',
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_input},
                ],
                'temperature': 0.7,
                'max_tokens': 200,
            },
        )
        response.raise_for_status()  # HTTP 오류 상태코드(4xx/5xx)면 예외 발생
        return response.json()['choices'][0]['message']['content']
    except Exception as error:
        # 네트워크 끊김, API 키 오류 등이 여기서 잡힌다
        print('API 요청 중 오류 발생:', str(error))
        return '응답을 가져오는 도중 오류가 발생했습니다.'

if __name__ == '__main__':
    print('챗봇과 대화를 시작합니다. (종료: exit)')
    while True:
        user_input = input('\n나: ').strip()
        if user_input.lower() == 'exit':
            print('대화를 종료합니다.')
            break
        print('챗봇:', ask_chatgpt(user_input))
