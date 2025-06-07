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

# 안전한 계산을 위한 함수
def safe_eval(expression):
    """ 사용자가 입력한 수식을 안전하게 평가 """
    try:
        # 숫자 및 연산자만 포함된 안전한 수식인지 확인
        if not re.match(r"^[0-9+\-*/().\s]+$", expression):
            return None  # 허용되지 않는 문자가 있으면 계산 안 함
        return eval(expression)
    except:
        return None
    
@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("question")

    if not user_input:
        return jsonify({"error": "질문을 입력하세요."}), 400

    # 세션에서 대화 기록 가져오기 (없으면 초기화)
    if "messages" not in session:
        session["messages"] = [{"role": "system", "content": "You are a helpful assistant."}]
        session["conversation_count"] = 0

    # 사용자가 수학 연산을 입력했는지 확인
    match = re.search(r"[\d+\-*/().\s]+", user_input)
    if match and match.group() == user_input.strip():
        result = safe_eval(user_input.strip())  # 안전한 평가 수행
        if result is not None:
            bot_reply = f"계산 결과: {result}"
            session["messages"].append({"role": "assistant", "content": bot_reply})
            return jsonify({"response": bot_reply})
        
    # 사용자 입력 추가
    session["messages"].append({"role": "user", "content": user_input})
    session.modified = True

    # 대화 길이 제한 (최근 MAX_HISTORY_LENGTH개 유지)
    if len(session["messages"]) > MAX_HISTORY_LENGTH + 1:  # system 메시지 제외
        session["messages"] = [session["messages"][0]] + session["messages"][-MAX_HISTORY_LENGTH:]

    # 현재 대화 개수 계산 (시스템 메시지 제외)
    session["conversation_count"] = session.get("conversation_count", 0) + 1

    # 시스템 메시지 업데이트 (대화 개수 추가 - 히스토리에 매번 10개만 남김으로...)
    session["messages"][0] = {
        "role": "system",
        "content": f"You are a helpful assistant. 현재까지 총 {session["conversation_count"]}개의 대화가 오갔습니다."
    }
    
    print(session["messages"])
    print('-' * 50)
    
    # GPT API 호출
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=session["messages"]
    )

    # GPT 응답 저장
    bot_reply = response.choices[0].message.content
    session["messages"].append({"role": "assistant", "content": bot_reply})
    session.modified = True

    return jsonify({"response": bot_reply})

@app.route("/clear", methods=["POST"])
def clear():
    """대화 내용 초기화"""
    session.pop("messages", None)
    return jsonify({"message": "대화 기록이 초기화되었습니다."})

if __name__ == "__main__":
    app.run(debug=True)
