from flask import Flask, request, jsonify
import requests
import ollama

app = Flask(__name__)

SERVER1_URL = "http://localhost:5001"
# MODEL = "mistral"
MODEL = "gemma:2b"  # 경량화된 모델로 변경 (Google 출시)
MAX_CONVERSATIONS = 5  # 최대 대화 횟수
conversation_count = {"story": 0, "debate": 0}  # 각각의 대화 횟수 카운트
REQUEST_TIMEOUT = 300

story_history = []  # 소설 내용 저장
debate_history = []  # 토론 내용 저장


# --------------- Story 기능 ---------------
def get_story_response():
    """Ollama를 사용하여 소설 문단 생성"""
    try:
        story_context = "\n".join(story_history[-5:])  # 최근 5개 문단만 유지
        response = ollama.chat(
            model=MODEL, 
            messages=[
                {"role": "system", "content": "당신은 창의적인 소설을 작성하는 작가입니다. 이야기를 자연스럽게 한 문장만 이어서 작성하세요."},
                {"role": "user", "content": f"현재 이야기:\n{story_context}\n\n내용을 반복하지 말고 다음 문장을 이어서 작성하세요."}
            ],
            options={"max_tokens": 50}  # 최대 문장 길이 제한
        )
        return response['message']['content'].strip()
    except Exception as e:
        print(f"[Bot2] Ollama 응답 생성 중 오류 발생: {e}")
        return "이야기를 이어갈 수 없습니다."


@app.route("/story", methods=["POST"])
def story():
    global conversation_count
    if conversation_count["story"] >= MAX_CONVERSATIONS:
        print("\n[Bot2] 소설 종료!")
        return jsonify({"answer": "\n".join(story_history) + "\n\n(소설이 끝났습니다.)"})

    try:
        data = request.get_json(force=True)  # JSON 파싱 오류 방지
        question = data.get("question")
        print(f"\n[Bot2] 받은 문단: {question}")

        story_history.append(question)  # 이전 문단 저장
        new_paragraph = get_story_response()  # 새로운 문단 생성
        print(f"\n[Bot2] 작성한 문단: {new_paragraph}")

        story_history.append(new_paragraph)  # 새로운 문단 저장
        conversation_count["story"] += 1  # 대화 횟수 증가

        if conversation_count["story"] < MAX_CONVERSATIONS:
            try:
                response = requests.post(f"{SERVER1_URL}/story", json={"question": new_paragraph}, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()  # 응답 코드가 200이 아닐 경우 예외 발생
            except requests.exceptions.RequestException as e:
                print(f"[Bot2] Server1 요청 중 오류 발생: {e}")

        return jsonify({"answer": new_paragraph})

    except Exception as e:
        print(f"[Bot2] 요청 처리 중 오류 발생: {e}")
        return jsonify({"error": "요청을 처리하는 중 오류가 발생했습니다."}), 500


# --------------- Debate 기능 (반대 입장) ---------------
def get_debate_response():
    """AI 찬반 토론 생성 (반대 입장)"""
    try:
        debate_context = "\n".join(debate_history[-5:])  # 최근 5개의 토론 내용을 유지
        response = ollama.chat(
            model=MODEL, 
            messages=[
                {"role": "system", "content": "당신은 AI 예술을 반대하는 입장의 토론자입니다. 상대방의 찬성 의견에 논리적으로 반박하며 토론을 이어가세요."},
                {"role": "user", "content": f"현재까지의 토론:\n{debate_context}\n\n상대방의 주장을 반박하며 반대 입장에서 논리를 펼치세요."}
            ],
            options={"max_tokens": 50}  # 응답 길이 제한 (짧은 문장 유지)
        )
        return response['message']['content'].strip()
    except Exception as e:
        print(f"[Bot2] Ollama 응답 생성 중 오류 발생: {e}")
        return "논쟁을 이어갈 수 없습니다."


@app.route("/debate", methods=["POST"])
def debate():
    global conversation_count
    if conversation_count["debate"] >= MAX_CONVERSATIONS:
        print("\n[Bot2] 토론 종료!")
        return jsonify({"answer": "\n".join(debate_history) + "\n\n(토론이 끝났습니다.)"})

    try:
        data = request.get_json(force=True)  # JSON 파싱 오류 방지
        question = data.get("question")
        print(f"\n[Bot2] 받은 토론 문장: {question}")

        debate_history.append(question)  # 이전 토론 내용 저장
        new_argument = get_debate_response()  # 새로운 반박 생성
        print(f"\n[Bot2] 작성한 반박: {new_argument}")

        debate_history.append(new_argument)  # 새로운 토론 내용 저장
        conversation_count["debate"] += 1  # 대화 횟수 증가

        if conversation_count["debate"] < MAX_CONVERSATIONS:
            try:
                response = requests.post(f"{SERVER1_URL}/debate", json={"question": new_argument}, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"[Bot2] Server1 요청 중 오류 발생: {e}")

        return jsonify({"answer": new_argument})

    except Exception as e:
        print(f"[Bot2] 요청 처리 중 오류 발생: {e}")
        return jsonify({"error": "요청을 처리하는 중 오류가 발생했습니다."}), 500


if __name__ == "__main__":
    app.run(port=5002)
