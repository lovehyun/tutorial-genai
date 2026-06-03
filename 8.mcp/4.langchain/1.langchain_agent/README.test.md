# MCP 서버 완전한 STDIO 테스트 가이드

## 개요
MCP(Model Context Protocol) 서버를 STDIO 모드로 수동 테스트하는 완전한 가이드입니다.

## 1단계: 서버 시작
```bash
python server2.py
```

서버가 시작되면 다음과 같은 메시지가 출력됩니다:
```
MCP 서버 시작 (STDIO 모드)
사용 가능한 도구:
- say_hello: 인사말 생성
- add: 덧셈 계산
- multiply: 곱셈 계산
- now: 현재 시간
- get_day_of_week: 요일 정보
------------------------------
```

## 2단계: JSON-RPC 메시지 시퀀스

### 2-1. 초기화 요청 (필수)
```json
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}
```

**예상 응답:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {"listChanged": true},
      "resources": {"subscribe": true, "listChanged": true}
    },
    "serverInfo": {
      "name": "ImprovedServer",
      "version": "unknown"
    }
  }
}
```

### 2-2. 초기화 완료 알림 (필수)
초기화 응답을 받은 후 반드시 다음 알림을 보내야 합니다:
```json
{"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
```

**예상 응답:** 없음 (알림이므로 응답 없음)

### 2-3. 도구 목록 조회
```json
{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
```

**예상 응답:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "say_hello",
        "description": "사용자에게 개인화된 인사말을 생성합니다.",
        "inputSchema": {
          "type": "object",
          "properties": {
            "name": {
              "type": "string",
              "description": "인사할 대상의 이름"
            }
          },
          "required": ["name"]
        }
      },
      {
        "name": "add",
        "description": "두 정수를 더합니다.",
        "inputSchema": {
          "type": "object",
          "properties": {
            "a": {"type": "integer", "description": "첫 번째 숫자"},
            "b": {"type": "integer", "description": "두 번째 숫자"}
          },
          "required": ["a", "b"]
        }
      }
    ]
  }
}
```

### 2-4. say_hello 도구 호출
```json
{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "say_hello", "arguments": {"name": "Alice"}}}
```

**예상 응답:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "안녕하세요, Alice님! 좋은 하루 되세요!"
      }
    ]
  }
}
```

### 2-5. add 도구 호출
```json
{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "add", "arguments": {"a": 10, "b": 25}}}
```

**예상 응답:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "10 + 25 = 35"
      }
    ]
  }
}
```

### 2-6. now 도구 호출
```json
{"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "now", "arguments": {}}}
```

**예상 응답:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "현재 시간: 2025년 08월 11일 00시 30분 45초"
      }
    ]
  }
}
```

### 2-7. multiply 도구 호출
```json
{"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "multiply", "arguments": {"a": 7, "b": 8}}}
```

**예상 응답:**
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "7 × 8 = 56"
      }
    ]
  }
}
```

### 2-8. get_day_of_week 도구 호출
```json
{"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "get_day_of_week", "arguments": {}}}
```

**예상 응답:**
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "오늘은 일요일입니다."
      }
    ]
  }
}
```

## 빠른 복사용 전체 시퀀스

### Windows (PowerShell):
```powershell
# 전체 시퀀스를 한 번에 실행
@"
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}
{"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "say_hello", "arguments": {"name": "Alice"}}}
{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "add", "arguments": {"a": 10, "b": 25}}}
{"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "now", "arguments": {}}}
"@ | python server2.py
```

### Linux/Mac:
```bash
# 전체 시퀀스를 한 번에 실행
(
  echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}'
  echo '{"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}'
  echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}'
  echo '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "say_hello", "arguments": {"name": "Alice"}}}'
  echo '{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "add", "arguments": {"a": 10, "b": 25}}}'
  echo '{"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "now", "arguments": {}}}'
) | python server2.py
```

## 중요 주의사항

1. **필수 순서**: `initialize` → `notifications/initialized` → 다른 메소드들
2. **한 줄 입력**: 각 JSON 메시지는 반드시 한 줄로 입력해야 합니다
3. **ID 관리**: 요청에는 고유한 ID가 필요하지만, 알림(`notifications/initialized`)에는 ID가 없습니다
4. **JSON 형식**: 정확한 JSON 형식을 유지해야 합니다 (따옴표, 괄호 등)
5. **응답 확인**: 각 요청 후 응답을 확인하고 다음 단계로 진행하세요

## 트러블슈팅

### "Received request before initialization" 오류
- `initialize` 메시지를 먼저 보내지 않았거나
- `notifications/initialized` 알림을 빠뜨렸을 때 발생

### JSON 파싱 오류
- JSON 형식이 올바르지 않을 때 발생
- 온라인 JSON 검증기로 형식을 확인하세요

### 응답이 보이지 않음
- STDIO 모드에서는 로그와 응답이 섞여서 출력됩니다
- `clear_test.py` 스크립트를 사용하면 더 명확하게 확인할 수 있습니다

## 성공 기준

모든 단계가 성공적으로 완료되면:
1. 초기화 응답에서 서버 정보 확인
2. 도구 목록에서 5개 도구 확인 (`say_hello`, `add`, `multiply`, `now`, `get_day_of_week`)
3. 각 도구 호출 시 예상된 텍스트 응답 확인

이 가이드를 따라하면 MCP 서버가 올바르게 작동하는지 완전히 테스트할 수 있습니다.
