# curl -X POST http://localhost:5000/generate -H "Content-Type: application/json" -d '{"prompt":"Tell me a funny story about a robot."}'
# curl -X POST http://localhost:5000/generate -H "Content-Type: application/json" -d "{\"prompt\":\"Tell me a funny story about a robot.\"}"

from flask import Flask, request, jsonify

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

# Flask 앱 초기화
app = Flask(__name__)

# 모델 및 파이프라인 초기화 (서버 시작 시 1회만 실행됨)
model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=128,
    temperature=0.7,
    pad_token_id=tokenizer.eos_token_id
)

llm = HuggingFacePipeline(pipeline=generator)

# LangChain 프롬프트 템플릿 및 체인 구성
prompt_template = PromptTemplate(
    input_variables=["prompt"],
    template="{prompt}"
)

qa_chain = prompt_template | llm | RunnableLambda(lambda x: {"response": x})

# 엔드포인트 정의
@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    result = qa_chain.invoke({"prompt": prompt})
    return jsonify({"response": result["response"]})

# 서버 실행
if __name__ == "__main__":
    app.run(port=5000)
