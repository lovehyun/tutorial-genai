# Windows에서 Ollama는 일반적으로 C:\Users\사용자이름\AppData\Local\Programs\Ollama 에 설치됩니다.
# dir %LOCALAPPDATA%\Programs\Ollama\
# dir %LOCALAPPDATA%\Ollama\
#
# tasklist | findstr ollama
# taskkill /F /IM ollama.exe  # Windows에서 Ollama 종료

# 기본 포트 11434
# OLLAMA_HOST=0.0.0.0:8080 ollama serve
# curl http://localhost:11434/api/tags 

import requests

url = "http://localhost:11434/api/chat"
data = {
    "model": "mistral",
    "messages": [{"role": "user", "content": "안녕?"}],
    "stream": False  # 스트리밍을 비활성화 (기본이 스트림처리)
}

response = requests.post(url, json=data)

# 응답을 텍스트 형태로 출력
print("Response Text:", response.text)

# JSON 변환 테스트
try:
    json_response = response.json()
    # print(json_response)
    print(json_response["message"]["content"])
except requests.exceptions.JSONDecodeError:
    print("JSON 디코딩 오류 발생! 응답 내용:", response.text)
