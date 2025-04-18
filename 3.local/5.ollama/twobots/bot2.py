import ollama
import time

CONVO_FILE = "conversation.txt"
MODEL = "mistral"

def get_response(prompt):
    response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return response['message']['content']

def main():
    while True:
        # bot1이 응답할 때까지 기다림
        time.sleep(5)

        # 최신 응답 읽기
        with open(CONVO_FILE, "r") as f:
            lines = f.readlines()
        
        if len(lines) % 2 == 1:  # bot2 차례 (홀수 줄)
            last_response = lines[-1].strip()
            print("[Bot1] 응답: ", last_response)
            
            # 새로운 질문 생성
            new_prompt = get_response(last_response)
            print("[Bot2] 응답: ", new_prompt)

            # 파일에 추가
            with open(CONVO_FILE, "a") as f:
                f.write(new_prompt + "\n")

if __name__ == "__main__":
    main()
