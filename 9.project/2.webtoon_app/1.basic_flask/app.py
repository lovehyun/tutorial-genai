from flask import Flask, request, render_template
from openai import OpenAI
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv('../../.env')

app = Flask(__name__)

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 소설 내용을 요약하는 함수 (최신 OpenAI SDK 사용)
def summarize_text(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following text into 5 short sentences:\n\n{text}"}
        ],
        max_tokens=300,
        temperature=0.5,
    )
    summary = response.choices[0].message.content.strip().split('. ')
    print("Summary:", summary)
    return summary[:5]

# 이미지 생성 함수 (DALL-E 최신 API 사용)
def generate_image(prompt):
    response = client.images.generate(
        model="dall-e-3",             # 최신 모델 명시 (또는 dall-e-2)
        prompt=prompt,
        n=1,
        size="1024x1024",
        quality="standard"            # 또는 "hd" (유료 플랜 기준)
    )
    image_url = response.data[0].url
    print("Generated image URL:", image_url)
    return image_url

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        prompts = summarize_text(text)
        images = [generate_image(prompt) for prompt in prompts]
        return render_template('index.html', prompts=prompts, images=images)
    return render_template('index.html', prompts=None, images=None)

if __name__ == '__main__':
    app.run(debug=True)
