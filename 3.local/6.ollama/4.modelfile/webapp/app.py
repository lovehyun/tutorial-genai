"""
gemma4-korean 대화 백엔드 (Flask + Ollama SDK 스트리밍)

핵심: gemma4 는 '진짜 reasoning 모델' 이라 추론을 '네이티브 thinking 채널' 로 따로 낸다.
  - message.thinking  → 모델의 추론  → '생각' 컬럼
  - message.content   → 최종 답변     → '답변' 컬럼
두 갈래를 모델 스스로 구조적으로 분리해주므로, <think>/<answer> 같은 '텍스트 태그'를
직접 파싱할 필요가 없다. (텍스트 태그 방식은 모델이 태그를 본문에서 '언급'만 해도
오인식되어 깨진다 — 그래서 여기선 네이티브 채널만 사용한다.)

견고함을 위해 두 가지를 더 한다:
  1) think=True 로 추론을 thinking 채널에 '강제' → content 에 추론이 새지 않음
  2) '태그를 쓰라'는 지시가 없는 깨끗한 system 을 넘김
     (런타임 system 은 Modelfile 의 SYSTEM 을 덮어써서 content 가 태그 없이 깔끔해짐)

준비: pip install flask ollama   +   ollama create gemma4-korean -f ../Modelfile.reasoning
실행: python app.py   →   http://localhost:5000
"""
import json
import ollama
from flask import Flask, request, Response, send_from_directory, stream_with_context

MODEL = "gemma4-korean"
SYSTEM = (
    "당신은 한국어 AI 비서입니다. "
    "질문이 어떤 언어로 들어오든 반드시 한국어 존댓말로만 답변하세요. "
    "기술 질문은 예제를 포함해 단계별로 설명하세요."
)

app = Flask(__name__, static_folder="static", static_url_path="")


def stream_chat(question):
    def emit(col, text):
        return json.dumps({"col": col, "text": text}, ensure_ascii=False) + "\n"

    for chunk in ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question},
        ],
        think=True,    # 추론을 thinking 채널로 '강제' → content(답변)에 추론이 새지 않음
        stream=True,
    ):
        msg = chunk.get("message", {})
        thinking = msg.get("thinking")   # 네이티브 추론 → 생각
        if thinking:
            yield emit("think", thinking)
        content = msg.get("content")     # 최종 답변 → 답변
        if content:
            yield emit("answer", content)
    yield emit("done", "")


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.post("/chat")
def chat():
    question = (request.json or {}).get("question", "").strip()
    if not question:
        return {"error": "질문이 비어 있습니다."}, 400
    return Response(
        stream_with_context(stream_chat(question)),
        mimetype="application/x-ndjson",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )


if __name__ == "__main__":
    app.run(port=5000, threaded=True)
