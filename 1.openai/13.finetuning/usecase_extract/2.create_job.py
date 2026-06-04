# Fine-tuning use-case [구조화 추출] - 2단계: 업로드 → 잡 생성 → 폴링
# (흐름은 루트 13.finetuning/2.create_job.py 와 동일 — 데이터만 추출용)
# ⚠️ 과금·시간 소요.

import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

train_file = client.files.create(file=open('train.jsonl', 'rb'), purpose='fine-tune')
print('업로드:', train_file.id)

job = client.fine_tuning.jobs.create(
    training_file=train_file.id,
    model='gpt-4o-mini-2024-07-18',
)
print('잡 생성:', job.id, '|', job.status)

while job.status not in ('succeeded', 'failed', 'cancelled'):
    time.sleep(30)
    job = client.fine_tuning.jobs.retrieve(job.id)
    print('  상태:', job.status)

if job.status == 'succeeded':
    print('\n완성 모델:', job.fine_tuned_model)
    print('  export FT_MODEL=' + str(job.fine_tuned_model) + '  후 3.use_finetuned.py 실행')
else:
    print('실패/취소:', job.status)
