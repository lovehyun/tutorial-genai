# gpt-image 앱 - 1단계: 이미지 생성
# pip install flask openai python-dotenv
#
# OpenAI 이미지 모델(gpt-image-1.5)로 텍스트 → 이미지를 만드는 웹앱.
#
# 이 폴더 묶음(11.gpt_image_app*)은 gpt-image의 3가지 기능을 단계별로 다룬다:
#   1단계 생성  →  2단계 특정 영역만 편집(인페인팅)  →  3단계 주인공 유지 변형

import os
from flask import Flask, request, render_template, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = (request.json.get('prompt') or '').strip()
    if not prompt:
        return jsonify({'error': '프롬프트를 입력하세요.'}), 400

    # [관전 포인트] gpt-image-1.5 이미지 생성
    #   quality 는 low / medium / high / auto 중 선택
    result = client.images.generate(
        model='gpt-image-1.5',
        prompt=prompt,
        size='1024x1024',
        quality='medium',
    )

    # [관전 포인트] dall-e와 달리 응답에 URL이 없다 → b64_json(base64 문자열)로 온다.
    #   base64를 그대로 브라우저로 보내면 <img src="data:image/png;base64,...">로 표시된다.
    return jsonify({'image': result.data[0].b64_json})

if __name__ == '__main__':
    app.run(debug=True)
