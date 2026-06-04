# OpenAI TTS - 2단계: 여러 목소리(voice) 비교
# pip install openai python-dotenv
#
# 같은 문장을 여러 voice 로 합성해 파일로 저장하고 들어보며 고른다.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

text = '오늘 날씨가 정말 좋네요. 산책하기 딱 좋은 날입니다.'

# 대표적인 voice 들 (그 외: echo, fable, onyx, shimmer, coral, sage ...)
voices = ['alloy', 'nova', 'onyx']

for voice in voices:
    response = client.audio.speech.create(
        model='gpt-4o-mini-tts',
        voice=voice,
        input=text,
    )
    filename = f'voice_{voice}.mp3'
    response.write_to_file(filename)
    print('저장:', filename)
