# LLM 10일차: MCP를 통한 ChatGPT Desktop, Claude Desktop과 윈도우 파일시스템 연동 (확장판)

## 학습 목표
- ChatGPT Desktop과 Claude Desktop에서 MCP 서버를 통해 윈도우 파일시스템 제어
- 파일 탐색, 읽기, 쓰기, 메타데이터 조회, 검색 기능 구현
- LLM이 직접 파일시스템 작업을 수행할 수 있도록 MCP 서버 설계

---

## 1. 아키텍처
```plaintext
ChatGPT Desktop / Claude Desktop (MCP Client)
       │
       ▼
윈도우 파일시스템 MCP 서버 (Python)
       │
       ├─ list_files(dir)
       ├─ read_file(path)
       ├─ write_file(path, content)
       └─ search_files(keyword)
```

---

## 2. MCP 서버 예시 (Windows Filesystem)

```python
import os, fnmatch
from mcp.server import Server

srv = Server("windows_fs")

@srv.command()
def list_files(dir_path: str) -> list[str]:
    '''디렉토리 내 파일 목록'''
    return os.listdir(dir_path)

@srv.command()
def read_file(path: str) -> str:
    '''파일 내용 읽기'''
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@srv.command()
def write_file(path: str, content: str) -> str:
    '''파일 쓰기'''
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return "ok"

@srv.command()
def search_files(keyword: str, root_dir: str = ".") -> list[str]:
    '''키워드가 포함된 파일명 검색'''
    matches = []
    for root, dirs, files in os.walk(root_dir):
        for filename in fnmatch.filter(files, f"*{keyword}*"):
            matches.append(os.path.join(root, filename))
    return matches

if __name__ == "__main__":
    srv.run_stdio()
```

---

## 3. ChatGPT Desktop 설정
1. MCP 서버 실행 (위 Python 코드 실행)
2. ChatGPT Desktop → Settings → MCP → Add Server → STDIO/WS 선택
3. 서버 연결 확인 후 LLM 프롬프트에서 직접 명령 호출 가능

---

## 4. Claude Desktop 설정
- 동일 절차로 MCP 서버 등록
- Claude에서 `list_files`, `read_file` 등 호출 가능

---

## 5. 보안 고려
- 디렉토리 접근 제한
- 쓰기/삭제 권한 구분
- 접근/수정 로그 기록

---

## 6. 실습 과제
1. 특정 폴더 내 `.txt` 파일 목록을 가져오고, LLM이 내용을 요약
2. 키워드로 파일 검색 후, 해당 파일 내용을 읽어 핵심 정보 추출
3. 자동 보고서 파일을 생성하고 저장
