# pip install anthropic python-dotenv
#
# 3단계: 멀티턴 대화.
# Anthropic API 는 "상태가 없다(stateless)" — 서버가 이전 대화를 기억하지 않는다.
# 그래서 매 호출마다 지금까지의 대화 전체(messages)를 다시 보내야 한다.
# user / assistant 를 번갈아 쌓아주면 모델이 맥락을 이어간다.

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-haiku-4-5"

# 대화 기록을 리스트로 직접 관리한다.
messages = []

def ask(user_text):
    # 1) 사용자 메시지 추가
    messages.append({"role": "user", "content": user_text})
    # 2) 지금까지의 전체 대화를 보낸다
    reply = client.messages.create(model=MODEL, max_tokens=300, messages=messages)
    answer = reply.content[0].text
    # 3) 모델 답변도 기록에 추가 → 다음 턴에서 맥락이 된다
    messages.append({"role": "assistant", "content": answer})
    return answer

print("Q: 내 이름은 홍길동이야.")
print("A:", ask("내 이름은 홍길동이야."))
print()
print("Q: 내 이름이 뭐였지?")
print("A:", ask("내 이름이 뭐였지?"))   # 앞 대화를 같이 보냈으므로 '홍길동' 을 기억한다
