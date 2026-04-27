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
    if request.method == "POST":
        image_file = request.files["image"]
        if image_file:
            image_bytes = image_file.read()
            # Base64 문자열로 변환
            b64_str = base64.b64encode(image_bytes).decode()
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
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
