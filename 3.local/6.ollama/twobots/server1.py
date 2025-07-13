# curl -X POST "http://localhost:5001/ask" -H "Content-Type: application/json" -d '{"question": "hello?"}'
# curl -X POST "http://localhost:5001/ask" -H "Content-Type: application/json" -d "{""question"": ""hello?""}"

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

SERVER2_URL = "http://localhost:5002/ask"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "안녕!")  # 기본 질문
    print(f"[Bot1] 질문: {question}")

    # Server2에 질문 전달
    response = requests.post(SERVER2_URL, json={"question": question})
    answer = response.json().get("answer", "응답 없음")

    print(f"[Bot1] 응답: {answer}")
    return jsonify({"answer": answer})

@app.route("/ask-safe", methods=["POST"])
def ask_safe():
    data = request.json
    question = data.get("question", "안녕!")  # 기본 질문
    print(f"[Bot1] 질문: {question}")

    try:
        # Server2로 요청 보내기
        response = requests.post(SERVER2_URL, json={"question": question}, timeout=5)
        response.raise_for_status()  # 응답 코드가 200이 아니면 예외 발생

        # 정상적인 응답 처리
        answer = response.json().get("answer", "응답 없음")
        print(f"[Bot1] 응답: {answer}")

    except requests.exceptions.ConnectionError:
        print("[Bot1] 서버2에 연결할 수 없습니다. 서버2가 실행 중인지 확인하세요.")
        return jsonify({"error": "Server2 is not available"}), 503

    except requests.exceptions.Timeout:
        print("[Bot1] 서버2 요청이 시간 초과되었습니다.")
        return jsonify({"error": "Server2 request timed out"}), 504

    except requests.exceptions.RequestException as e:
        print(f"[Bot1] 서버2 요청 중 오류 발생: {e}")
        return jsonify({"error": "Server2 request failed"}), 500

    print(f"[Bot1] 응답: {answer}")
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(port=5001)
