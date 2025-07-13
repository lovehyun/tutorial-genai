# curl -X POST http://localhost:5000/generate -H "Content-Type: application/json" -d '{"prompt": "What are good fitness tips?"}'
# curl -X POST http://localhost:5000/generate -H "Content-Type: application/json" -d "{\"prompt\": \"What are good fitness tips?\"}"

# pip install fastapi uvicorn

from fastapi import FastAPI, Request
import uvicorn
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

app = FastAPI()

@app.post("/generate")
async def generate(request: Request):
    data = await request.json()
    prompt = data["prompt"]
    output = generator(prompt)[0]["generated_text"]
    return {"response": output}

if __name__ == "__main__":
    # uvicorn.run("server:app", port=5000, reload=True)
    uvicorn.run(app, host="127.0.0.1", port=5000)
