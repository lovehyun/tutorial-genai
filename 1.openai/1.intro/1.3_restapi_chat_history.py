# pip install python-dotenv
import os, requests
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
openai_api_key = os.getenv('OPENAI_API_KEY')

def ask_chatgpt(messages: list,
                model: str = "gpt-3.5-turbo",
                max_tokens: int = 150,
                temperature: float = 0.7,
                top_p: float = 0.9,
                frequency_penalty: float = 0.5,
                presence_penalty: float = 0.6) -> str:
    """
    messages 형식의 대화 히스토리를 받아 GPT 응답을 반환합니다.
    실패 시 예외를 발생시킵니다.
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status() # 4xx / 5xx 시 예외
    return resp.json()["choices"][0]["message"]["content"]

# 개선된 버전 - 대화 히스토리 유지
def chat_with_history():
    print("챗봇과 대화를 시작합니다. 종료하려면 'quit' 또는 'exit'를 입력하세요.")
    print("="*50)
    
    # 대화 히스토리 저장
    messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}]
    
    while True:
        user_input = input("\n당신: ").strip()
        
        if user_input.lower() in ['quit', 'exit', '종료', '끝']:
            print("대화를 종료합니다. 안녕히 가세요!")
            break
        
        if not user_input:
            print("메시지를 입력해주세요.")
            continue
        
        # 사용자 메시지를 히스토리에 추가
        messages.append({'role': 'user', 'content': user_input})
        
        try:
            print("\n챗봇이 응답을 생성중입니다...")
            bot_response = ask_chatgpt(messages)
            # 봇 응답 저장
            messages.append({"role": "assistant", "content": bot_response})
            print(f"\n챗봇: {bot_response}")
            print("-"*30)
        except Exception as e:
            print(f"❗️요청 실패: {e}")
            print("다시 시도해주세요.")

if __name__ == "__main__":
    # 히스토리 유지 버전 실행
    chat_with_history()
