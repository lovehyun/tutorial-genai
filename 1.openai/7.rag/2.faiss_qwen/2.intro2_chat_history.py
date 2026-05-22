# pip install requests

import requests

MODEL_NAME = "qwen2.5:1.5b"

# 전체 대화 기록
conversation_history = ""

def ask_qwen(user_input):
    global conversation_history

    # 사용자 입력 추가
    conversation_history += f"\n사용자: {user_input}\nAI: "

    # Ollama API 호출
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": MODEL_NAME,
            "prompt": conversation_history,
            "stream": False
        }
    )

    # AI 응답 추출
    ai_response = response.json()["response"]

    # 대화 기록 저장
    conversation_history += ai_response

    return ai_response


# -----------------------------
# CLI 채팅
# -----------------------------

print("Qwen CLI 채팅 시작")
print("종료하려면 exit 입력\n")

while True:

    user_input = input("나: ")

    if user_input.lower() == "exit":
        print("프로그램 종료")
        break

    response = ask_qwen(user_input)

    print(f"\nQwen: {response}\n")
