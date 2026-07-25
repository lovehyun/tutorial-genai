# Batch - 1단계: 여러 요청을 한 번에 비동기 처리 (50% 할인, 최대 24h)
# pip install openai python-dotenv
#
# Batch API 는 '즉시 응답'이 아니라 '대량을 싸게' 처리하는 용도다 (분류/요약/번역/임베딩 대량 작업).
# 흐름: ① 요청들을 JSONL 로 → ② 파일 업로드 → ③ 배치 생성 → ④ 완료까지 폴링 → ⑤ 결과 다운로드

import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

questions = ['파이썬이 뭐야? 한 줄로.', 'RAG 가 뭐야? 한 줄로.', '임베딩이 뭐야? 한 줄로.']

# ① JSONL: 한 줄 = 한 요청. custom_id 로 나중에 결과를 매칭한다.
with open('batch_input.jsonl', 'w', encoding='utf-8') as f:
    for i, q in enumerate(questions):
        f.write(json.dumps({
            'custom_id': f'q-{i}',
            'method': 'POST',
            'url': '/v1/chat/completions',
            'body': {'model': 'gpt-4o-mini', 'messages': [{'role': 'user', 'content': q}]},
        }, ensure_ascii=False) + '\n')

# ② 업로드 (purpose='batch')
up = client.files.create(file=open('batch_input.jsonl', 'rb'), purpose='batch')

# ③ 배치 생성
batch = client.batches.create(
    input_file_id=up.id,
    endpoint='/v1/chat/completions',
    completion_window='24h',
)
print('배치 생성:', batch.id, '| 상태:', batch.status)

# ④ 완료까지 폴링 (실제로는 수 분~24h 걸릴 수 있음)
while batch.status not in ('completed', 'failed', 'expired', 'cancelled'):
    time.sleep(15)
    batch = client.batches.retrieve(batch.id)
    print('  상태:', batch.status, '|', batch.request_counts)

# ⑤ 결과 다운로드 (출력도 JSONL — custom_id 로 매칭)
if batch.status == 'completed':
    out = client.files.content(batch.output_file_id).text
    for line in out.splitlines():
        row = json.loads(line)
        ans = row['response']['body']['choices'][0]['message']['content']
        print(f"\n[{row['custom_id']}] {ans}")
else:
    print('배치 미완료:', batch.status)
