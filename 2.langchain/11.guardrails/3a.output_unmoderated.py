"""
3a — 출력 검증 없음 (모델 답변을 검사 없이 그대로 노출)
# pip install langchain-ollama   (GUARDRAIL_PROVIDER=ollama 로 로컬 모델을 쓸 때만 필요)

1a/1b, 2a/2b는 '입력'을 막았다. 하지만 입력이 멀쩡해도 모델이 스스로 부적절한 답을
만들어낼 수 있다(예: 의료 자문을 단정적으로 처방). 여기서는 그걸 그대로 사용자에게 보여준다.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

PROVIDER = os.getenv("GUARDRAIL_PROVIDER", "openai")
OLLAMA_MODEL = os.getenv("GUARDRAIL_OLLAMA_MODEL", "qwen2.5:7b")

if PROVIDER == "ollama":
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.7)
    print(f"[모델] Ollama · {OLLAMA_MODEL} (로컬)\n")
else:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    print("[모델] OpenAI · gpt-4o-mini\n")

RISKY_QUESTION = "제가 두통이 심한데 무슨 약을 먹어야 할지 정확히 처방해줘"


def ask_unmoderated(user_input: str) -> str:
    # [문제] 모델이 만든 답을 검사 없이 그대로 반환한다.
    return llm.invoke(user_input).content


if __name__ == "__main__":
    print("=== 3a: 출력 검증 없음 ===")
    print(f"질문: {RISKY_QUESTION}\n")

    answer = ask_unmoderated(RISKY_QUESTION)
    print(f"사용자에게 그대로 노출되는 답변:\n{answer}")

    print("\n👉 의료 자문을 단정적으로 하고 있는지 확인할 것.")
    print("   3b.output_moderated.py 에서 같은 질문이 어떻게 걸러지는지 비교.")
