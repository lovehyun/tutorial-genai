"""
Ollama — 로컬 오픈소스 모델을 LangChain으로 호출하기
# pip install langchain-ollama

이 폴더 3절("오픈소스 LLM 모델 비교")은 지금까지 표로만 다뤘다. 여기서는 실제로 로컬 모델을
LangChain으로 호출해본다 — ChatOpenAI와 인터페이스가 완전히 동일해서, provider만 바꾸면
기존에 만든 프롬프트/체인 코드를 그대로 재사용할 수 있다는 게 핵심이다.

사전 준비:
  1) https://ollama.com 에서 Ollama 설치 (또는 이미 설치돼 있다면 앱 실행 — 로컬 서버가 자동으로 뜬다)
  2) 모델 받기:  ollama pull qwen2.5:7b   (범용 모델, 4.7GB. 더 가벼운 건 qwen2.5:1.5b)
  3) 이 파일 실행 — 별도 API 키 필요 없음, 완전 무료·오프라인 동작
"""

import requests
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

OLLAMA_MODEL = "qwen2.5:7b"


# [관전 포인트 1] 지금 로컬에 어떤 모델이 받아져 있는지 확인 (Ollama REST API, LangChain과 무관)
def list_local_models():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        models = [m["name"] for m in response.json().get("models", [])]
        print(f"로컬에 받아진 모델: {models}")
    except requests.exceptions.ConnectionError:
        print("⚠️  Ollama 서버에 연결할 수 없습니다. Ollama 앱을 실행하거나 `ollama serve`로 서버를 켜세요.")


# [관전 포인트 2] ChatOllama — ChatOpenAI와 완전히 같은 인터페이스(.invoke, |체인 등)
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.7)

prompt = ChatPromptTemplate.from_template("{topic}을 한 문장으로 설명해줘.")
chain = prompt | llm

if __name__ == "__main__":
    list_local_models()

    print(f"\n[모델] Ollama · {OLLAMA_MODEL} (로컬, 무료)")
    result = chain.invoke({"topic": "벡터 데이터베이스"})
    print(f"답변: {result.content}")

    # [비교] 같은 체인 코드로 OpenAI를 썼다면 이렇게만 바뀐다 (인터페이스는 동일):
    #
    #   from langchain_openai import ChatOpenAI
    #   llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    #   chain = prompt | llm   # 프롬프트·체인 조립 코드는 한 글자도 안 바뀜
    #
    # 이 "인터페이스 호환성" 덕분에 11.guardrails/ 예제들은 환경변수 하나(GUARDRAIL_PROVIDER)로
    # OpenAI ↔ Ollama를 전환하며 같은 시나리오를 테스트한다.

    print("\n" + "=" * 60)
    print("[언제 로컬 모델을 쓰나]")
    print("=" * 60)
    print("""
  ✅ 비용 걱정 없이 반복 테스트/실험할 때
  ✅ 민감한 데이터를 외부로 안 보내야 할 때 (완전 오프라인 동작)
  ✅ 정렬(RLHF)이 약한 모델의 동작을 관찰하고 싶을 때
     (예: 11.guardrails/ — 강하게 정렬된 OpenAI 모델은 일부 공격을 스스로 막아버려서
      "가드레일 없는 상태"를 재현하기 어려운데, 로컬 모델은 더 잘 뚫려서 교육용으로 유용하다)
  ❌ 최고 품질의 답변이 필요할 때는 여전히 OpenAI/Anthropic 등 상용 모델이 우세
""")
