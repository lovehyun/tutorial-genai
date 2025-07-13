# pip install transformers protobuf sentencepiece torch

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

model_name = "mistralai/Mistral-7B-Instruct-v0.3"

# 모델 및 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto")

# 파이프라인 설정
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=128,
    temperature=0.5,
    pad_token_id=tokenizer.eos_token_id
)

# LangChain에 연결
llm = HuggingFacePipeline(pipeline=generator)

# 프롬프트 템플릿 설정
prompt_template = PromptTemplate(
    input_variables=["prompt"],
    template="{prompt}"
)

qa_chain = prompt_template | llm | RunnableLambda(lambda x: {"response": x})

# 테스트
def answer_question(prompt):
    result = qa_chain.invoke({"prompt": prompt})
    return result["response"]

# 실행
if __name__ == "__main__":
    prompt = "What are good fitness tips?"
    print("Prompt:", prompt)
    print("Answer:", answer_question(prompt))
