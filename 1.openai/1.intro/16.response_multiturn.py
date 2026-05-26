# OpenAI SDK - 16단계: Responses API 멀티턴 (previous_response_id 체인)
#
# 15단계 대비 새로 추가된 것:
#   대화를 '서버 측'에서 이어붙인다 — Responses API의 핵심 기능.
#
# 13.chat_multiturn.py 와의 차이:
#   - chat.completions:  매 호출마다 messages 리스트에 '이전 대화 전체'를 다시 보내야 함
#                        (클라이언트가 누적 관리)
#   - responses:         previous_response_id 만 넘기면 서버가 알아서 맥락을 이어감
#                        (클라이언트는 매번 작은 요청만 보내면 됨)
#
# 6.restapi_response_chain.py 의 SDK 버전이기도 하다 — 같은 일이지만 코드가 훨씬 짧다.
#
# 저장 기간: store=true(기본값)이면 응답이 서버에 30일간 저장된다.
#            30일이 지나면 previous_response_id 가 무효화되므로 그 시점부턴
#            input에 messages 배열로 대화 전체를 직접 보내야 한다.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 1) 첫 질문
r1 = client.responses.create(
    model='gpt-4o-mini',
    input='대한민국의 수도는 어디야?',
)
print('나: 대한민국의 수도는 어디야?')
print('챗봇:', r1.output_text)

# 2) 후속 — [관전 포인트] previous_response_id 로 1)을 가리킨다
#    '그 도시'가 무엇인지 적지 않았지만 서버가 맥락을 기억하고 있어 답한다.
r2 = client.responses.create(
    model='gpt-4o-mini',
    input='그 도시의 인구는 얼마야?',
    previous_response_id=r1.id,
)
print('\n나: 그 도시의 인구는 얼마야?')
print('챗봇:', r2.output_text)

# 3) 한 번 더 — [관전 포인트] 직전 응답의 id를 또 가리킨다 (체인이 계속 이어진다)
r3 = client.responses.create(
    model='gpt-4o-mini',
    input='거기서 가볼 만한 관광지 세 곳만 알려줘.',
    previous_response_id=r2.id,
)
print('\n나: 거기서 가볼 만한 관광지 세 곳만 알려줘.')
print('챗봇:', r3.output_text)

# 핵심: 매 호출에 previous_response_id 만 바꿔주면 된다.
# chat.completions(13단계)에서는 messages 리스트에 사용자/모델 메시지를 매번 다 누적해야 했다.
