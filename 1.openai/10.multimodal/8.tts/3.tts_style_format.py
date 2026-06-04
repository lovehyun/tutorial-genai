# OpenAI TTS - 3단계: 말투(instructions) 지정 + 출력 포맷 바꾸기
# pip install openai python-dotenv
#
# gpt-4o-mini-tts 는 instructions 로 '어떻게 읽을지'(말투/감정)를 지시할 수 있다.
# response_format 으로 mp3 외에 wav/opus/aac/flac 등으로 받을 수 있다.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

text = '주문하신 음료가 준비되었습니다. 카운터에서 받아 가세요.'

# 1) 말투 지정 — 같은 문장을 다른 분위기로
response = client.audio.speech.create(
    model='gpt-4o-mini-tts',
    voice='nova',
    input=text,
    instructions='밝고 친절한 카페 직원처럼, 약간 빠르고 경쾌하게 말해줘.',
)
response.write_to_file('cheerful.mp3')
print('저장: cheerful.mp3 (말투 지정)')

# 2) 출력 포맷 변경 — wav 로 받기
response_wav = client.audio.speech.create(
    model='gpt-4o-mini-tts',
    voice='nova',
    input=text,
    response_format='wav',     # mp3(기본) / wav / opus / aac / flac / pcm
)
response_wav.write_to_file('output.wav')
print('저장: output.wav (wav 포맷)')
