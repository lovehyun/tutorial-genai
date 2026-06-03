# 공식 MCP 서버/클라이언트 사용 가이드

## 개요

이 가이드는 공식 MCP (Model Context Protocol) SDK를 사용하여 서버와 클라이언트를 설정하고 테스트하는 방법을 설명합니다.

---

## 설치 요구사항

```bash
pip install mcp python-dotenv
```

---

## 서버 실행 방법

### 1. 기본 실행 (STDIO 모드)
```bash
python server.py
```

출력:
```
기본 서버 시작 (STDIO 모드)
```

### 2. HTTP 모드 실행
```bash
python server.py --http
```

출력:
```
HTTP 서버 시작
```

### 3. STDIO 모드 실행
```bash
python server.py --stdio
```

### 4. 도움말
```bash
python server.py --help
```

출력:
```
사용법:
  python server.py          # 기본 STDIO 서버
  python server.py --stdio  # STDIO 서버
  python server.py --http   # HTTP 서버
  python server.py --help   # 도움말
```

---

## 사용 가능한 도구

서버는 다음 7개의 도구를 제공합니다:

1. **hello** - 인사말 생성
   - 매개변수: name (선택, 기본값: "World")
   - 반환: 문자열

2. **add** - 두 숫자 덧셈
   - 매개변수: a, b (필수)
   - 반환: 숫자

3. **multiply** - 두 숫자 곱셈
   - 매개변수: a, b (필수)
   - 반환: 숫자

4. **current_time** - 현재 시간 조회
   - 매개변수: 없음
   - 반환: 문자열 (YYYY-MM-DD HH:MM:SS 형식)

5. **weather** - 가상 날씨 정보
   - 매개변수: city (필수)
   - 반환: 딕셔너리 (도시, 온도, 상태, 습도, 출처)

6. **get_server_info** - 서버 정보
   - 매개변수: 없음
   - 반환: 딕셔너리 (이름, 상태, 프레임워크, 타임스탬프)

7. **echo** - 메시지 반향
   - 매개변수: message (필수)
   - 반환: 문자열

---

## 클라이언트 실행 방법

### 1. 클라이언트 시작
```bash
python client.py
```

### 2. 모드 선택
```
MCP 클라이언트 테스트
모드를 선택하세요:
1. 자동 테스트
2. 대화형 테스트
선택 (1/2): 
```

---

## 자동 테스트 모드

자동 테스트는 모든 도구를 순차적으로 실행합니다:

```
MCP 서버 연결: http://localhost:8000/mcp
==================================================
서버 연결 성공

사용 가능한 도구 (7개):
  - hello: 인사말을 생성합니다.
  - add: 두 숫자를 더합니다.
  - multiply: 두 숫자를 곱합니다.
  - current_time: 현재 시간을 조회합니다.
  - weather: 도시의 날씨 정보를 조회합니다 (가상 데이터).
  - get_server_info: 서버 정보를 반환합니다.
  - echo: 메시지를 그대로 반환합니다.

==================================================
도구 테스트 시작
==================================================

테스트 1/8: 인사말 테스트
  도구: hello
  매개변수: {'name': 'MCP User'}
  결과: Hello, MCP User! (from remote server)
  ----------------------------------------

테스트 2/8: 기본값 테스트
  도구: hello
  매개변수: {}
  결과: Hello, World! (from remote server)
  ----------------------------------------

... (계속)

모든 테스트 완료
```

---

## 대화형 테스트 모드

대화형 모드에서는 직접 명령어를 입력할 수 있습니다:

```
대화형 MCP 클라이언트
========================================
사용 가능한 명령어:
  - hello: 인사말을 생성합니다.
  - add: 두 숫자를 더합니다.
  - multiply: 두 숫자를 곱합니다.
  - current_time: 현재 시간을 조회합니다.
  - weather: 도시의 날씨 정보를 조회합니다 (가상 데이터).
  - get_server_info: 서버 정보를 반환합니다.
  - echo: 메시지를 그대로 반환합니다.

사용 예시:
  hello Alice
  add 10 20
  weather Seoul
  time
  quit (종료)
----------------------------------------

[사용자] 명령: hello Alice
[서버] Hello, Alice! (from remote server)

[사용자] 명령: add 15 25
[서버] 15.0 + 25.0 = 40.0

[사용자] 명령: weather Seoul
[서버] {'city': 'Seoul', 'temperature': '22°C', 'condition': '맑음', 'humidity': '60%', 'source': 'remote_server'}

[사용자] 명령: time
[서버] Remote server time: 2025-08-29 15:30:45

[사용자] 명령: quit
대화형 모드를 종료합니다.
```

### 대화형 명령어

- **hello [이름]** - 인사말 (이름 선택)
- **add 숫자1 숫자2** - 두 숫자 더하기
- **multiply 숫자1 숫자2** - 두 숫자 곱하기
- **time** - 현재 시간
- **weather [도시]** - 날씨 정보 (도시 선택, 기본값: Seoul)
- **info** - 서버 정보
- **echo 메시지** - 메시지 반향
- **quit** - 프로그램 종료

---

## 환경변수 설정

클라이언트에서 서버 URL을 변경하려면 `.env` 파일 생성:

```bash
# .env 파일
MCP_SERVER_URL=http://localhost:8000/mcp
```

또는 환경변수 직접 설정:

```bash
# Windows
set MCP_SERVER_URL=http://localhost:8000/mcp

# Mac/Linux
export MCP_SERVER_URL=http://localhost:8000/mcp
```

---

## STDIO vs HTTP 모드

### STDIO 모드 (기본)
- 표준 입출력 통신
- 로컬 전용
- 네트워크 설정 불필요
- 더 안정적

### HTTP 모드
- HTTP 통신
- 원격 접근 가능
- 네트워크 설정 필요
- 웹 기반 클라이언트 지원

---

## 오류 해결

### 1. 서버 연결 실패
```
연결 오류: [Errno 61] Connection refused
```

**해결 방법:**
- 서버가 HTTP 모드로 실행 중인지 확인
- 포트 번호 확인 (기본: 8000)
- 방화벽 설정 확인

### 2. 모듈 없음 오류
```
ModuleNotFoundError: No module named 'mcp'
```

**해결 방법:**
```bash
pip install mcp python-dotenv
```

### 3. STDIO 모드에서 HTTP 클라이언트 실행
HTTP 클라이언트는 STDIO 서버와 통신할 수 없습니다. 서버를 HTTP 모드로 실행하세요:

```bash
python server.py --http
```

---

## 원격 접속 설정

### 1. 서버 컴퓨터에서:
```bash
python server.py --http
```

### 2. 방화벽 설정:
- Windows: Windows Defender 방화벽에서 포트 8000 허용
- Mac/Linux: `sudo ufw allow 8000`

### 3. 클라이언트 컴퓨터에서:
```bash
# 환경변수 설정
export MCP_SERVER_URL=http://192.168.1.100:8000/mcp
python client.py
```

---

## 서버 종료

서버를 종료하려면 터미널에서 `Ctrl+C`를 누르세요.

```
^C
대화형 모드를 종료합니다.
```

---

## 요약

이 MCP 서버/클라이언트는 공식 MCP SDK를 사용하여 표준 프로토콜을 지원합니다. STDIO와 HTTP 두 가지 전송 방식을 지원하며, 자동 테스트와 대화형 모드를 통해 쉽게 테스트할 수 있습니다.
