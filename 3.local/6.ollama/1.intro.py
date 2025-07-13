# Ollama는 로컬에서 대형 언어 모델(LLM) 을 쉽게 실행할 수 있게 해주는 오픈소스 툴입니다.
# 특히 Mac, Linux, Windows에서 GPU 또는 CPU로 실행할 수 있도록 지원하며, llama.cpp 기반으로 작동합니다.
# Ollama는 다양한 llama.cpp 호환 모델들을 지원합니다. 공식 문서나 ollama list / ollama run을 통해 확인할 수 있습니다.
# - CLI(Command Line Interface)와 API로 모델을 실행 가능
# - 모델 다운로드, 실행, API 제공이 한 줄 명령어로 처리됨
# - 자체 Python 라이브러리 또는 REST API를 통해 연동 가능
#
# 다운로드: https://ollama.com/download
# Mac (brew)
# brew install ollama
#
# 모델 실행
# pip install ollama
# ollama pull mistral
# ollama run codellama

import ollama

ollama.pull("mistral")
response = ollama.chat(model="mistral", messages=[{"role": "user", "content": "안녕?"}])
print(response["message"]["content"])
