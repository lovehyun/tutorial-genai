"""
HuggingFacePipeline — HuggingFace 의 transformers 모델을 LangChain 체인에 끼우기.
이 예제: 가장 작고 빠른 인기 모델로 채팅 시연 (Microsoft Phi-3.5-mini).

자주 쓰는 인기 LLM (HuggingFace, 오픈 액세스):
  - microsoft/Phi-3.5-mini-instruct      ~3.8B, 작고 똑똑, 영어 위주        ← 이 예제
  - Qwen/Qwen2.5-1.5B-Instruct           ~1.5B, 더 가벼움, 다국어 (한국어 가능)
  - Qwen/Qwen2.5-3B-Instruct             ~3B,   품질 ↑
  - google/gemma-2-2b-it                 ~2B,   Google (HF 로그인 필요)
  - meta-llama/Llama-3.2-1B-Instruct     ~1B,   초경량 (HF 로그인 필요)

준비:
  pip install langchain-huggingface transformers torch accelerate
  ※ 첫 실행 시 모델 다운로드 (수 GB).  GPU 가 있으면 훨씬 빠름.
"""

from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# HuggingFacePipeline 한 줄로 모델 로드 + 파이프라인 생성
llm = HuggingFacePipeline.from_model_id(
    model_id="microsoft/Phi-3.5-mini-instruct",
    task="text-generation",
    pipeline_kwargs={
        "max_new_tokens": 256,
        "do_sample": False,         # 결정론적 (temperature 0 효과)
        "return_full_text": False,  # 입력 prompt 는 제외하고 생성된 부분만
    },
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Be concise."),
    ("user", "{question}"),
])

chain = prompt | llm | StrOutputParser()

print(chain.invoke({"question": "What is RAG in one paragraph?"}))

# 한국어가 필요하면 Qwen2.5 가 더 좋음:
#   llm = HuggingFacePipeline.from_model_id(model_id="Qwen/Qwen2.5-1.5B-Instruct", ...)
