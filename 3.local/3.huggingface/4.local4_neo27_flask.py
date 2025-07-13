# curl -X POST http://localhost:5000/generate -H "Content-Type: application/json" -d '{"prompt": "What are good fitness tips?"}'
# curl -X POST http://localhost:5000/generate -H "Content-Type: application/json" -d "{\"prompt\": \"What are good fitness tips?\"}"

from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# 모델 초기화 (서버 시작 시 1회만 실행)
model_name = "EleutherAI/gpt-neo-2.7B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")

generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=128,
    temperature=0.7,
    pad_token_id=tokenizer.eos_token_id
)

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate():
    user_input = request.json.get("prompt", "")
    output = generator(user_input)[0]["generated_text"]
    return jsonify({"response": output})

if __name__ == "__main__":
    app.run(port=5000)
