"""
(2단계) ChatHuggingFace — 1_instruct_basic 의 '평문' 방식을 chat template 적용으로 발전.
이 예제: 같은 모델(Phi-3.5-mini)을 ChatHuggingFace 로 감싸 올바른 대화 포맷으로 호출.

  핵심 diff (1_instruct_basic 대비): HuggingFacePipeline 을 ChatHuggingFace 로 한 번 더 감쌈.
    → tokenizer.apply_chat_template 로 <|system|>...<|user|>...<|assistant|> 포맷 자동 적용.

이 방식(ChatHuggingFace)이 적합한 모델:
  ▶ chat template 이 '있는' instruct / chat 모델 — system/user/assistant 역할로 학습됨.
    (이름에 -instruct / -chat / -it 가 붙은 것들. 전부 ChatHuggingFace 로 호출하면 됨)
      - microsoft/Phi-3.5-mini-instruct      ~3.8B, 작고 똑똑, 영어 위주        ← 이 예제
      - Qwen/Qwen2.5-1.5B-Instruct           ~1.5B, 더 가벼움, 다국어 (한국어 가능)
      - Qwen/Qwen2.5-3B-Instruct             ~3B,   품질 ↑
      - google/gemma-2-2b-it                 ~2B,   Google (-it = instruction-tuned, HF 로그인 필요)
      - meta-llama/Llama-3.2-1B-Instruct     ~1B,   초경량 (HF 로그인 필요)
      - meta-llama/Llama-2-7b-chat-hf        ~7B,   구형 '-chat' 계열도 동일하게 동작
  ※ 반대로 base/완성형 모델(gpt2, Llama-3.2-1B 등)은 chat template 이 없어 이 방식이 안 맞음
    → 그런 모델은 1_instruct_basic 의 평문 방식으로.

준비:
  pip install langchain-huggingface transformers torch accelerate
  ※ 첫 실행 시 모델 다운로드 (수 GB).  GPU 가 있으면 훨씬 빠름.
"""

from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# HuggingFacePipeline 한 줄로 모델 로드 + 파이프라인 생성
#   device_map="auto" : GPU 가 있으면 GPU, 없으면 CPU 에 자동 배치 (없으면 CPU 라 매우 느림)
#                       ※ accelerate 설치 필요 — pip install accelerate
llm = HuggingFacePipeline.from_model_id(
    model_id="microsoft/Phi-3.5-mini-instruct",
    task="text-generation",
    device_map="auto",
    pipeline_kwargs={
        "max_new_tokens": 256,
        "do_sample": False,         # 결정론적 (temperature 0 효과)
        "return_full_text": False,  # 입력 prompt 는 제외하고 생성된 부분만
    },
)

# [중요] HuggingFacePipeline 을 ChatHuggingFace 로 한 번 더 감싼다.
#   - Phi/Qwen/EXAONE 같은 instruct 모델은 고유 chat template 이 있다
#     (예: <|system|>...<|user|>...<|assistant|>).
#   - HuggingFacePipeline 에 ChatPromptTemplate 을 그냥 파이프하면 "System: ...\nHuman: ..."
#     평문으로 펼쳐져 들어가 template 이 적용되지 않는다 → 답 품질 저하.
#   - ChatHuggingFace 가 tokenizer.apply_chat_template 로 올바른 포맷을 자동 적용한다.
chat = ChatHuggingFace(llm=llm)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Be concise."),
    ("user", "{question}"),
])

chain = prompt | chat | StrOutputParser()

print(chain.invoke({"question": "What is RAG in one paragraph?"}))

# 한국어가 필요하면 Qwen2.5 가 더 좋음:
#   llm = HuggingFacePipeline.from_model_id(model_id="Qwen/Qwen2.5-1.5B-Instruct", ...)
