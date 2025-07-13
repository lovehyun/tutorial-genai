from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

model_name = "mistralai/Mistral-7B-Instruct-v0.3"

# 모델 및 토크나이저 로드 (서버 시작 시 1회)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto")

generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=128,
    temperature=0.5,
    pad_token_id=tokenizer.eos_token_id
)

# Flask 앱 정의
app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt.strip():
        return jsonify({"error": "No prompt provided."}), 400

    output = generator(prompt)[0]["generated_text"]
    return jsonify({"response": output})

# 서버 실행
if __name__ == "__main__":
    app.run(port=5000)
