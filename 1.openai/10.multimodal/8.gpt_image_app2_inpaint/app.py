# gpt-image-1 앱 - 2단계: 특정 영역만 편집 (인페인팅)
# pip install flask openai pillow python-dotenv
#
# 1단계(생성) 대비 새로 추가된 것:
#   생성한 이미지 위에서 '편집할 사각형 영역'을 드래그로 고르면,
#   그 영역만 프롬프트대로 다시 그린다 (images.edit + 마스크).
#
# 인페인팅의 핵심은 '마스크'다 — 아래 /edit 의 관전 포인트 참고.

import os
import io
import base64
from flask import Flask, request, render_template, jsonify
from openai import OpenAI
from PIL import Image, ImageDraw
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# 1단계와 동일 — 편집할 원본 이미지를 만들기 위해 생성 기능을 그대로 둔다
@app.route('/generate', methods=['POST'])
def generate():
    prompt = (request.json.get('prompt') or '').strip()
    if not prompt:
        return jsonify({'error': '프롬프트를 입력하세요.'}), 400
    result = client.images.generate(
        model='gpt-image-1', prompt=prompt, size='1024x1024', quality='medium',
    )
    return jsonify({'image': result.data[0].b64_json})

@app.route('/edit', methods=['POST'])
def edit():
    data = request.json
    image_b64 = data.get('image')
    prompt = (data.get('prompt') or '').strip()
    rect = data.get('rect')   # {x, y, w, h} — 0~1 비율 (캔버스 크기와 무관)
    if not image_b64 or not prompt or not rect:
        return jsonify({'error': '이미지·프롬프트·영역이 모두 필요합니다.'}), 400

    # 현재 이미지를 디코딩
    image = Image.open(io.BytesIO(base64.b64decode(image_b64))).convert('RGBA')
    W, H = image.size

    # [관전 포인트] 인페인팅 마스크 만들기 (gpt-image-1 규칙)
    #   마스크는 원본과 같은 크기의 RGBA 이미지.
    #   '투명한(alpha=0)' 픽셀 = 편집 대상,  불투명한 픽셀 = 그대로 유지.
    mask = Image.new('RGBA', (W, H), (0, 0, 0, 255))   # 전체 불투명 → 전부 유지
    x0, y0 = int(rect['x'] * W), int(rect['y'] * H)
    x1, y1 = int((rect['x'] + rect['w']) * W), int((rect['y'] + rect['h']) * H)
    ImageDraw.Draw(mask).rectangle([x0, y0, x1, y1], fill=(0, 0, 0, 0))  # 선택 영역만 투명 → 편집

    # PIL 이미지를 '파일처럼' 전달하기 위해 메모리 버퍼(BytesIO)로 변환한다
    img_buf = io.BytesIO(); image.save(img_buf, 'PNG'); img_buf.name = 'image.png'; img_buf.seek(0)
    mask_buf = io.BytesIO(); mask.save(mask_buf, 'PNG'); mask_buf.name = 'mask.png'; mask_buf.seek(0)

    # [관전 포인트] images.edit + mask → 마스크의 '투명 영역'만 prompt대로 재생성된다
    result = client.images.edit(
        model='gpt-image-1',
        image=img_buf,
        mask=mask_buf,
        prompt=prompt,
        size='1024x1024',
    )
    return jsonify({'image': result.data[0].b64_json})

if __name__ == '__main__':
    app.run(debug=True)
