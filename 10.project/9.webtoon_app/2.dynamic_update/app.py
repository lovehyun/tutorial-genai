from flask import Flask, request, render_template, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os
from deep_translator import GoogleTranslator

# .env 파일 로드
load_dotenv('../../.env')

app = Flask(__name__)

# OpenAI 클라이언트 설정
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 전역 이미지 URL 저장 (초기값은 placeholder 이미지)
generated_images = ["/static/placeholder.png"] * 5

# 소설 텍스트를 5개의 짧은 문장으로 요약하는 함수
def summarize_text(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following text into 5 short sentences:\n\n{text}"}
        ],
        max_tokens=300,
        temperature=0.5
    )

    # 응답에서 요약 텍스트 추출 후 문장 단위로 나눔
    summary_text = response.choices[0].message.content.strip()
    summary = summary_text.split('. ')
    return summary[:5]

def translate(text):
    return GoogleTranslator(source='auto', target='en').translate(text)

# GPT로부터 받은 요약 프롬프트를 기반으로 DALL·E 이미지 5장을 생성하는 함수
def generate_images2(prompts):
    global generated_images

    # 공통 스타일(픽사풍) 및 캐릭터 설정 프롬프트
    base_prompt = (
        "Create a series of 5 images in a consistent Pixar style featuring a young male and female in a classic story setting. "
        "The characters should be a young man named John and a young woman named Emily, both in Pixar style. "
        "John is wearing a blue shirt and brown pants, and Emily is wearing a white dress with a blue ribbon. "
        "Ensure all characters and background settings are consistent. Each image should depict a single scene and be in a 1x1 layout."
    )

    # 사용자의 요약 문장을 장면별로 정리
    detailed_prompt = f"{base_prompt} Here are the scenes and a boy is John and a girl is Emily:\n"
    for i, prompt in enumerate(prompts):
        detailed_prompt += f"{i+1}. {prompt}.\n"

    # 디버깅용 프롬프트 출력
    print("DALL·E에 보낼 프롬프트:")
    print(detailed_prompt)

    # DALL·E 2 모델로 5개 이미지 생성 요청
    response = client.images.generate(
        model="dall-e-2",
        prompt=detailed_prompt,
        n=5,
        size="1024x1024"
    )

    # 생성된 이미지 URL 저장
    generated_images = [img.url for img in response.data]

    # 각 이미지 URL 출력 (디버깅용)
    for i, url in enumerate(generated_images, 1):
        print(f"Image {i}: {url}")

def generate_images3(prompts):
    global generated_images

    # 빈 배열로 초기화
    generated_images = ["/static/placeholder.png"] * 5

    for i, prompt in enumerate(prompts):
        if i >= 5:  # 최대 5개 이미지로 제한
            break
            
        translated_prompt = translate(prompt)
        
        # DALL-E 3에 적합한 프롬프트 구성
        full_prompt = (
            f"Create a Pixar style image featuring a young man named John and a young woman named Emily. "
            f"John is wearing a blue shirt and brown pants, and Emily is wearing a white dress with a blue ribbon. "
            f"Scene description: {translated_prompt}"
        )

        print(f"DALL·E-3 프롬프트 {i+1}: {full_prompt}")

        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
                n=1,  # DALL-E 3는 한 번에 하나의 이미지만 생성 가능
                size="1024x1024",
                quality="standard"  # 또는 "hd" → 더 고화질 (유료)
            )

            generated_images[i] = response.data[0].url
            print(f"DALL·E-3 이미지 {i+1}: {generated_images[i]}")
            
        except Exception as e:
            print(f"DALL·E-3 이미지 {i+1} 생성 오류: {e}")
            # 오류 발생 시 이미지는 플레이스홀더 유지

# 메인 페이지 렌더링
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# 텍스트 요약 요청 처리 (JSON 형태로 반환)
@app.route('/summarize', methods=['POST'])
def summarize():
    global generated_images

    # 요청 본문에서 텍스트와 모델 추출
    data = request.json
    text = data.get('text')
    model = data.get('model', 'dall-e-2')  # 기본값으로 dall-e-2 사용
    
    print(f"선택된 모델: {model}")

    # 텍스트 요약
    prompts = summarize_text(text)

    # placeholder로 초기화
    generated_images = ["/static/placeholder.png"] * 5

    # 비동기로 이미지 생성 시작 (선택된 모델에 따라)
    from threading import Thread
    if model == 'dall-e-3':
        Thread(target=generate_images3, args=(prompts,)).start()
    else:  # 기본값은 dall-e-2
        Thread(target=generate_images2, args=(prompts,)).start()

    # 요약된 문장들을 JSON 형태로 반환
    return jsonify({ "prompts": prompts })

# 이미지 URL 목록 요청 처리 (AJAX 폴링용)
@app.route('/update_images', methods=['POST'])
def update_images():
    return jsonify(generated_images)

# 앱 실행
if __name__ == '__main__':
    app.run(debug=True)
