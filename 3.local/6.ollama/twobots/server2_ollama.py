from flask import Flask, request, jsonify
import requests
import ollama

app = Flask(__name__)

SERVER1_URL = "http://localhost:5001/ask"
MODEL = "mistral"
MAX_CONVERSATIONS = 5  # 최대 대화 횟수
conversation_count = 0  # 현재 대화 횟수
REQUEST_TIMEOUT = 120

def get_response(prompt):
    """Ollama를 사용하여 응답 생성 (system 프롬프트 추가)"""
    try:
        response = ollama.chat(
            model=MODEL, 
            messages=[
                {"role": "system", "content": "당신은 짧고 간결하게 대답하는 AI 어시스턴트입니다."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['message']['content']
    except Exception as e:
        print(f"[Bot1] Ollama 응답 생성 중 오류 발생: {e}")
        return "Ollama 응답을 생성할 수 없습니다."

@app.route("/ask", methods=["POST"])
def ask():
    global conversation_count
    if conversation_count >= MAX_CONVERSATIONS:
        print("[Bot2] 대화 종료!")
        return jsonify({"answer": "대화를 종료합니다."})

    try:
        data = request.get_json(force=True)  # JSON 파싱 오류 방지
        question = data.get("question", "질문이 없습니다.")
        print(f"[Bot2] 받은 질문: {question}")

        answer = get_response(question)
        print(f"[Bot2] Ollama 응답: {answer}")

        conversation_count += 1

        if conversation_count < MAX_CONVERSATIONS:
            try:
                response = requests.post(SERVER1_URL, json={"question": answer}, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()  # HTTP 응답 코드가 200이 아닐 경우 예외 발생
            except requests.exceptions.ConnectionError:
                print("[Bot2] Server1에 연결할 수 없습니다.")
            except requests.exceptions.Timeout:
                print("[Bot2] Server1 요청이 시간 초과되었습니다.")
            except requests.exceptions.RequestException as e:
                print(f"[Bot2] Server1 요청 중 오류 발생: {e}")

        return jsonify({"answer": answer})

    except Exception as e:
        print(f"[Bot2] 요청 처리 중 오류 발생: {e}")
        return jsonify({"error": "요청을 처리하는 중 오류가 발생했습니다."}), 500

if __name__ == "__main__":
    app.run(port=5002, threaded=True)
