import os
import logging

from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO
from openai import OpenAI
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# 환경변수 로드 (.env 파일에서 OPENAI_API_KEY 등을 불러옴)
load_dotenv()

PUBLIC_DIR='public'

# Flask 앱 초기화, 정적 파일은 별도 설정 없이 'static' 폴더로 간주
app = Flask(__name__, static_folder=PUBLIC_DIR, static_url_path='')
# SocketIO 설정 (모든 출처 허용)
socketio = SocketIO(app, cors_allowed_origins="*")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 전역 상태 저장 변수들
messages = []      # 전체 채팅 메시지 목록
user_map = {}      # 소켓 ID -> 사용자 정보 매핑
typing_users = set()  # 현재 타이핑 중인 사용자 집합

# 메시지를 target_lang 언어로 번역하는 함수
def translate_message(text, target_lang):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Translate to {target_lang}:"},
                {"role": "user", "content": text}
            ]
        )
        translated = response.choices[0].message.content
        print(f"🔄 Translation: {text} -> {translated} ({target_lang})")
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # 오류 발생 시 원문 반환

# 루트 페이지 요청 시 index.html 제공
@app.route('/')
def index():
    return send_from_directory(PUBLIC_DIR, 'index.html')

# 클라이언트가 접속했을 때
@socketio.on('connect')
def handle_connect():
    total_users = len(socketio.server.eio.sockets)
    print(f"✅ New user connected! Socket ID: {request.sid}, Total users: {total_users}")
    socketio.emit('user count', total_users)

# 새로운 사용자가 참여했을 때
@socketio.on('user joined')
def handle_join(username):
    user_map[request.sid] = {'username': username, 'language': 'ko'}
    print(f"👤 User joined: {username} (id: {request.sid})")

# 사용자가 언어를 변경했을 때
@socketio.on('set language')
def handle_language(lang):
    if request.sid in user_map:
        user_map[request.sid]['language'] = lang
        print(f"🌍 Language set for {user_map[request.sid]['username']}: {lang}")

# 사용자가 타이핑 중일 때
@socketio.on('typing')
def handle_typing():
    username = user_map.get(request.sid, {}).get('username', 'Unknown user')
    print(f"✍️ {username} is typing...")
    typing_users.add(username)
    # 자신을 제외한 다른 사용자들에게 타이핑 알림 전송
    socketio.emit('typing', username, skip_sid=request.sid)

# 사용자가 타이핑을 멈췄을 때
@socketio.on('stop typing')
def handle_stop_typing():
    username = user_map.get(request.sid, {}).get('username', 'Unknown user')
    print(f"✋ {username} has stopped typing...")
    typing_users.discard(username)
    socketio.emit('stop typing', username, skip_sid=request.sid)

# 채팅 메시지를 수신했을 때
@socketio.on('chat message')
def handle_message(data):
    sender = user_map.get(request.sid, {})
    unread_users = [sid for sid in user_map if sid != request.sid]

    # 메시지 저장
    message_data = {
        'username': data['username'],
        'message': data['message'],
        'timestamp': data['timestamp'],
        'unread_users': unread_users
    }
    messages.append(message_data)

    # 다른 사용자에게 해당 언어로 번역된 메시지 전송
    for sid in user_map:
        target_lang = user_map[sid]['language']
        if sid != request.sid:
            translated_msg = translate_message(data['message'], target_lang)
            socketio.emit('chat message', {
                'username': data['username'],
                'message': translated_msg,
                'timestamp': data['timestamp'],
                'unreadUsers': unread_users
            }, room=sid)

# 메시지 읽음 처리
@socketio.on('read message')
def handle_read(data):
    msg_idx = next((i for i, m in enumerate(messages) if m['timestamp'] == data['timestamp']), -1)
    if msg_idx != -1:
        messages[msg_idx]['unread_users'].remove(request.sid)
        socketio.emit('update read receipt', {
            'timestamp': data['timestamp'],
            'unreadUsers': messages[msg_idx]['unread_users']
        })

# 클라이언트가 연결 해제됐을 때
@socketio.on('disconnect')
def handle_disconnect():
    username = user_map.get(request.sid, {}).get('username', 'Unknown user')
    print(f"❌ User disconnected: {username} (ID: {request.sid})")

    if request.sid in user_map:
        del user_map[request.sid]

    # 해당 사용자를 unread 목록에서도 제거
    for msg in messages:
        if request.sid in msg['unread_users']:
            msg['unread_users'].remove(request.sid)

    # 접속자 수 갱신
    socketio.emit('user count', len(socketio.server.eio.sockets))

# 서버 실행
if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
