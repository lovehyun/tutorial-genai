from flask import Flask, request, render_template
import openai
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv('../.env')

app = Flask(__name__)

# OpenAI 클라이언트 설정
openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai.Client(api_key=openai.api_key)

# 소설 내용을 요약하는 함수
def summarize_text(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following text into 5 short sentences:\n\n{text}"}
        ],
        max_tokens=150,
        temperature=0.5,
    )
    summary = response.choices[0].message.content.strip().split('. ')
    print("Summary:", summary)  # 요약된 결과 출력

    return summary[:5]

# DALL-E API 호출 함수
def generate_image(prompt):
    response = client.images.generate(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    print(response)
    image_url = response.data[0].url
    print("Generated image URL:", image_url)  # 생성된 이미지 URL 출력

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
