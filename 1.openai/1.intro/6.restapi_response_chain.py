# OpenAI REST API - 6단계: Responses API — 대화 이어가기 (previous_response_id)
#
# 5단계 대비 새로 추가된 것:
#   대화를 '서버 측'에서 이어붙인다 — Responses API의 가장 큰 특징.
#
# Chat Completions와의 차이:
#   - chat.completions: 매 호출마다 messages 리스트에 '이전 대화 전체'를 다시 보내야 함
#   - responses:        previous_response_id 만 넘기면 서버가 알아서 맥락을 이어감
#     → 클라이언트는 매번 작은 요청만 보내면 된다.
#
# (chat.completions 방식의 멀티턴은 13.chat_multiturn.py 와,
#  같은 일을 SDK로 더 간결하게 한 버전은 16.response_multiturn.py 와 비교해 보세요.)
#
# 저장 기간:
#   응답은 store=true(기본값)이면 서버에 30일 동안 저장된다. 30일이 지나면
#   previous_response_id 가 무효화되므로, 그 시점부턴 input에 messages 배열로
#   대화 전체를 직접 보내야 한다. 저장을 원치 않으면 store=false 로 호출하면 된다.

import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
openai_api_key = os.getenv('OPENAI_API_KEY')

URL = 'https://api.openai.com/v1/responses'
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {openai_api_key}',
}

# 응답에서 답변 텍스트만 꺼내는 도우미 — output[0].content[0].text 위치
# (SDK는 response.output_text 한 줄이면 되지만 raw HTTP는 직접 접근해야 한다)
def extract_text(data):
    return data['output'][0]['content'][0]['text']

# 1) 첫 질문 — 서버가 응답을 저장하고 id를 돌려준다
r1 = requests.post(URL, headers=HEADERS, json={
    'model': 'gpt-4o-mini',
    'input': '대한민국의 수도는 어디야?',
}).json()
print('나: 대한민국의 수도는 어디야?')
print('챗봇:', extract_text(r1))

# 2) 후속 질문 — [관전 포인트] previous_response_id 로 1)을 가리킨다
#    질문에 '그 도시'가 무엇인지 적지 않았지만, 서버가 맥락을 기억하고 있어 답할 수 있다.
r2 = requests.post(URL, headers=HEADERS, json={
    'model': 'gpt-4o-mini',
    'input': '그 도시의 인구는 얼마야?',
    'previous_response_id': r1['id'],
}).json()
print('\n나: 그 도시의 인구는 얼마야?')
print('챗봇:', extract_text(r2))

# 3) 한 번 더 — [관전 포인트] 직전 응답의 id를 또 가리킨다 (체인이 계속 이어진다)
r3 = requests.post(URL, headers=HEADERS, json={
    'model': 'gpt-4o-mini',
    'input': '거기서 가볼 만한 관광지 세 곳만 알려줘.',
    'previous_response_id': r2['id'],
}).json()
print('\n나: 거기서 가볼 만한 관광지 세 곳만 알려줘.')
print('챗봇:', extract_text(r3))

# 핵심: 매 호출에 previous_response_id 만 바꿔주면 된다.
# chat.completions에서는 messages 리스트에 사용자/모델 메시지를 매번 다 누적해야 했다
# (13.multiturn.py 참고). Responses는 그 일을 서버가 대신 한다.
