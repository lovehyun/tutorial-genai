# 3b: app3a_history.py + 요청/응답 시간 측정
# start~end 로 왕복 시간을 재는 것 말고는 3a와 완전히 동일하다.

import os
import time
import logging

from flask import Flask, request, send_from_directory, jsonify
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv('../.env')

app = Flask(__name__, static_folder='public')  # 정적 파일 폴더 설정
port = int(os.environ.get('PORT', 5000))

# OpenAI 셋업
openai_api_key = os.environ.get('OPENAI_API_KEY')

# Create a client instance
client = OpenAI(api_key=openai_api_key)

# logging 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 이전 대화 내용을 저장할 리스트
conversation_history = []


@app.route('/api/chat', methods=['POST'])
def chat():
    start = time.time() * 1000  # 요청 시작 시간 기록
    user_input = request.json.get('userInput', '')
    print(f' => [사용자 요청]: {user_input}')

    # 이전 대화 내용 추가
    conversation_history.append({'role': 'user', 'content': user_input})
    print(f' => [(프롬푸트) 통합 요청]: {conversation_history}')

    # ChatGPT에 대화 내용 전송
    response = ask_chatgpt(conversation_history)

    end = time.time() * 1000  # 응답 완료 시간 기록
    print(f' <= [ChatGPT 응답]: {response}')
    print(f'    (요청 및 응답 시간: {end - start} ms)')

    # 이전 대화 내용에 ChatGPT 응답 추가
    conversation_history.append({'role': 'assistant', 'content': response})

    return jsonify({'chatgpt': response})

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# ChatGPT에 전송할 대화 내용 구성
def ask_chatgpt(conversation_history):
    try:
        # 'system' 역할을 사용하여 사용자와 챗봇 간의 대화를 초기화합니다.
        input_messages = [
            # {'role': 'system', 'content': 'You are a helpful assistant.'},
            # {'role': 'system', 'content': 'You are a first-class hotel chef providing culinary recommendations.'},
            # {'role': 'system', 'content': 'You are a travel guide providing assistance and information for travelers.'},
            {'role': 'system', 'content': '당신은 도움이 되는 AI 어시스턴트입니다.'},
            # {'role': 'system', 'content': '당신은 최고급 호텔의 요리사로서 요리와 관련된 추천을 제공합니다.'},
            # {'role': 'system', 'content': '당신은 여행자들에게 도움과 정보를 제공하는 여행 가이드입니다.'},
            *conversation_history,
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=input_messages
        )

        chatgpt_response = response.choices[0].message.content
        return chatgpt_response

    except Exception as error:
        logger.error('Error making ChatGPT API request: %s', str(error))
        return '챗봇 응답을 가져오는 도중에 오류가 발생했습니다.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
