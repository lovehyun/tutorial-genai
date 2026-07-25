# Fine-tuning - 2단계: 파일 업로드 → 파인튜닝 잡 생성 → 완료까지 폴링
# pip install openai python-dotenv
#
# 흐름: ① train.jsonl 업로드(purpose='fine-tune') → ② jobs.create → ③ 상태 폴링 → ④ ft 모델 ID 확인
#
# ⚠️ 주의: 파인튜닝은 '돈이 들고(학습 토큰 과금)' '시간이 걸린다(수 분~수십 분)'. 데모 실행 시 유의.

import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# ① 학습 파일 업로드 (1.prepare_data.py 로 만든 train.jsonl)
train_file = client.files.create(file=open('train.jsonl', 'rb'), purpose='fine-tune')
print('업로드 완료:', train_file.id)

# ② 파인튜닝 잡 생성
#    model 은 '파인튜닝 가능한 베이스 모델' 이어야 한다 (예: gpt-4o-mini 스냅샷).
job = client.fine_tuning.jobs.create(
    training_file=train_file.id,
    model='gpt-4o-mini-2024-07-18',
    # validation_file=val_file.id,            # (선택) 검증셋
    # hyperparameters={'n_epochs': 3},        # (선택) 에폭 등
)
print('잡 생성:', job.id, '| 상태:', job.status)

# ③ 완료까지 폴링 (running → succeeded). 실제로는 수 분 이상 걸릴 수 있음.
while job.status not in ('succeeded', 'failed', 'cancelled'):
    time.sleep(30)
    job = client.fine_tuning.jobs.retrieve(job.id)
    print('  상태:', job.status)

# ④ 결과: 파인튜닝된 모델 ID (ft:gpt-4o-mini-...:...:...)
if job.status == 'succeeded':
    print('\n완성된 모델:', job.fine_tuned_model)
    print('→ 이 ID 를 3.use_finetuned.py 의 FT_MODEL 환경변수로 넣어 사용하세요.')
    print('   예) export FT_MODEL=' + str(job.fine_tuned_model))
else:
    print('학습 실패/취소:', job.status)
