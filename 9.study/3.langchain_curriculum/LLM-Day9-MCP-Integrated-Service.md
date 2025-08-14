# LLM 9일차: MCP를 통한 통합 서비스 (확장판)

## 학습 목표
- MCP(Model Context Protocol)를 이용해 **여러 리소스를 하나의 LLM 서비스에 통합**하는 방법 이해
- 로컬/클라우드/웹 API/데이터베이스 등 다양한 소스를 LLM이 필요에 따라 자동 호출
- ChatGPT Desktop, Claude Desktop, 혹은 서버형 LLM 환경에서 활용

---

## 1. MCP 통합 서비스 개념
- **MCP Client** (LLM 환경)와 **MCP Server** (기능 제공자)를 연결
- 하나의 LLM이 **여러 개의 MCP Server**를 동시에 연결하여 통합 에이전트처럼 활용
- 장점:
  - 새로운 기능을 서버 추가만으로 확장
  - 기능별로 권한과 보안 분리
  - 표준화된 호출 방식(JSON-RPC)으로 유지보수 용이

---

## 2. 통합 아키텍처 예시

```plaintext
사용자 질의
   │
   ▼
LLM (MCP Client)  ←→  MCP 서버 #1 (파일시스템)
                 ←→  MCP 서버 #2 (데이터베이스)
                 ←→  MCP 서버 #3 (웹 API)
```

---

## 3. 통합 MCP 서버 예제 (다중 리소스)

```python
from mcp.server import Server
import os, sqlite3, requests

srv = Server("integrated_service")

@srv.command()
def read_file(path: str) -> str:
    '''로컬 파일 읽기'''
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@srv.command()
def query_db(sql: str) -> list[tuple]:
    '''SQLite 질의 실행'''
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    return rows

@srv.command()
def github_user_info(username: str) -> dict:
    '''GitHub 사용자 정보 가져오기'''
    r = requests.get(f"https://api.github.com/users/{username}")
    return r.json()

if __name__ == "__main__":
    srv.run_stdio()
```

---

## 4. LLM 활용 시나리오
사용자:  
> "프로젝트 메모를 읽고, DB에서 최근 5개 로그를 가져오고, GitHub에서 torvalds 정보 알려줘."

실행 절차:
1. LLM이 `read_file` 호출
2. LLM이 `query_db` 호출
3. LLM이 `github_user_info` 호출
4. 세 결과를 종합 요약 후 사용자에게 응답

---

## 5. 보안 및 관리
- 서버별 접근 경로/쿼리 화이트리스트
- 민감정보는 `.env`에 저장
- 호출 로그 기록 및 감사 기능

---

## 6. 실습 과제
1. 로컬 이미지 폴더 목록을 읽어 LLM이 이미지 설명을 자동 생성
2. DB 쿼리 결과를 차트 이미지로 변환
3. 웹 검색 결과 + 로컬 파일 내용을 결합한 리포트 작성
