from flask import Flask, request, render_template
from openai import OpenAI
from dotenv import load_dotenv
import os
import re

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
    
    content = response.choices[0].message.content.strip()
    summary = re.split(r'\.\s+|\.\n|\.\r\n', content)
    summary = [s.strip() for s in summary if s.strip()]
    
    print("Summary:", summary)
    return summary[:5]

# 시각적 이미지 생성에 맞게 프롬프트 변환
def make_visual_prompts(sentences):
    visual_prompts = []
    for sentence in sentences:
        if sentence.strip():  # 빈 문장 방지
            visual_prompts.append(f"An illustration of: {sentence.strip()}")
            
    print("ImagePrompt: ", visual_prompts)
    return visual_prompts

# 이미지 생성 함수 (DALL-E API 사용)
def generate_image_dalle2(prompt):
    response = client.images.generate(
        model="dall-e-2",
        prompt=prompt,
        n=1,
        size="512x512"
    )
    image_url = response.data[0].url
    print("Generated image URL:", image_url)
    return image_url


def generate_image_dalle3(prompt):
    try:
        response = client.images.generate(
            model="dall-e-3",             # 최신 모델 명시
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard"            # 또는 "hd" (유료 플랜 기준)
        )
        image_url = response.data[0].url
        print("Generated image URL:", image_url)
        return image_url
    except Exception as e:
        print("이미지 생성 실패. 프롬프트:", prompt)
        print("에러 메시지:", repr(e))
        return ""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        
        # 실험1. 요약된 소설로 바로 이미지 생성
        prompts = summarize_text(text)
        images = [generate_image_dalle3(prompt) for prompt in prompts]

        # 실험2. 요약된 소설을 기반으로 이미지 문장으로 변환 후 이미지 생성
        # summaries = summarize_text(text)                                # 1. 텍스트 요약
        # prompts = make_visual_prompts(summaries)                        # 2. 이미지용 문장으로 변환
        # images = [generate_image_dalle3(prompt) for prompt in prompts]  # 3. 이미지 생성
        
        return render_template('index.html', prompts=prompts, images=images)
    return render_template('index.html', prompts=None, images=None)

if __name__ == '__main__':
    app.run(debug=True)
