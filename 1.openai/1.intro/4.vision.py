import openai
from dotenv import load_dotenv
import os
import base64

load_dotenv(dotenv_path='../.env')
openai_api_key = os.getenv('OPENAI_API_KEY')

client = openai.OpenAI(api_key=openai_api_key)

def encode_image_to_base64(image_path):
    """이미지를 base64로 인코딩하여 Data URL 형식으로 반환"""
    with open(image_path, "rb") as image_file:
        base64_bytes = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:image/jpeg;base64,{base64_bytes}"
        # return f"data:image/png;base64,{base64_bytes}"

def analyze_pose_with_image(image_path, question):
    image_base64 = encode_image_to_base64(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",  # vision 지원 모델: gpt-4o 또는 gpt-4-vision-preview
        messages=[
            {
                "role": "system",
                "content": "You are a fitness trainer. Analyze the user's posture and provide constructive feedback."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": question
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_base64
                        }
                    }
                ]
            }
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    image_path = "squats_good.jpg"  # 분석할 운동 자세 이미지
    # image_path = "squats_bad.jpg"  # 분석할 운동 자세 이미지
    # question = "이 운동 자세에 대해서 평가해줘."
    question = "이 운동 자세에서 잘못된 점이나 개선할 부분이 있나요?"
    
    result = analyze_pose_with_image(image_path, question)
    print("\nGPT 자세 분석 결과:")
    print(result)
