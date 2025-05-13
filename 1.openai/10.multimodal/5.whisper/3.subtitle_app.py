# pip install gradio openai python-dotenv

import gradio as gr
from openai import OpenAI
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 오디오 전사 함수
def transcribe(audio):
    if audio is None:
        return "음성 입력이 없습니다."

    with open(audio, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="ko",  # 한국어
            response_format="text"
        )
    return result.strip()

# Gradio 인터페이스 구성
interface = gr.Interface(
    fn=transcribe,
    inputs=gr.Audio(type="filepath", label="말해보세요"),
    outputs=gr.Textbox(label="전사된 텍스트"),
    title="실시간 자막: Whisper 음성 인식 데모",
    description="마이크로 말한 내용을 Whisper를 통해 텍스트로 변환하여 자막처럼 보여줍니다."
)

# 앱 실행
interface.launch()
