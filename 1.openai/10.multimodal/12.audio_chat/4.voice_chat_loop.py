# gpt-4o-audio - 4단계(실용): 연속 음성 대화 (계속 묻고 → 자동 재생 → 반복, 맥락 유지)
# pip install openai sounddevice scipy python-dotenv
#
# 3.voice_chat 은 '한 턴'(녹음 → 파일 저장)만 했다. 여기선:
#   · Enter 로 녹음 시작 → 답변을 '자동 재생' (저장·수동 재생 X)
#   · 대화 히스토리를 누적해 '맥락이 이어지는' 연속 대화
#   · q 입력 시 종료

import os
import base64
import tempfile
import sounddevice as sd
from scipy.io.wavfile import write, read
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

SR = 16000          # 녹음 샘플레이트
RECORD_SEC = 5      # 한 번 말할 시간(초)


def record_to_b64():
    """마이크로 RECORD_SEC 초 녹음 → base64 wav"""
    print(f'🎤 말하세요... ({RECORD_SEC}초)')
    rec = sd.rec(int(RECORD_SEC * SR), samplerate=SR, channels=1)
    sd.wait()
    path = os.path.join(tempfile.gettempdir(), 'voice_q.wav')
    write(path, SR, rec)
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def play_b64_wav(b64):
    """응답 오디오(base64 wav)를 바로 재생 — 저장·수동 재생 불필요"""
    path = os.path.join(tempfile.gettempdir(), 'voice_a.wav')
    with open(path, 'wb') as f:
        f.write(base64.b64decode(b64))
    sr, data = read(path)        # wav 헤더의 실제 샘플레이트 사용 (모델 출력은 보통 24kHz)
    sd.play(data, sr)
    sd.wait()                    # 재생이 끝날 때까지 대기


# 대화 히스토리 — 누적해서 맥락 유지
messages = [{'role': 'system', 'content': '너는 한국어로 짧고 자연스럽게 대화하는 음성 비서야.'}]

print('연속 음성 대화 — [Enter]=말하기, q=종료')
while True:
    cmd = input('\n[Enter] 말하기 / q 종료 > ').strip().lower()
    if cmd == 'q':
        break

    # 1) 녹음 → 사용자 턴 추가
    q_b64 = record_to_b64()
    messages.append({
        'role': 'user',
        'content': [{'type': 'input_audio', 'input_audio': {'data': q_b64, 'format': 'wav'}}],
    })

    # 2) 오디오 입력 → 오디오 출력 (지금까지의 대화 전체를 함께 전송)
    completion = client.chat.completions.create(
        model='gpt-4o-audio-preview',
        modalities=['text', 'audio'],
        audio={'voice': 'alloy', 'format': 'wav'},
        messages=messages,
    )
    msg = completion.choices[0].message

    # 3) 답변: 텍스트 출력 + 오디오 '자동 재생'
    print('🤖', msg.audio.transcript)
    play_b64_wav(msg.audio.data)

    # 4) 맥락 유지: 어시스턴트 답변을 '텍스트(transcript)'로 히스토리에 추가
    #    (오디오 대신 텍스트를 넣어 과거 답변 오디오의 재전송·재과금을 줄인다)
    messages.append({'role': 'assistant', 'content': msg.audio.transcript})

    # 5) (선택) 비용 관리: 과거 'user 오디오'는 매 호출마다 다시 처리되어 비용이 커진다.
    #    긴 대화에서는 최근 N턴만 유지(아래)하거나, Whisper로 텍스트 전사해 보관하는 게 좋다.
    if len(messages) > 13:                       # system 1개 + 최근 6턴(12개)만 유지
        messages = messages[:1] + messages[-12:]

print('대화를 종료합니다.')
