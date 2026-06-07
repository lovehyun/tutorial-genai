from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

SERVER1_URL = "http://localhost:5001/ask"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "질문이 없습니다.")
    print(f"[Bot2] 받은 질문: {question}")

    # 간단한 응답 로직
    answer = f"'{question}'에 대한 답변입니다."
    print(f"[Bot2] 응답: {answer}")

    # Server1에 응답 전달
    response = requests.post(SERVER1_URL, json={"question": answer})
    return jsonify({"answer": answer})

@app.route("/ask-safe", methods=["POST"])
def ask_safe():
    data = request.json
    question = data.get("question", "질문이 없습니다.")
    print(f"[Bot2] 받은 질문: {question}")

    # 간단한 응답 생성
    answer = f"'{question}'에 대한 답변입니다."
    print(f"[Bot2] 응답: {answer}")

    try:
        # 서버1로 다시 요청 보내기
        response = requests.post(SERVER1_URL, json={"question": answer}, timeout=5)
        response.raise_for_status()  # 응답 코드가 200이 아니면 예외 발생

    except requests.exceptions.ConnectionError:
        print("[Bot2] 서버1에 연결할 수 없습니다. 서버1이 실행 중인지 확인하세요.")
        return jsonify({"error": "Server1 is not available"}), 503

    except requests.exceptions.Timeout:
        print("[Bot2] 서버1 요청이 시간 초과되었습니다.")
        return jsonify({"error": "Server1 request timed out"}), 504

    except requests.exceptions.RequestException as e:
        print(f"[Bot2] 서버1 요청 중 오류 발생: {e}")
        return jsonify({"error": "Server1 request failed"}), 500

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(port=5002)
