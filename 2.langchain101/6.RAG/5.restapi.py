# curl -X POST http://localhost:5000/ask -H "Content-Type: application/json" -d '{"prompt": "What are good fitness tips?"}'
# curl -X POST http://localhost:5000/ask -H "Content-Type: application/json" -d "{\"prompt\": \"What are good fitness tips?\"}"

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

app = Flask(__name__)

# 모델과 토크나이저를 로드하고 파이프라인을 설정합니다.
model_name = "EleutherAI/gpt-neo-2.7B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
text_generation_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_length=150,
    temperature=0.7,
    top_k=50,
    top_p=0.95,
    repetition_penalty=1.2,
    pad_token_id=tokenizer.eos_token_id
)

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    result = text_generation_pipeline(prompt)[0]
    return jsonify({"generated_text": result['generated_text']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
