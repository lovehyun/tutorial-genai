# 5: 히스토리 요약 압축 (오래된 대화를 버리지 않고 요약해서 남긴다)
# 4 대비 달라진 것: MAX_HISTORY_LENGTH를 넘으면 그냥 삭제(pop)하는 대신,
#                    오래된 부분을 LLM으로 한 문단 요약해서 대신 남긴다.
#                    → 맥락은 유지하면서 토큰은 절약.
#
# 히스토리가 두 종류로 나뉜다는 게 이 단계의 핵심이다:
#   full_history        : 실제로 오간 대화 전부. 압축되지 않는다 (비교/확인용).
#   conversation_history: GPT에 실제로 보내는 "작업용" 히스토리. 길어지면 압축된다.
# 두 값을 각각 /api/history, /api/history/compressed 로 확인할 수 있다.

import os
import logging
import json

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

# 대화 히스토리 길이 관리
MAX_HISTORY_LENGTH = 10  # 작업용 히스토리가 이 개수를 넘으면 압축 실행
KEEP_RECENT = 4          # 압축 후에도 원문 그대로 남겨둘 최근 메시지 개수

# 원본 로그 — 압축 없이 오간 대화 전부를 그대로 쌓아둔다 (비교용)
full_history = []

# 작업용 히스토리 — 실제로 GPT에 보내는 대화. 길어지면 압축된다.
conversation_history = []
conversation_seq = 0
compression_count = 0


@app.route('/api/chat', methods=['POST'])
def chat():
    global conversation_history
    global conversation_seq
    global compression_count

    user_input = request.json.get('userInput', '')
    print(f' => [사용자 요청]: {user_input}')

    # 사용자 메시지를 원본 로그와 작업용 히스토리 양쪽에 추가
    full_history.append({'role': 'user', 'content': user_input})
    conversation_history.append({'role': 'user', 'content': user_input})
    conversation_seq += 1

    # ChatGPT에 (압축될 수도 있는) 작업용 히스토리를 전송
    response = ask_chatgpt(conversation_history)
    print(f' <= [ChatGPT 응답]: {response}')

    full_history.append({'role': 'assistant', 'content': response})
    conversation_history.append({'role': 'assistant', 'content': response})
    conversation_seq += 1

    # 작업용 히스토리가 길어지면 오래된 부분을 요약으로 압축
    if len(conversation_history) > MAX_HISTORY_LENGTH:
        compress_history()

    return jsonify({'chatgpt': response})

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# 오래된 대화를 요약 1개 + 최근 대화로 교체한다
def compress_history():
    global conversation_history
    global compression_count

    old_part = conversation_history[:-KEEP_RECENT]
    recent_part = conversation_history[-KEEP_RECENT:]

    summary_text = summarize_conversation(old_part)
    compression_count += 1

    print(f'\n[히스토리 압축 #{compression_count}] {len(old_part)}개 메시지 → 요약 1개 + 최근 {len(recent_part)}개 유지')
    print(f'  압축 전(원문): {old_part}')
    print(f'  압축 후(요약): {summary_text}')

    conversation_history[:] = [
        {'role': 'system', 'content': f'[이전 대화 요약] {summary_text}'},
        *recent_part,
    ]

# 메시지 목록을 짧은 한 문단으로 요약한다 (별도 LLM 호출)
def summarize_conversation(messages):
    try:
        transcript = '\n'.join(f"{m['role']}: {m['content']}" for m in messages)
        prompt = (
            '다음은 챗봇과 사용자가 나눈 대화의 일부다. '
            '이후 대화에서 맥락으로 참고할 수 있도록 핵심만 3문장 이내로 요약해줘.\n\n'
            f'{transcript}'
        )

        summary_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {'role': 'system', 'content': '너는 대화 내용을 간결하게 요약하는 요약 전문가야.'},
                {'role': 'user', 'content': prompt},
            ],
            temperature=0.3,
        )
        return summary_response.choices[0].message.content.strip()
    except Exception as error:
        print('Error summarizing conversation:', str(error))
        return '(요약 실패 — 이전 대화 내용을 확인할 수 없습니다)'

# 원본 로그 확인 — 압축과 무관하게 실제로 오간 대화 전부
@app.route('/api/history')
def get_history():
    numbered_history = [
        {'role': item['role'], 'content': item['content'], 'number': index + 1}
        for index, item in enumerate(full_history)
    ]
    return json.dumps({'conversationHistory': numbered_history, 'totalMessages': len(full_history)}, ensure_ascii=False)

# 압축된(작업용) 히스토리 확인 — 지금 이 순간 GPT에게 실제로 보내지는 것
@app.route('/api/history/compressed')
def get_compressed_history():
    return json.dumps({
        'workingHistory': conversation_history,
        'compressionCount': compression_count,
        'maxHistoryLength': MAX_HISTORY_LENGTH,
        'keepRecent': KEEP_RECENT,
    }, ensure_ascii=False)

# ChatGPT에 전송할 대화 내용 구성
def ask_chatgpt(conversation_history):
    try:
        # 'system' 역할을 사용하여 사용자와 챗봇 간의 대화를 초기화합니다.
        input_messages = [
            {'role': 'system', 'content': '당신은 도움이 되는 AI 어시스턴트입니다.'},
            *conversation_history,
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=input_messages
        )

        return response.choices[0].message.content

    except Exception as error:
        logger.error('Error making ChatGPT API request: %s', str(error))
        return '챗봇 응답을 가져오는 도중에 오류가 발생했습니다.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
