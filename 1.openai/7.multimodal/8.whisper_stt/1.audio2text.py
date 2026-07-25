from openai import OpenAI
from dotenv import load_dotenv
import os

# .env에서 API 키 로드
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Whisper API 호출 (요금: $0.006 / 분)
def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",   # 'json', 'srt', 'verbose_json' 등도 가능
            language="ko"             # 한국어
        )
    return transcript

# 테스트 실행
result = transcribe_audio("sample.mp3")
print("전사 결과:\n", result)
