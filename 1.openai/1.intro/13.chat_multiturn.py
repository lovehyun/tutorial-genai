# OpenAI SDK - 13단계: 멀티턴 대화 (chat.completions 방식, 클라이언트 누적)
#
# 12단계까지는 매 호출이 독립적이었다 — 모델은 직전 질문을 기억하지 못한다.
# 멀티턴의 핵심: messages 리스트에 '이전 대화'를 함께 담아 보내면 맥락이 이어진다.
#
# [assistant 역할의 쓰임]
#   모델의 지난 답변을 assistant 역할로 messages에 다시 넣어야
#   모델이 "내가 이렇게 답했지" 하고 맥락을 이어간다.
# 이 원리를 본격적으로 다루는 곳이 다음 폴더 3.chatbot2_history 다.
#
# 참고: Responses API(/v1/responses)는 이 누적을 서버가 대신 해준다 —
#       6.restapi_response_chain.py (REST) / 16.response_multiturn.py (SDK) 참고.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 대화 누적 리스트 — system 메시지로 시작한다.
messages = [
    {'role': 'system', 'content': '당신은 친절한 AI 도우미입니다.'},
]

def chat(user_input):
    # 1) 사용자 메시지를 리스트에 추가
    messages.append({'role': 'user', 'content': user_input})

    # 2) 지금까지의 '전체 대화'를 보낸다
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
    )
    answer = response.choices[0].message.content

    # 3) 모델의 답변도 assistant 역할로 추가 → 다음 턴에서 기억된다
    messages.append({'role': 'assistant', 'content': answer})
    return answer

if __name__ == '__main__':
    # 질문을 이어서 한다. 두 번째 질문엔 '그 도시'가 어디인지 적지 않았지만,
    # 1번 답변이 messages에 남아 있어 모델이 맥락을 이어서 답한다.
    # 질문을 더 넣어보려면 아래 줄의 주석을 풀어보세요.
    turns = [
        '대한민국의 수도는 어디야?',
        '그 도시의 인구는 얼마야?',
        # '거기서 유명한 관광지 세 곳만 알려줘',
    ]
    for question in turns:
        print(f'\n나: {question}')
        print('챗봇:', chat(question))
