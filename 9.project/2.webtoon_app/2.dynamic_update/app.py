from flask import Flask, request, render_template, jsonify
import openai
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv('../.env')

app = Flask(__name__)

# OpenAI 클라이언트 설정
openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai.Client(api_key=openai.api_key)

# 전역 변수로 이미지 URL 저장
generated_images = ["/static/placeholder.png"] * 5

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
    return summary[:5]

# DALL-E API 호출 함수
def generate_images(prompts):
    base_prompt = (
        "Create a series of 5 images in a consistent Pixar style featuring a young male and female in a classic story setting. "
        "The characters should be a young man named John and a young woman named Emily, both in Pixar style. "
        "John is wearing a blue shirt and brown pants, and Emily is wearing a white dress with a blue ribbon. "
        "Ensure all characters and background settings are consistent. Each image should depict a single scene and be in a 1x1 layout."
    )

    # 사용자 제공 프롬프트를 결합하고, 'a boy'와 'a girl'을 각각 John과 Emily로 설명
    detailed_prompt = f"{base_prompt} Here are the scenes and a boy is John and a girl is Emily: "
    for i, prompt in enumerate(prompts):
        detailed_prompt += f"{i+1}. {prompt}.\n"
 
    # 프롬프트 출력 (디버깅용)
    print("Detailed Prompt for Image Generation:")
    print(detailed_prompt)

    response = client.images.generate(
        model="dall-e-2",  # 멀티 이미지 생성을 위해서 dall-e-2 사용
        prompt=detailed_prompt,
        n=5,
        size="1024x1024"
    )
    
    for i in range(5):
        generated_images[i] = response.data[i].url
        # generated_images[i] = "/static/imageresult.jpg"

        # 생성된 이미지 URL 출력 (디버깅용)
        print(f"Generated image URL {i+1}: {generated_images[i]}")

@app.route('/', methods=['GET', 'POST'])
def index():
    global generated_images

    if request.method == 'POST':
        text = request.form['text']
        prompts = summarize_text(text)

        # 요약된 프롬프트 출력 (디버깅용)
        print("Summarized Prompts:")
        for i, prompt in enumerate(prompts):
            print(f"Prompt {i+1}: {prompt}")

        # Placeholder 이미지로 초기화
        generated_images = ["/static/placeholder.png"] * 5

        # 이미지 생성
        generate_images(prompts)

        return render_template('index.html', prompts=prompts, images=generated_images)
    return render_template('index.html', prompts=None, images=None)

@app.route('/update_images', methods=['POST'])
def update_images():
    return jsonify(generated_images)

if __name__ == '__main__':
    app.run(debug=True)
