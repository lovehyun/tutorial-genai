from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from flask_cors import CORS
import os

# Flask 앱 생성
app = Flask(__name__)
# CORS 설정 - Node.js 서버에서 API 호출 허용
CORS(app)

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai_api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    OpenAI API를 사용하여 채팅 응답을 생성하는 API 엔드포인트
    """
    try:
        # JSON 요청 데이터 가져오기
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "JSON 데이터가 필요합니다"}), 400
        
        # 필수 파라미터 확인
        grade = data.get('grade')
        curriculum_title = data.get('curriculum_title')
        user_input = data.get('user_input')
        
        if not all([grade, curriculum_title, user_input]):
            return jsonify({
                "error": "필수 파라미터가 누락되었습니다 (grade, curriculum_title, user_input)"
            }), 400
        
        # OpenAI API 요청
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"당신은 초등학교 {grade}학년 학생을 위한 영어 교사입니다. "
                        f"학생이 {curriculum_title}에 대해 학습할 수 있도록 도와주세요. "
                        f"학생이 한국말로 문의를 하더라도 영어로 다시 해당 한국어에 대해서 질문을 할 수 있도록 답변을 유도해야 합니다. "
                        f"학생이 영어를 못하는 경우에는 한국말로 설명을 하면서 영어를 가르쳐주세요. "
                        f"예를 들어, '이 문장을 따라서 간단한 인사말을 해보세요: \"Good morning\" 이라는 단어를 따라해보세요.'"
                        f"라는 형태로 지금의 {curriculum_title} 에 해당하는 분야의 대화를 통해 학생의 영어 실력을 향상시키는 것이 목표입니다."
                    )
                },
                {"role": "user", "content": user_input}
            ]
        )
        
        # 응답 반환
        chat_response = response.choices[0].message.content.strip()
        return jsonify({"response": chat_response})
        
    except Exception as e:
        app.logger.error(f"오류 발생: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 메인 실행 코드
if __name__ == '__main__':
    # 기본 포트는 5000
    port = int(os.environ.get('PORT', 5000))
    # 디버그 모드로 실행
    app.run(debug=True, host='0.0.0.0', port=port)
