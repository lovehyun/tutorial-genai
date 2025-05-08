from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path='../../.env')

client = OpenAI()

# 이미지 생성
# 파라미터	     타입	     설명
# model	        str	        사용할 모델 이름입니다. 예: "dall-e-2", "dall-e-3"
# prompt	    str     	생성할 이미지에 대한 설명(프롬프트)입니다. 영어로 상세히 작성할수록 품질이 좋습니다.
# n	            int	        생성할 이미지 수입니다. (DALL·E 3은 항상 1장만 생성 가능, DALL·E 2는 최대 10장까지 가능)
# size	        str	        이미지 크기입니다. "1024x1024", "1024x1792", "1792x1024" 중 선택 (DALL·E 3 기준)
# quality	    str	        "standard" 또는 "hd" 선택 가능 (DALL·E 3). hd는 더 높은 해상도지만 비용이 더 듦
# style	        str	        "vivid" (현실적) 또는 "natural" (자연스러운 톤). dall-e-3에서 사용 가능
# user	        str	        (선택) 사용자 식별용 태그. abuse detection 용도로 사용됨
response = client.images.generate(
    model="dall-e-3",
    prompt="A cute baby sea otter",
    size="1024x1024",
    quality="standard",
    n=1,
)

# 이미지 데이터 추출
image_url = response.data[0].url
print(image_url)

# 이미지를 파일로 저장
# 방법1.
import urllib
urllib.request.urlretrieve(image_url, "DATA/generated_image.png")

# 방법2.
# import requests
# img_data = requests.get(image_url).content
# with open("generated_image.png", "wb") as f:
#     f.write(img_data)
