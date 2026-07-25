# gpt-4o-audio - 2단계: 오디오 '입력' → 이해하고 답변
# pip install openai python-dotenv
#
# 1단계는 텍스트로 물었다. 여기선 '오디오 파일을 그대로' 모델에 넣는다.
# 단순 받아쓰기(STT)와 달리, 내용을 '이해/추론'해서 답한다 (요약·질의응답 등).

import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

AUDIO_PATH = 'question.wav'   # 같은 폴더에 음성 파일을 두세요 (wav/mp3)
with open(AUDIO_PATH, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')

completion = client.chat.completions.create(
    model='gpt-4o-audio-preview',
    modalities=['text'],                   # 여기선 텍스트로만 답
    messages=[{
        'role': 'user',
        'content': [
            {'type': 'text', 'text': '이 오디오의 내용을 한국어로 요약하고, 질문이면 답해줘.'},
            # 오디오는 input_audio 블록으로 전달 (data=base64, format=wav/mp3)
            {'type': 'input_audio', 'input_audio': {'data': b64, 'format': 'wav'}},
        ],
    }],
)

print(completion.choices[0].message.content)
