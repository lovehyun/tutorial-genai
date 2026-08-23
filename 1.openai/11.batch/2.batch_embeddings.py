# Batch - 2단계(실용): 대량 임베딩을 배치로 (RAG 인덱싱 비용 50%↓)
# pip install openai python-dotenv
#
# RAG 에서 문서 청크가 수천~수만 개면 동기 임베딩은 느리고 비싸다.
# Batch 로 한 번에 올리면 비용 절반 (급하지 않은 인덱싱 작업에 적합).
# endpoint 만 /v1/embeddings 로 바꾸면 1단계와 흐름이 동일하다.

import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 실제로는 문서를 청킹한 결과 리스트가 들어온다 (여기선 예시 3개)
chunks = [
    'NVMe 는 SSD 의 인터페이스 규격으로 PCIe 를 사용한다.',
    'RAG 는 검색 증강 생성으로 할루시네이션을 줄인다.',
    '임베딩은 텍스트를 의미 벡터로 바꾸는 기술이다.',
]

# ① JSONL — endpoint 가 /v1/embeddings
with open('embed_input.jsonl', 'w', encoding='utf-8') as f:
    for i, c in enumerate(chunks):
        f.write(json.dumps({
            'custom_id': f'chunk-{i}',
            'method': 'POST',
            'url': '/v1/embeddings',
            'body': {'model': 'text-embedding-3-small', 'input': c},
        }, ensure_ascii=False) + '\n')

# ② 업로드 → ③ 배치 생성
up = client.files.create(file=open('embed_input.jsonl', 'rb'), purpose='batch')
batch = client.batches.create(
    input_file_id=up.id,
    endpoint='/v1/embeddings',
    completion_window='24h',
)
print('배치 생성:', batch.id)

# ④ 폴링
while batch.status not in ('completed', 'failed', 'expired', 'cancelled'):
    time.sleep(15)
    batch = client.batches.retrieve(batch.id)
    print('  상태:', batch.status)

# ⑤ 결과 — custom_id 로 벡터 매칭 (그대로 벡터DB에 저장하면 됨)
if batch.status == 'completed':
    out = client.files.content(batch.output_file_id).text
    for line in out.splitlines():
        row = json.loads(line)
        vec = row['response']['body']['data'][0]['embedding']
        print(f"[{row['custom_id']}] dim={len(vec)}  앞3={[round(x, 4) for x in vec[:3]]}")
else:
    print('배치 미완료:', batch.status)
