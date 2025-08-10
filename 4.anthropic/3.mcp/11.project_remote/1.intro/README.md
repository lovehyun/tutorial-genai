# 원격 MCP 서버 사용 가이드

## 개요

이 가이드는 간단한 원격 MCP (Model Context Protocol) 서버를 설정하고 테스트하는 방법을 설명합니다. 서버와 클라이언트가 분리된 구조로 실제 원격 통신을 경험할 수 있습니다.

---

## 서버 실행 방법

### 1. 일반 실행 (경고 없음) - 권장
```bash
python server/server.py
```

### 2. 개발 모드 (auto-reload 지원)
```bash
python server/server.py --dev
```

실행 성공 시 다음과 같은 출력이 나타납니다:
```
원격 MCP 서버 시작...
서버 주소: http://localhost:8000
도구 목록: http://localhost:8000/tools
헬스 체크: http://localhost:8000/health
==================================================
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 웹 브라우저 테스트

서버가 실행된 후 웹 브라우저에서 다음 URL들을 확인할 수 있습니다.

### 1. 서버 상태 확인
**URL:** http://localhost:8000

**예상 응답:**
```json
{
  "message": "Simple Remote MCP Server",
  "status": "running"
}
```

### 2. 도구 목록 보기
**URL:** http://localhost:8000/tools

**예상 응답:**
```json
[
  {
    "name": "hello",
    "description": "인사말을 생성합니다",
    "parameters": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "인사할 대상의 이름"
        }
      },
      "required": []
    }
  },
  {
    "name": "add",
    "description": "두 숫자를 더합니다",
    "parameters": {
      "type": "object",
      "properties": {
        "a": {
          "type": "number",
          "description": "첫 번째 숫자"
        },
        "b": {
          "type": "number",
          "description": "두 번째 숫자"
        }
      },
      "required": ["a", "b"]
    }
  },
  {
    "name": "current_time",
    "description": "현재 시간을 조회합니다",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "weather",
    "description": "도시의 날씨 정보를 조회합니다 (가상)",
    "parameters": {
      "type": "object",
      "properties": {
        "city": {
          "type": "string",
          "description": "도시 이름"
        }
      },
      "required": ["city"]
    }
  }
]
```

### 3. 헬스 체크
**URL:** http://localhost:8000/health

**예상 응답:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-21T10:30:45.123456"
}
```

### 4. 특정 도구 정보 조회

**hello 도구:**
**URL:** http://localhost:8000/tools/hello

**예상 응답:**
```json
{
  "name": "hello",
  "description": "인사말을 생성합니다",
  "parameters": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "인사할 대상의 이름"
      }
    },
    "required": []
  }
}
```

**add 도구:**
**URL:** http://localhost:8000/tools/add

**예상 응답:**
```json
{
  "name": "add",
  "description": "두 숫자를 더합니다",
  "parameters": {
    "type": "object",
    "properties": {
      "a": {
        "type": "number",
        "description": "첫 번째 숫자"
      },
      "b": {
        "type": "number",
        "description": "두 번째 숫자"
      }
    },
    "required": ["a", "b"]
  }
}
```

---

## 명령 프롬프트에서 API 테스트

### 1. 도구 목록 조회
```cmd
curl http://localhost:8000/tools
```

### 2. hello 도구 실행
```cmd
curl -X POST http://localhost:8000/execute -H "Content-Type: application/json" -d "{\"tool_name\": \"hello\", \"parameters\": {\"name\": \"Test\"}}"
```

**예상 응답:**
```json
{
  "success": true,
  "result": "Hello, Test! (from remote server)",
  "error": null
}
```

### 3. add 도구 실행
```cmd
curl -X POST http://localhost:8000/execute -H "Content-Type: application/json" -d "{\"tool_name\": \"add\", \"parameters\": {\"a\": 10, \"b\": 20}}"
```

**예상 응답:**
```json
{
  "success": true,
  "result": 30,
  "error": null
}
```

### 4. current_time 도구 실행
```cmd
curl -X POST http://localhost:8000/execute -H "Content-Type: application/json" -d "{\"tool_name\": \"current_time\", \"parameters\": {}}"
```

**예상 응답:**
```json
{
  "success": true,
  "result": "Remote server time: 2025-07-21 10:30:45",
  "error": null
}
```

### 5. weather 도구 실행
```cmd
curl -X POST http://localhost:8000/execute -H "Content-Type: application/json" -d "{\"tool_name\": \"weather\", \"parameters\": {\"city\": \"Seoul\"}}"
```

**예상 응답:**
```json
{
  "success": true,
  "result": {
    "city": "Seoul",
    "temperature": "22°C",
    "condition": "맑음",
    "humidity": "60%",
    "source": "remote_server"
  },
  "error": null
}
```

### 6. hello 도구 (기본값 테스트)
```cmd
curl -X POST http://localhost:8000/execute -H "Content-Type: application/json" -d "{\"tool_name\": \"hello\", \"parameters\": {}}"
```

**예상 응답:**
```json
{
  "success": true,
  "result": "Hello, World! (from remote server)",
  "error": null
}
```

---

## 오류 테스트

### 1. 존재하지 않는 도구 호출
```cmd
curl -X POST http://localhost:8000/execute -H "Content-Type: application/json" -d "{\"tool_name\": \"unknown_tool\", \"parameters\": {}}"
```

**예상 응답:**
```json
{
  "success": false,
  "result": null,
  "error": "알 수 없는 도구: unknown_tool"
}
```

### 2. 필수 매개변수 누락
```cmd
curl -X POST http://localhost:8000/execute -H "Content-Type: application/json" -d "{\"tool_name\": \"add\", \"parameters\": {\"a\": 10}}"
```

**예상 응답:**
```json
{
  "success": false,
  "result": null,
  "error": "a와 b 매개변수가 필요합니다"
}
```

---

## 서버 로그 확인

서버를 실행한 터미널에서 다음과 같은 로그를 확인할 수 있습니다:

```
도구 실행 요청: hello - {'name': 'Test'}
도구 실행 성공: Hello, Test! (from remote server)
INFO:     127.0.0.1:54321 - "POST /execute HTTP/1.1" 200 OK

도구 실행 요청: add - {'a': 10, 'b': 20}
도구 실행 성공: 30
INFO:     127.0.0.1:54322 - "POST /execute HTTP/1.1" 200 OK
```

---

## 원격 접속 설정

### 다른 컴퓨터에서 접속하려면:

1. **서버 컴퓨터의 IP 주소 확인:**
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig` 또는 `ip addr`

2. **방화벽 설정:**
   - 포트 8000번 열기
   - Windows: Windows Defender 방화벽 설정
   - Mac/Linux: `sudo ufw allow 8000`

3. **클라이언트에서 접속:**
   ```bash
   curl http://192.168.1.100:8000/tools  # 서버 IP로 변경
   ```

---

## curl이 없는 경우

Windows에서 curl이 설치되어 있지 않다면 다음 방법을 사용할 수 있습니다:

### 방법 1: Windows 10/11 내장 curl 사용
Windows 10 버전 1803 이후부터는 curl이 기본 제공됩니다.

### 방법 2: 웹 브라우저 개발자 도구 사용
1. 웹 브라우저에서 F12 키를 눌러 개발자 도구 열기
2. Console 탭에서 다음 JavaScript 코드 실행:

```javascript
fetch('http://localhost:8000/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    tool_name: 'hello',
    parameters: { name: 'Browser User' }
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

### 방법 3: Python 스크립트로 테스트
```python
import requests

# 도구 목록 조회
response = requests.get('http://localhost:8000/tools')
print(response.json())

# hello 도구 실행
response = requests.post('http://localhost:8000/execute', 
    json={'tool_name': 'hello', 'parameters': {'name': 'Python User'}})
print(response.json())
```

---

## 서버 종료

서버를 종료하려면 터미널에서 `Ctrl+C`를 누르세요.

```
^C
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [12345]
```

---

## 요약

이 원격 MCP 서버는 다음 4개의 도구를 제공합니다:

1. **hello** - 인사말 생성 (name 매개변수 선택)
2. **add** - 두 숫자 덧셈 (a, b 매개변수 필수)
3. **current_time** - 현재 시간 조회 (매개변수 없음)
4. **weather** - 가상 날씨 정보 (city 매개변수 필수)

모든 도구는 `/execute` 엔드포인트를 통해 JSON 형태로 호출할 수 있으며, 성공/실패 여부와 결과를 명확하게 반환합니다.
