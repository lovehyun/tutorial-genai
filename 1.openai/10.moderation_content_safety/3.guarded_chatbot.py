# Moderation - 3단계(실용): 입력을 검사해 '통과한 것만' 챗봇에 전달
# pip install openai python-dotenv
#
# 실전 패턴: 사용자 입력 → (1) Moderation 으로 안전성 검사 → 안전하면 (2) LLM 호출, 아니면 차단.
# 비용·정책 사고를 막는 가장 기본적인 가드.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def check_input(text):
    """(안전여부, 걸린_카테고리) 반환"""
    r = client.moderations.create(model='omni-moderation-latest', input=text)
    res = r.results[0]
    if res.flagged:
        cats = [c for c, v in res.categories.model_dump().items() if v]
        return False, cats
    return True, []


def ask_llm(text):
    r = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': '당신은 친절한 AI 도우미입니다.'},
            {'role': 'user', 'content': text},
        ],
    )
    return r.choices[0].message.content


if __name__ == '__main__':
    print('안전 가드 챗봇 (종료: exit)')
    while True:
        user = input('\n나: ').strip()
        if user.lower() == 'exit':
            break
        if not user:
            continue

        safe, cats = check_input(user)
        if not safe:
            print(f'챗봇: ⚠️ 정책 위반으로 답변할 수 없습니다. (걸린 항목: {cats})')
            continue

        print('챗봇:', ask_llm(user))
