# pip install requests
import requests

MODEL_NAME = "qwen2.5:1.5b"

conversation_history = ""

print("로컬 Qwen 채팅 시작")
print("종료하려면 exit 입력\n")

while True:
    user_input = input("나: ")
    if user_input.lower() == "exit":
        print("프로그램 종료")
        break

    # 대화 누적
    conversation_history += f"\n사용자: {user_input}\nAI: "

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": MODEL_NAME,
            "prompt": conversation_history,
            "stream": False
        }
    )

    ai_response = response.json()["response"]

    print(f"\nQwen: {ai_response}\n")

    # AI 응답도 히스토리에 추가
    conversation_history += ai_response
