from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import json
import threading
import time
import os
from agents.agent_manager import AgentManager
from agents.memory_agent import MemoryAgent
from agents.search_agent import SearchAgent
from agents.calculation_agent import CalculationAgent
from agents.chat_agent import ChatAgent

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Agent 매니저 초기화
agent_manager = AgentManager()

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """채팅 API 엔드포인트"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': '메시지가 없습니다.'}), 400
    
    # Agent 매니저를 통해 메시지 처리
    response = agent_manager.process_message(user_message)
    
    return jsonify(response)

@socketio.on('connect')
def handle_connect():
    """클라이언트 연결 처리"""
    print('클라이언트가 연결되었습니다.')
    emit('status', {'message': '연결되었습니다.'})

@socketio.on('disconnect')
def handle_disconnect():
    """클라이언트 연결 해제 처리"""
    print('클라이언트가 연결 해제되었습니다.')

@socketio.on('send_message')
def handle_message(data):
    """실시간 메시지 처리"""
    user_message = data.get('message', '')
    
    if not user_message:
        emit('error', {'message': '메시지가 없습니다.'})
        return
    
    # 실시간으로 agent 처리 과정을 클라이언트에 전송
    def process_with_updates():
        with app.app_context():
            try:
                # Agent 매니저를 통해 메시지 처리 (실시간 업데이트 포함)
                response = agent_manager.process_message_with_updates(user_message, socketio)
                socketio.emit('chat_response', response)
            except Exception as e:
                socketio.emit('error', {'message': f'오류가 발생했습니다: {str(e)}'})
    
    # 백그라운드에서 처리
    thread = threading.Thread(target=process_with_updates)
    thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
