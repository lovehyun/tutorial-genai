# pip install openai python-dotenv
#
# 드롭인 호환의 핵심 증명 — 함수는 하나, `client`만 바꿔치기해서 실제 OpenAI와 로컬 Ollama 양쪽에
# 같은 질문을 던진다. base_url/api_key/model 세 줄 말고는 코드가 한 글자도 다르지 않다.
#
# 실전에서 이 패턴이 쓰이는 이유: 개발 중엔 무료·오프라인인 로컬 모델로 반복 테스트하다가,
# 배포할 때만 진짜 OpenAI로 바꾸는 식으로 비용을 아낄 수 있다(또는 그 반대 — 민감한 데이터는
# 로컬로, 고품질 답변이 필요할 때만 OpenAI로).

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

question = "MCP가 뭔지 한 문장으로 설명해줘."


def ask(client: OpenAI, model: str, label: str) -> None:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": question}],
    )
    print(f"[{label}] {response.choices[0].message.content}")


# [관전 포인트] 이 아래 두 client 정의 말고는 코드가 완전히 동일하다 — ask() 함수는
# "OpenAI인지 Ollama인지" 전혀 모른 채로 똑같이 호출한다.
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ollama_client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

print(f"질문: {question}\n")
ask(openai_client, "gpt-4o-mini", "OpenAI")
ask(ollama_client, "qwen2.5:7b", "Ollama(로컬)")

# 실행 결과 (실측):
#   [OpenAI]      MCP는 'Microsoft Certified Professional'의 약자로, 마이크로소프트의
#                 기술 관련 인증 프로그램을 통해 전문성을 인증받은 IT 전문가를 의미합니다.
#   [Ollama(로컬)] MCP는 마이크로소프트 공인 전문가(Microsoft Certified Professional)를 의미합니다.
#
# ⚠️ 둘 다 틀렸다(여기선 Model Context Protocol을 물어본 거였는데) — 그것도 흥미로운 지점이다.
#   "MCP"처럼 맥락 없이 애매한 약어는 OpenAI든 로컬 모델이든 똑같이 잘못 짚을 수 있다.
#   API 형태가 호환된다는 게 "같은 지식을 갖고 있다"는 뜻은 아니라는 걸 직접 확인한 것 —
#   질문에 "5.mcp 저장소의 그 MCP" 처럼 맥락을 붙이면 결과가 달라질 수 있다(직접 시도해볼 것).
