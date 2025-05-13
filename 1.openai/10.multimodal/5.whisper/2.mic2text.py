# pip install openai python-dotenv sounddevice scipy
import sounddevice as sd
from scipy.io.wavfile import write
from openai import OpenAI
from dotenv import load_dotenv
import tempfile
import os

# .env에서 API 키 로드
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 설정: 샘플링 레이트와 녹음 시간
SAMPLE_RATE = 44100
DURATION = 5  # 녹음 시간(초)

def record_audio():
    print(f"{DURATION}초 동안 말하세요...")
    audio = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()
    print("녹음 완료!")

    temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    write(temp_wav.name, SAMPLE_RATE, audio)
    return temp_wav.name

def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="ko",  # 한국어
            response_format="text"
        )
    return transcript

if __name__ == "__main__":
    wav_file = record_audio()
    text = transcribe_audio(wav_file)
    print("\n전사 결과:")
    print(text)
    os.remove(wav_file)  # 임시 파일 삭제
