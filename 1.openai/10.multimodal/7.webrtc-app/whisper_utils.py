import os
import subprocess
from dotenv import load_dotenv

load_dotenv()
USE_MODE = os.getenv("WHISPER_MODE", "openai_whisper")  # local_webp, local_wav, openai_whisper

if USE_MODE.startswith("local"):
    from faster_whisper import WhisperModel
    model = WhisperModel("base", device="cpu")
# 모델 이름	크기	대략적 VRAM 요구	특징
# tiny	~39 MB	1GB 이하	매우 빠름, 정확도 낮음
# base	~74 MB	1–2GB	빠름, 기본 정확도
# small	~244 MB	2–4GB	균형 잡힌 속도와 정확도
# medium	~769 MB	4–6GB	높은 정확도, 느림
# large-v1	~1.5GB	8GB 이상	최고 정확도, 느림
# large-v2	~1.5GB	8GB 이상	large-v1보다 약간 향상된 정확도
# large-v3	(실험중)	8GB 이상	최신 대형 모델 (공식 배포X, 커뮤니티 기반)


if USE_MODE == "openai_whisper":
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def transcribe_audio(file_path):
    if USE_MODE == "openai_whisper":
        with open(file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                language="ko"
            )
        return response.strip()

# def transcribe_audio(file_path):
#     if USE_MODE == "openai_whisper":
#         # webm → wav 변환 (OpenAI가 codec 문제로 인한 에러를 피하기 위해 필요할 수 있음)
#         wav_path = file_path + ".converted.wav"
#         subprocess.run([
#             "ffmpeg", "-y", "-i", file_path, "-ar", "16000", "-ac", "1", wav_path
#         ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#         with open(wav_path, "rb") as audio_file:
#             response = client.audio.transcriptions.create(
#                 model="whisper-1",
#                 file=audio_file,
#                 response_format="text",
#                 language="ko"
#             )
#         os.remove(wav_path)
#         return response.strip()

    elif USE_MODE == "local_wav":
        # WAV 전용 (ffmpeg 변환 없이)
        segments, _ = model.transcribe(file_path, language="ko")
        return " ".join(segment.text for segment in segments)

    elif USE_MODE == "local_webp":
        # WEBM → WAV 변환 후 처리
        wav_path = file_path + ".wav"
        subprocess.run([
            "ffmpeg", "-y", "-i", file_path, "-ar", "16000", "-ac", "1", wav_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        segments, _ = model.transcribe(wav_path, language="ko")
        os.remove(wav_path)
        return " ".join(segment.text for segment in segments)

    else:
        raise ValueError("WHISPER_MODE must be one of: openai_whisper, local_wav, local_webp")
