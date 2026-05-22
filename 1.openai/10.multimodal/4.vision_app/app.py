# 이미지 분석(Vision) 앱 - 1단계: 기본 — 이미지 업로드 → GPT-4o 설명
# pip install flask openai python-dotenv
#
# 이 폴더(4.vision_app*)는 '이미지를 생성'하는 게 아니라,
# 업로드한 이미지를 GPT-4o가 보고 '설명·분석'하는 Vision 앱이다.
#
# 1단계: 가장 단순한 형태 — HTML 폼으로 이미지를 올리면 결과를 같은 페이지에 표시한다.

import os, base64
import openai
from flask import Flask, request, render_template
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    # [관전 포인트] 같은 '/' 라우트가 GET(폼 보여주기)과 POST(이미지 처리)를 모두 맡는다
    if request.method == "POST":
        image_file = request.files["image"]
        if image_file:
            image_bytes = image_file.read()
            # [관전 포인트] 업로드 이미지를 base64 Data URL로 변환해야 GPT에 보낼 수 있다
            b64_str = base64.b64encode(image_bytes).decode()
            # [관전 포인트] Vision 호출 — content를 리스트로: 텍스트 + 이미지를 함께 전달
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "이 이미지를 설명해줘"},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{b64_str}"}
                            },
                        ],
                    }
                ],
                max_tokens=300
            )
            result = response.choices[0].message.content
    # 결과를 템플릿에 넘겨 같은 페이지에 표시
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
