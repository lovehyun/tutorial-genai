"""
(1단계) HuggingFacePipeline 직접 호출 — 모델에 '평문' 을 그대로 넣는 가장 단순한 방식.
이 예제: chat template 을 적용하지 않고, 프롬프트를 평문 문자열로 모델에 전달한다.

이 방식(HuggingFacePipeline, task="text-generation")이 적합한 모델:
  ▶ base / 완성형(pretrained) 모델 — chat template 이 '아예 없는' 이어쓰기 전용 모델.
    이런 모델은 역할(system/user) 개념이 없어, 이 평문 방식이 사실상 유일한 호출법이다.
      - gpt2                                  (고전, 초경량)
      - microsoft/phi-2                       ~2.7B, base
      - meta-llama/Llama-3.2-1B               ← '-Instruct' 없는 base 버전
      - mistralai/Mistral-7B-v0.1             ~7B, base
  ▶ instruct/chat 모델(아래 Phi-3.5-mini-instruct)도 이 방식으로 '부를 수는' 있지만,
    학습 때 본 chat template 이 적용되지 않아 품질·정지(멈춤)가 불안정할 수 있다.
    → 그 문제를 2_chat_basic.py 의 ChatHuggingFace 가 해결한다. (이 파일은 '발전 전' 모습)

준비:
  pip install langchain-huggingface transformers torch accelerate
  ※ 첫 실행 시 모델 다운로드 (수 GB). GPU 가 있으면 훨씬 빠름.
"""

from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# device_map="auto": GPU 있으면 GPU, 없으면 CPU (accelerate 필요)
llm = HuggingFacePipeline.from_model_id(
    model_id="microsoft/Phi-3.5-mini-instruct",   # 데모용으로 instruct 모델을 '평문' 으로 호출
    task="text-generation",
    device_map="auto",
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

# [관전 포인트] ChatPromptTemplate 을 LLM(HuggingFacePipeline)에 그냥 파이프하면
#   메시지가 '평문' 으로 펼쳐져 들어간다 — chat template(특수토큰)이 적용되지 않는다.
#   실제 모델이 받는 문자열을 직접 찍어 보자.
pv = prompt.invoke({"question": "What is RAG in one paragraph?"})
print("=== 모델이 실제로 받는 입력 (평문 — chat template 미적용) ===")
print(pv.to_string())
print("=" * 60)

chain = prompt | llm | StrOutputParser()
print(chain.invoke({"question": "What is RAG in one paragraph?"}))

# → instruct 모델인데 학습 포맷(<|user|>...<|assistant|>)이 아니라 평문을 받았다.
#   간단한 질문은 그럭저럭 답하지만, system 지시 준수·멈춤이 흔들릴 수 있다.
#   다음 2_chat_basic.py: 같은 모델 + ChatHuggingFace 로 chat template 을 입혀 해결.
