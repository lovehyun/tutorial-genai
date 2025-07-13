# 개념 설계 (End-to-End 데이터 파이프)
# ┌──────────────┐   mic stream   ┌──────────────┐   (≈ 300 ms)   ┌────────────┐
# │  브라우저    │ ─────────────▶ │  실시간 ASR  │ ─────────────▶ │   GPT-4o   │
# │  (Web)       │   WebRTC /     │  (Whisper RT │   텍스트        │  (Vision)  │
# │              │   WebSocket    │   또는 Realtime│                │            │
# │              │ ◀───────────── │  API)        │ ◀───────────── │            │
# │              │   TTS stream   │              │   응답 텍스트   │            │
# └──────────────┘                └──────────────┘                └────────────┘
#          ▲                                                               │
#          └────────────────────────  TTS 오디오 스트림  ───────────────────┘
#
# 구간	기술 후보	지연 목표
# Mic → ASR	WebRTC + Opus 스트림 → Whisper-Streaming(로컬) 또는 OpenAI Realtime API	200–400 ms
# ASR → GPT	chat.completions 스트리밍, image context 포함	200–500 ms
# GPT → TTS	OpenAI TTS 스트리밍 엔드포인트 (chunked)	200–400 ms
# TTS → Browser	WebSocket → MediaSource / WebAudio	50 ms
#
# OpenAI Realtime API(음성 in ⇆ 음성 out 스트리밍) 가용 시 가장 간단합니다.
# 현재 공개 베타로, Whisper-Turbo 기반 초저지연 STT + TTS 통합을 제공합니다.
# GPT-4o Vision은 같은 세션에서 이미지를 반복 전달하지 않아도 일관성을 유지하지만,
# 완전한 컨텍스트 보장을 위해 2-3턴마다 이미지 블록을 재주입하는 것이 안전합니다.

# Quart 기반 비동기 웹 서버 구현 (Flask는 WebSocket 비동기 처리에 부적합)

# 설치 필요:
# pip install quart quart-cors openai aiohttp python-dotenv

import os
import base64
import openai
import asyncio
import aiohttp
from quart import Quart, render_template, request, websocket
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Quart(__name__)

# 전역 이미지 컨텍스트 저장 (최신 이미지 1장)
image_ctx_url = None

# ===============================
# (1) 메인 페이지 라우트
# ===============================
@app.route("/")
async def index():
    return await render_template("index.html")

# ===============================
# (2) 이미지 업로드 → Base64 URL로 저장
# ===============================
@app.route("/upload_img", methods=["POST"])
async def upload_img():
    global image_ctx_url
    form = await request.files
    file = form.get("image")
    mime = file.mimetype or "image/jpeg"
    b64 = base64.b64encode(await file.read()).decode()
    image_ctx_url = f"data:{mime};base64,{b64}"
    return "ok"

# ===============================
# (3) 텍스트 + 이미지 → GPT-4o Vision 질의
# ===============================
@app.route("/ask", methods=["POST"])
async def ask():
    form = await request.form
    files = await request.files
    question = form.get("question", "").strip()
    file = files.get("image")

    if not question or not file:
        return {"answer": "질문과 이미지를 모두 입력해 주세요."}, 400

    mime = file.mimetype or "image/jpeg"
    b64 = base64.b64encode(await file.read()).decode()
    image_url = f"data:{mime};base64,{b64}"

    # GPT Vision API 호출
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": question},
            {"role": "user", "content": [
                {"type": "text", "text": "위 질문은 이 이미지와 관련 있습니다."},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]}
        ],
        max_tokens=500
    )

    return {"answer": response.choices[0].message.content}

# ===============================
# (4) 실시간 음성 ↔ GPT-4o Realtime 통신
# ===============================
@app.websocket("/voice")
async def voice():
    if not image_ctx_url:
        await websocket.send(b"")  # 이미지 없으면 종료
        return

    url = "wss://api.openai.com/v1/audio/chat"
    headers = {"Authorization": f"Bearer {openai.api_key}"}

    async with aiohttp.ClientSession(headers=headers) as sess:
        async with sess.ws_connect(url) as oa_ws:

            # 시스템 메시지 + 이미지 context 전달
            await oa_ws.send_json({
                "type": "system",
                "content": [
                    {"type": "text", "text": "이 이미지를 계속 참고해 대화하세요."},
                    {"type": "image_url", "image_url": {"url": image_ctx_url}}
                ]
            })

            async def pipe():
                async def client_to_openai():
                    async for msg in websocket:
                        await oa_ws.send_bytes(msg)

                async def openai_to_client():
                    async for msg in oa_ws:
                        if msg.type == aiohttp.WSMsgType.BINARY:
                            await websocket.send(msg.data)
                        elif msg.type == aiohttp.WSMsgType.TEXT:
                            print("GPT partial:", msg.data)

                await asyncio.gather(client_to_openai(), openai_to_client())

            await pipe()

# ===============================
# (5) 서버 실행 (개발용 CLI 권장)
# ===============================
# 아래 명령어로 실행하세요:
# quart --app app run --reload

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=5000)

# 직접 python app.py로 실행하는 방식은 비동기 서버 구조상 권장되지 않습니다
