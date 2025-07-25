import os
import time
import logging
import sqlite3
import json

from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv('../.env')

app = Flask(__name__, static_folder='public')  # 정적 파일 폴더 설정
CORS(app)  # Cross-Origin Resource Sharing 설정
port = int(os.environ.get('PORT', 5000))

# OpenAI 셋업
openai_api_key = os.environ.get('OPENAI_API_KEY')

# Create a client instance
client = OpenAI(api_key=openai_api_key)

# logging 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLite3 DB 설정
# conn = sqlite3.connect(':memory:', check_same_thread=False) # 메모리에 DB 생성 (파일로 저장하려면 파일 경로를 지정)
conn = sqlite3.connect('history.db', check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 대화 히스토리 테이블 생성
def init_db():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

init_db()

def cleanup_old_conversations():
    # 30일 이상 된 대화 삭제
    cursor.execute("DELETE FROM conversation WHERE timestamp < datetime('now', '-30 day')")
    conn.commit()

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    cursor.execute("DELETE FROM conversation")
    conn.commit()
    return jsonify({'status': 'success'})

@app.route('/api/search')
def search_history():
    query = request.args.get('q', '')
    cursor.execute("SELECT * FROM conversation WHERE content LIKE ? ORDER BY id DESC", (f'%{query}%',))
    rows = cursor.fetchall()
    return json.dumps({'results': [dict(row) for row in rows]}, ensure_ascii=False)
                      
# 최근 10개의 대화 내용 가져오기
def get_recent_conversation():
    cursor.execute("SELECT * FROM conversation ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    return rows[::-1]

# 사용자의 대화를 받아 처리하고 챗봇 응답을 반환
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        start = time.time() * 1000  # 요청 시작 시간 기록
        user_input = request.json['userInput']
        print(f' => 사용자 요청: {user_input}')

        # 대화 내용 DB에 추가
        cursor.execute("INSERT INTO conversation (role, content) VALUES (?, ?)", ('user', user_input))
        conn.commit()

        # 최근 10개 대화 내용 가져오기
        recent_conversation = get_recent_conversation()
        print(recent_conversation)

        # 필요한 필드만 선택하고 딕셔너리 리스트로 변환
        formatted_conversation = [{'role': row['role'], 'content': row['content']} for row in recent_conversation]
        print(f' => 실제(프롬푸트) 요청: {formatted_conversation}')

        # ChatGPT에 대화 내용 전송
        response = ask_chatgpt(formatted_conversation)

        end = time.time() * 1000  # 응답 완료 시간 기록
        print(f' <= ChatGPT 응답: {response}')
        print(f' == 요청 및 응답 시간: {end - start} ms')

        # 대화 내용 DB에 추가
        cursor.execute("INSERT INTO conversation (role, content) VALUES (?, ?)", ('assistant', response))
        conn.commit()

        return jsonify({'chatGPTResponse': response})
    except Exception as e:
        print('Error processing chat request:', str(e))
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# 최근 10개의 대화 내용을 JSON으로 반환
@app.route('/api/history')
def get_history():
    try:
        recent_conversation = get_recent_conversation()
        formatted_rows = [{'role': row['role'], 'content': row['content']} for row in recent_conversation]
        # return jsonify({'conversationHistory': formatted_rows})
        return json.dumps({'conversationHistory': formatted_rows}, ensure_ascii=False)
    except Exception as e:
        print('Error getting recent conversation:', str(e))
        return jsonify({'error': 'Internal Server Error'}), 500

# ChatGPT에 전송할 대화 내용 구성
def ask_chatgpt(conversation_history):
    try:
        input_messages = [
            # 'system' 역할을 사용하여 사용자와 챗봇 간의 대화를 초기화합니다.
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            *conversation_history
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=input_messages
        )

        chatgpt_response = response.choices[0].message.content
        # logger.info('ChatGPT 응답: %s', chatgpt_response)
        return chatgpt_response

    except Exception as e:
        print('Error making ChatGPT API request:', str(e))
        return '챗봇 응답을 가져오는 도중에 오류가 발생했습니다.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
