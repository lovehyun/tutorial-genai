# REST API를 직접 호출
# Ollama는 기본적으로 localhost:11434에서 REST API 서버를 실행합니다.
# ollama list
# ollama pull llama3  - 모델을 미리 다운로드만 하고 싶을 때 사용. REST API로 호출할 준비만 하기.
# ollama run llama3   - 모델이 없다면 자동으로 다운로드(pull) 후 실행. 모델이 있다면 즉시 실행(인터랙티브 모드)합니다.

import requests
import json

response = requests.post(
    "http://localhost:11434/api/generate", 
    json={
        "model": "llama3",
        "prompt": "What is the capital of France?"
    },
    stream=True
)
# stream=False일 경우 전체 응답이 한 번에 오고, JSON 하나로 끝납니다.
# stream=True일 경우 단어 단위로 조각조각 스트리밍됩니다. 이를 SSE (Server-Sent Events)처럼 활용 가능.

# iter_lines()로 스트리밍 형식의 응답을 받을 수 있습니다.
# for chunk in response.iter_lines():
#     if chunk:
#         print(chunk.decode())

for line in response.iter_lines():
    if line:
        data = json.loads(line.decode('utf-8'))
        print(data.get("response", ""), end="", flush=True)
