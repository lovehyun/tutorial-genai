# gpt-image 앱 - 3단계: 주인공을 유지한 채 변형 (일관성)
# pip install flask openai pillow python-dotenv
#
# 2단계(영역 편집) 대비 새로 추가된 것:
#   기준 이미지(주인공/캐릭터)를 '참고'로 넣고 새 프롬프트를 주면,
#   gpt-image가 같은 피사체를 유지한 채 새 장면을 만든다.
#
# 2단계와의 핵심 차이는 '마스크의 유무'다:
#   - 마스크 O (2단계) → 한 이미지의 '특정 영역'만 수정 (인페인팅)
#   - 마스크 X (3단계) → 입력 이미지를 '시각적 참고'로 삼아 전체를 새로 생성

import os
import io
from flask import Flask, request, render_template, jsonify
from openai import OpenAI
from PIL import Image
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transform', methods=['POST'])
def transform():
    ref = request.files.get('reference')
    prompt = request.form.get('prompt', '').strip()
    if not ref or not prompt:
        return jsonify({'error': '기준 이미지와 프롬프트가 모두 필요합니다.'}), 400

    # 업로드 이미지를 PNG로 정규화해 메모리 버퍼에 담는다
    image = Image.open(ref).convert('RGBA')
    buf = io.BytesIO()
    image.save(buf, 'PNG')
    buf.name = 'reference.png'
    buf.seek(0)

    # [관전 포인트] 마스크 '없이' images.edit 호출
    #   gpt-image는 입력 이미지를 시각적 참고로 삼아,
    #   같은 피사체/스타일을 유지하면서 prompt가 묘사한 새 장면을 만든다.
    #   (참고 이미지를 여러 장 넣으면 image=[buf1, buf2, ...] 일관성이 더 좋아진다)
    result = client.images.edit(
        model='gpt-image-1.5',
        image=buf,
        prompt=prompt,
        size='1024x1024',
    )
    return jsonify({'image': result.data[0].b64_json})

if __name__ == '__main__':
    app.run(debug=True)
