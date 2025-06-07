from flask import Flask, request, render_template
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
import os
from openai import OpenAI  # 이미지 생성을 위해 사용

# .env 파일 로드
load_dotenv("../../.env")

app = Flask(__name__)

# LangChain LLM 초기화 (GPT 모델)
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.5
)

# OpenAI 이미지 생성 클라이언트 (dall-e 전용)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 요약 함수 (LangChain 프롬프트 체인 사용)
def summarize_text(text):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="Summarize the following text into 5 short sentences:\n\n{text}")
    ])

    chain = prompt | llm

    # 입력값을 dictionary로 전달
    response = chain.invoke({"text": text})
    summary = response.content.strip().split('. ')
    print("Summary:", summary)
    return summary[:5]

# 이미지 생성 함수 (OpenAI SDK 사용)
def generate_image(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024",
        quality="standard"
    )
    image_url = response.data[0].url
    print("Generated image URL:", image_url)
    return image_url

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form["text"]
        prompts = summarize_text(text)
        images = [generate_image(prompt) for prompt in prompts]
        return render_template("index.html", prompts=prompts, images=images)
    return render_template("index.html", prompts=None, images=None)

if __name__ == "__main__":
    app.run(debug=True)
