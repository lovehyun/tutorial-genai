# gpt-4o-audio - 3단계(실용): 오디오 입력 → 오디오 출력 (음성 대화 한 턴, 단일 모델)
# pip install openai sounddevice scipy python-dotenv
#
# 마이크로 녹음한 '음성 질문'을 넣고 '음성 답변'을 받는다.
# = (STT → GPT → TTS) 3단을 한 번의 호출로. 실시간 스트리밍 앱은 9.webrtc_app/ 과 비교.

import os
import base64
import tempfile
import sounddevice as sd
from scipy.io.wavfile import write
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 1) 마이크로 5초 녹음 → wav
SR, SEC = 16000, 5
print(f'{SEC}초간 질문을 말하세요...')
rec = sd.rec(int(SEC * SR), samplerate=SR, channels=1)
sd.wait()
tmp = os.path.join(tempfile.gettempdir(), 'voice_q.wav')
write(tmp, SR, rec)
with open(tmp, 'rb') as f:
    q_b64 = base64.b64encode(f.read()).decode('utf-8')

# 2) 오디오 입력 → 오디오 출력 (한 호출)
completion = client.chat.completions.create(
    model='gpt-4o-audio-preview',
    modalities=['text', 'audio'],
    audio={'voice': 'alloy', 'format': 'wav'},
    messages=[{
        'role': 'user',
        'content': [
            {'type': 'text', 'text': '아래 음성 질문에 한국어로 간단히 답해줘.'},
            {'type': 'input_audio', 'input_audio': {'data': q_b64, 'format': 'wav'}},
        ],
    }],
)

msg = completion.choices[0].message
print('답변(텍스트):', msg.audio.transcript)
with open('reply.wav', 'wb') as f:
    f.write(base64.b64decode(msg.audio.data))
print('저장: reply.wav (재생해 보세요)')
