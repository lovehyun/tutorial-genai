import os
import logging
from flask import Flask, request, send_from_directory, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# 환경 변수 로드
# load_dotenv('../../.env')
load_dotenv()

app = Flask(__name__, static_folder='public')
port = int(os.environ.get("PORT", 5000))

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 대화 히스토리 저장 (단일 사용자용)
chat_history = [
    {"role": "system", "content": "당신은 도움이 되는 AI 어시스턴트입니다."}
]

@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.json.get("userInput", "")
    logger.info(f"[사용자 요청]: {user_input}")

    # 사용자 입력 추가
    chat_history.append({"role": "user", "content": user_input})

    try:
        # 일반 방식으로 응답 요청
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_history
        )

        assistant_message = response.choices[0].message.content
        logger.info(f"[GPT 응답]: {assistant_message}")

        # 챗봇 응답도 히스토리에 추가
        chat_history.append({"role": "assistant", "content": assistant_message})

        return jsonify({"chatGPTResponse": assistant_message})

    except Exception as e:
        logger.error(f"❌ OpenAI 오류: {str(e)}")
        return jsonify({"chatGPTResponse": f"오류 발생: {str(e)}"}), 500

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
