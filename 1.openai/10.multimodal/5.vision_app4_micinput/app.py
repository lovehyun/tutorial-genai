# 이미지 분석(Vision) 앱 - 4단계: 마이크 음성 입력 + 백엔드 견고화
# pip install flask openai python-dotenv
#
# 3단계 대비 새로 추가된 것:
#   - 백엔드: 업로드 크기 제한 + 공통 에러 핸들러로 견고해진다.
#   - 모델을 gpt-4o-mini로 (비용 절감), temperature 지정.
#   - 음성으로 질문 입력(브라우저 SpeechRecognition)은 프론트엔드(static/)에 있다.

import os, base64
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
# [관전 포인트] 업로드 용량 상한 — 너무 큰 파일은 받기 전에 차단한다
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

# [관전 포인트] 공통 에러 핸들러 — 모든 예외를 일관된 JSON 형식으로 반환한다
@app.errorhandler(Exception)
def handle_error(e):
    code = getattr(e, "code", 500)
    return jsonify({"success": False, "error": str(e)}), code

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    question = request.form.get("question", "").strip()
    img = request.files.get("image")

    if not question or not img:
        return jsonify({"error":"질문과 이미지를 모두 보내야 합니다."}), 400

    mime = img.mimetype or "image/jpeg"
    b64 = base64.b64encode(img.read()).decode()
    img.seek(0)  # 파일 포인터 맨 앞으로 이동 (img 를 이후에 또 사용한다면, 포인터 이동 안하면 현재는 끝에 있어서 0바이트 반납됨.)

    data_url = f"data:{mime};base64,{b64}"  # 또는 S3 에 업로드 이후 해당 링크 전달 (가장 효율적)

    resp = openai.chat.completions.create(
        model="gpt-4o-mini", # 비용 최적화 (gpt-4o 대비)
        messages=[
            {"role":"user","content":question},
            {"role":"user","content":[
                {"type":"text","text":"위 질문을 이 이미지로 답해줘"},
                {"type":"image_url","image_url":{"url":data_url}}
            ]}
        ],
        max_tokens=400,
        temperature=0.4
    )

    return jsonify({"success": True,
                    "answer": resp.choices[0].message.content})

if __name__=="__main__":
    app.run(debug=True)
