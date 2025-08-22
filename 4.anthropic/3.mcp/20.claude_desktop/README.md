
# MCP Hello 서버 × Claude Desktop 연동 가이드

이 문서는 **파이썬으로 MCP 서버(hello)를 개발**하고 **Claude Desktop에 연결**하여
대화 중 툴처럼 호출하는 전체 과정을 빠르게 실습할 수 있도록 구성했습니다.

---

## 0) 미리 알아두기

- **MCP(Model Context Protocol)**: LLM 클라이언트(Claude Desktop 등)와 외부 도구/데이터를 표준 방식으로 연결하는 프로토콜입니다.
- **전송(Transport)**: 입문은 `stdio`가 가장 간단합니다. (클라이언트가 서버 프로세스를 실행 → stdin/stdout으로 JSON-RPC 통신)
- **핵심 주의점**: `stdio` 서버에서 **`print()`로 stdout에 로그를 찍지 마세요.** 프로토콜 프레이밍이 깨질 수 있습니다. 로깅은 `logging`으로 구성하여 **stderr**로 출력하세요.

---

## 1) 준비물

- Python 3.10+
- (권장) [uv](https://github.com/astral-sh/uv) 패키지/가상환경 관리자
- Claude Desktop (최신 버전)

> uv 없이도 가능합니다. 아래 **부록 A**를 참고해 `venv + pip`로 진행할 수 있습니다.

---

## 2) 프로젝트 구조

```text
mcp-hello/
├─ hello_server.py   # MCP 서버(툴 정의)
└─ (가상환경/의존성은 uv 또는 venv로 관리)
```

---

## 3) 파이썬 MCP 서버 만들기 (`hello_server.py`)

```python
# hello_server.py
from mcp.server.fastmcp import FastMCP
import logging

mcp = FastMCP("hello")  # 서버 이름

@mcp.tool()
async def hello(name: str) -> str:
    """간단한 인사말을 돌려줍니다."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    # stdout에 print() 금지! 로거는 stderr로 흘러가도록 설정
    logging.basicConfig(level=logging.INFO)
    mcp.run(transport="stdio")
```

- `FastMCP`는 타입힌트/Docstring 기반으로 툴 스키마를 자동 생성합니다.
- 서버 이름은 `"hello"`이며, `hello(name: str)` 툴 하나를 제공합니다.

---

## 4) 의존성 설치 & 실행 (uv 권장)

### 4.1 uv 설치 (한 번만)
- **macOS/Linux**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Windows (PowerShell)**
  ```powershell
  irm https://astral.sh/uv/install.ps1 | iex
  ```

### 4.2 프로젝트 의존성 설치
```bash
# 프로젝트 루트에서
uv venv
# macOS/Linux
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

uv add "mcp[cli]"
```

### 4.3 로컬 실행 테스트
```bash
uv run hello_server.py
```
- 에러 없이 대기 상태면 정상입니다. (직접 호출하려면 MCP 클라이언트가 필요합니다. 연동은 다음 단계에서 진행합니다.)

---

## 5) Claude Desktop에 MCP 서버 등록

Claude Desktop이 MCP 서버를 **자동 실행/연결**하도록 설정 파일(JSON)에 등록합니다.

### 5.1 설정 파일 경로
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

> 파일이 없으면 새로 만드셔도 됩니다.

### 5.2 설정 JSON 예시 (uv로 서버 실행)

> 아래에서 `C:/ABSOLUTE/PATH/TO/mcp-hello`(Windows) 또는 `/Users/you/path/mcp-hello`(macOS) 부분을 **절대경로**로 바꿔주세요.

```json
{
  "mcpServers": {
    "hello": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/ABSOLUTE/PATH/TO/mcp-hello",
        "run",
        "hello_server.py"
      ]
    }
  }
}
```

- macOS의 경우 예:
  ```json
  {
    "mcpServers": {
      "hello": {
        "command": "uv",
        "args": [
          "--directory",
          "/Users/you/path/mcp-hello",
          "run",
          "hello_server.py"
        ]
      }
    }
  }
  ```

### 5.3 적용 방법
1. Claude Desktop **완전 종료** 후 다시 실행합니다.
2. 입력창 우측/하단의 **툴 아이콘** 또는 **Search & tools** 패널에서 `hello` 서버(툴)가 보이면 성공입니다.

---

## 6) 사용법 (Claude 대화에서 호출)

Claude 대화창에서 자연어로 요청하세요. 예:

> "`hello` 툴로 제 이름 ‘박수현’에게 인사해줘."

Claude가 툴 호출을 제안/실행하고, 응답(`Hello, 박수현!`)을 메시지에 포함해 줍니다.
툴 목록은 우측 상단의 **Search & tools** 패널에서도 확인할 수 있습니다.

---

## 7) 트러블슈팅 체크리스트

1. **아이콘/툴이 안 보임**
   - 설정 JSON 문법 오류 여부 확인 (쉼표/중괄호/따옴표).
   - 절대경로가 맞는지 확인 (`--directory`, 파일명).
   - Claude Desktop을 **완전 종료 후 재실행**.
   - 서버가 터미널에서 단독 실행될 때 에러가 없는지 확인.

2. **서버는 뜨는데 호출이 실패**
   - `hello_server.py`에서 **stdout에 print 사용 금지**: 반드시 `logging` 사용.
   - 가상환경/의존성 문제: `uv run hello_server.py`로 실행되는지 재확인.

3. **로그 위치**
   - **macOS**: `~/Library/Logs/Claude/`
   - **Windows**: `%APPDATA%\Claude\logs\`
   - `mcp.log`, `mcp-server-hello.log` 등 확인.

---

## 8) 다음 단계 (확장 아이디어)

- **여러 툴 추가**: 파일 읽기(`read_file(path)`), HTTP 호출(`fetch(url)`), 로컬 DB 조회(`query(sql)`) 등 도구를 늘려 워크플로 자동화.
- **권한 제어**: 위험 명령(파일 삭제 등)은 툴을 분리하고 입력 검증/화이트리스트로 보호.
- **전송 확장**: stdio 외에 WebSocket/HTTP 전송 사용(고급).

---

## 부록 A) uv 없이 venv + pip로 설치하는 방법

```bash
# 가상환경 생성
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

pip install -U pip
pip install "mcp[cli]"

# 실행
python hello_server.py
```

---

## 부록 B) 보안 팁

- 툴 입력은 항상 **밸리데이션**(예: 경로 화이트리스트, URL 스킴 체크)하세요.
- 시스템 리소스 조작(파일/프로세스/네트워크)은 **명시 허용된 범위**에서만 제공하세요.
- 민감한 정보(토큰/키)는 환경변수나 OS 비밀 저장소를 이용해 관리하세요.
