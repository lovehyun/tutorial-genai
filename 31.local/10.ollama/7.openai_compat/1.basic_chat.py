# pip install openai
#
# Ollama는 자체 API(1.restapi, 2.sdk) 말고도 **OpenAI와 똑같은 REST 형태**(`/v1/chat/completions`)
# 를 흉내내는 엔드포인트를 함께 띄운다 — 그래서 `openai` 파이썬 패키지를 그대로 쓰되
# base_url만 로컬로 돌리면, `1.openai/1.restapi`·`1.openai/2.sdk`에서 쓰던 코드가 거의 그대로
# 로컬 모델에 붙는다. "API 키가 있으면 OpenAI, 없으면 로컬"처럼 실전에서 자주 쓰는 패턴이다.

from openai import OpenAI

# [관전 포인트] base_url만 로컬 Ollama 서버로 바꾼다. api_key는 검사하지 않지만
# openai 라이브러리가 값을 요구하므로 아무 문자열이나 넣는다("ollama"는 관례적인 더미 값).
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

response = client.chat.completions.create(
    model="qwen2.5:7b",  # ollama pull qwen2.5:7b 로 미리 받아둔 모델
    messages=[{"role": "user", "content": "5 더하기 3은?"}],
)

print(response.choices[0].message.content)

# 실행 결과 (실측): "5 더하기 3은 8입니다."
# → 실제 OpenAI API를 호출한 게 아니라 로컬 Ollama 서버가 응답했다 — 코드는 1.openai 예제와
#   똑같은 openai 라이브러리를 쓰지만, 요청은 인터넷 밖으로 한 번도 안 나갔다.
