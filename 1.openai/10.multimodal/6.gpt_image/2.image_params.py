# OpenAI 이미지 생성 - 2단계: size / quality 파라미터 비교
# pip install openai python-dotenv
#
# 품질과 크기를 바꿔가며 결과·비용 차이를 본다.

import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

prompt = '귀여운 로봇 캐릭터, 미니멀 플랫 일러스트'


def save(b64, filename):
    with open(filename, 'wb') as f:
        f.write(base64.b64decode(b64))
    print('저장:', filename)


# quality: low / medium / high / auto — 높을수록 품질↑ 비용↑
for quality in ['low', 'medium']:
    result = client.images.generate(
        model='gpt-image-1.5', prompt=prompt, size='1024x1024', quality=quality,
    )
    save(result.data[0].b64_json, f'robot_{quality}.png')

# size 옵션: '1024x1024'(정사각) / '1024x1536'(세로) / '1536x1024'(가로)
result = client.images.generate(
    model='gpt-image-1.5', prompt=prompt, size='1536x1024', quality='low',
)
save(result.data[0].b64_json, 'robot_wide.png')
