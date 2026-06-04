# OpenAI TTS - 1단계: 텍스트 → 음성(mp3) 만들기
# pip install openai python-dotenv
#
# TTS(Text-To-Speech) = 텍스트를 '입력'으로 받아 음성을 '생성'하는 것 (텍스트 → 오디오).
#   ↔ 음성을 텍스트로 받아쓰는 STT(음성 인식)는 8.whisper_stt/ 참고.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

text = '안녕하세요. OpenAI 음성 합성 예제입니다. 반갑습니다.'

# 핵심: audio.speech.create — model / voice / input
response = client.audio.speech.create(
    model='gpt-4o-mini-tts',   # 최신 경량 TTS (대안: tts-1, tts-1-hd)
    voice='alloy',             # 목소리 (2.tts_voices.py 에서 비교)
    input=text,
)

# 응답을 파일로 저장 (기본 포맷 mp3)
response.write_to_file('output.mp3')
print('저장: output.mp3')
