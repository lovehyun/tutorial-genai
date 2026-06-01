import os
import base64
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 1. 환경 변수 로드
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# 2. 이미지 base64로 인코딩
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded}"
        # return f"data:image/png;base64,{encoded}"

image_path = "squats.jpg"  # 운동 자세 이미지 경로
image_base64_url = encode_image_to_base64(image_path)

# 3. 프롬프트 템플릿 정의 (LangChain ChatPromptTemplate)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a professional fitness coach. Analyze the user's posture and give advice."),
    ("human", [
        {"type": "text", "text": "Please evaluate my exercise posture and provide feedback."},
        {"type": "image_url", "image_url": {"url": image_base64_url}}
    ])
])

# 4. LLM 설정 (GPT-4o or gpt-4-vision-preview)
llm = ChatOpenAI(model="gpt-4o", temperature=0.7, max_tokens=1000)

# 5. 후처리 파서
parser = StrOutputParser()

# 6. 메시지 생성
messages = prompt.format_messages()

# 7. LLM 호출
response = llm.invoke(messages)

# 8. 후처리
cleaned_output = parser.invoke(response)

# 9. 출력
print("\n자세 분석 결과:")
print(cleaned_output)
