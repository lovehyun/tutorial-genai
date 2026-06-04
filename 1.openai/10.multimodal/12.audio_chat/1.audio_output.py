# gpt-4o-audio - 1단계: 텍스트 질문 → '음성 답변' (모델이 직접 말함)
# pip install openai python-dotenv
#
# gpt-4o-audio 는 Whisper(STT)+TTS 2단계 파이프라인이 아니라, 오디오를 '직접 입출력'하는 멀티모달 챗 모델이다.
#   ↔ 받아쓰기만(STT): 8.whisper_stt/   ·   텍스트→음성만(TTS): 10.tts/
# 여기선 가장 단순하게: 텍스트로 묻고 '음성 답변'을 받는다 (modalities 에 audio 추가).

import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

completion = client.chat.completions.create(
    model='gpt-4o-audio-preview',          # 오디오 입출력 챗 모델 (신형 별칭: gpt-audio)
    modalities=['text', 'audio'],          # 출력에 audio 포함 요청
    audio={'voice': 'alloy', 'format': 'wav'},
    messages=[{'role': 'user', 'content': '한국어로 짧고 친절한 인사를 해줘.'}],
)

msg = completion.choices[0].message
# 응답에는 텍스트(transcript)와 오디오(base64)가 함께 온다
print('답변(텍스트):', msg.audio.transcript)
with open('answer.wav', 'wb') as f:
    f.write(base64.b64decode(msg.audio.data))
print('저장: answer.wav (재생해 보세요)')
