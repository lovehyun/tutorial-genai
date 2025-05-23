import os
import re
from flask import Flask, request, jsonify, send_from_directory, session
from dotenv import load_dotenv
from openai import OpenAI

# 환경 변수 로드
load_dotenv()
openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__, static_folder='public', static_url_path='')
app.secret_key = "your_secret_key"  # Flask 세션을 위한 키

# 최대 대화 저장 개수
MAX_HISTORY_LENGTH = 10  # 최근 10개의 메시지만 유지

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# 안전한 계산을 위한 함수 (Python 코드 실행)
def execute_python_code(code):
    print(code)
    
    """GPT가 생성한 Python 코드를 실행하여 결과 반환"""
    try:
        exec_globals = {}  # 실행을 위한 별도 네임스페이스
        exec(code, exec_globals)
        return exec_globals.get("result", "결과 없음")  # 결과 반환
    except Exception as e:
        return f"코드 실행 오류: {str(e)}"
    
@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("question")

    if not user_input:
        return jsonify({"error": "질문을 입력하세요."}), 400

    # 세션에서 대화 기록 가져오기 (없으면 초기화)
    if "messages" not in session:
        session["messages"] = [{"role": "system", "content": "You are a helpful assistant."}]

    # 사용자가 산술식을 입력했는지 확인
    if re.match(r"^[0-9+\-*/().\s]+$", user_input.strip()):
        # GPT에게 Python 코드 생성 요청
        gpt_response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "사용자가 입력한 수식을 Python 코드로 변환하고 'result' 변수에 저장하세요."},
                {"role": "user", "content": f"다음 수식을 Python 코드로 변환하세요: {user_input}"}
            ]
        )
        generated_code = gpt_response.choices[0].message.content

        # GPT가 생성한 Python 코드 실행
        result = execute_python_code(generated_code)

        # GPT의 코드 및 실행 결과 출력
        bot_reply = f"코드 실행 결과: {result}"
        session["messages"].append({"role": "assistant", "content": bot_reply})
        return jsonify({"response": bot_reply})
        
    # 사용자 입력 추가
    session["messages"].append({"role": "user", "content": user_input})

    # 대화 길이 제한 (최근 MAX_HISTORY_LENGTH개 유지)
    if len(session["messages"]) > MAX_HISTORY_LENGTH + 1:  # system 메시지 제외
        session["messages"] = [session["messages"][0]] + session["messages"][-MAX_HISTORY_LENGTH:]

    # 현재 대화 개수 계산 (시스템 메시지 제외)
    conversation_count = (len(session["messages"]) - 1) // 2  # 사용자-어시스턴트 쌍 기준

    # 시스템 메시지 업데이트 (대화 개수 추가)
    session["messages"][0] = {
        "role": "system",
        "content": f"You are a helpful assistant. 현재까지 총 {conversation_count}개의 대화가 오갔습니다."
    }
    
    print(session["messages"])
    print('-' * 50)
    
    # GPT API 호출
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=session["messages"]
    )

    # GPT 응답 저장
    bot_reply = response.choices[0].message.content
    session["messages"].append({"role": "assistant", "content": bot_reply})

    return jsonify({"response": bot_reply})

@app.route("/clear", methods=["POST"])
def clear():
    """대화 내용 초기화"""
    session.pop("messages", None)
    return jsonify({"message": "대화 기록이 초기화되었습니다."})

if __name__ == "__main__":
    app.run(debug=True)
