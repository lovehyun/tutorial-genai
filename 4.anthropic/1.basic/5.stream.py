import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

# Anthropic 클라이언트 초기화
client = anthropic.Anthropic(api_key=api_key)

def stream_response(prompt, model="claude-3-7-sonnet-20250219"):
    """스트리밍 응답 구현"""
    print("응답 스트리밍 중...")
    
    with client.messages.stream(
        model=model,
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    ) as stream:
        # 전체 응답 저장용
        full_response = ""
        
        # 스트림 처리
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text
            
    print("\n\n스트리밍 완료!")
    return full_response

# 사용 예시
if __name__ == "__main__":
    user_prompt = input("질문을 입력하세요: ")
    full_response = stream_response(user_prompt)
