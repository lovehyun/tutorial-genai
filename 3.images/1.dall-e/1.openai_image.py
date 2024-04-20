from dotenv import load_dotenv
from openai import OpenAI
import urllib

load_dotenv(dotenv_path='../.env')

client = OpenAI()

# 이미지 생성
response = client.images.generate(
    model="dall-e-3",
    prompt="A cute baby sea otter",
    n=1,
    size="1024x1024"
)

# 이미지 데이터 추출
image_url = response.data[0].url
print(image_url)

# 이미지를 파일로 저장
urllib.request.urlretrieve(image_url, "DATA/generated_image.png")
