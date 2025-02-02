import os
from flask import Flask, request, jsonify, send_from_directory, session
from dotenv import load_dotenv
from openai import OpenAI

# 환경 변수 로드
load_dotenv()
openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__, static_folder='public', static_url_path='')
app.secret_key = "your_secret_key"  # Flask 세션을 위한 키

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("question")

    if not user_input:
        return jsonify({"error": "질문을 입력하세요."}), 400

    # 세션에서 대화 기록 가져오기 (없으면 초기화)
    if "messages" not in session:
        session["messages"] = [{"role": "system", "content": "You are a helpful assistant."}]

    # 사용자 입력 추가
    session["messages"].append({"role": "user", "content": user_input})
    
    print(session["messages"])
    print('-' * 50)

    # GPT API 호출
    response = openai.chat.completions.create(
        model="gpt-4",  # 사용할 모델
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
