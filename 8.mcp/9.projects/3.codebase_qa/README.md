# 3.codebase_qa — RAG 를 MCP 서버로 노출하기

이 프로젝트는 레포에서 배운 **RAG(검색 증강 생성)** 를 **하나의 MCP 서버**로 감싼다.
한 번 서버로 만들어 두면 **GPT · Claude · LangChain · VSCode** 어디서든 같은 "문서 QA" 능력을 재사용한다.

> 핵심 메시지: 도구(RAG)를 MCP 표준으로 한 번 만들면, 클라이언트만 바꿔 끼우면 된다.

## 구성

```
3.codebase_qa/
├── data/                  코퍼스 (자체 포함된 3개 문서: MCP / RAG / 임베딩)
│   ├── 01_mcp.md
│   ├── 02_rag.md
│   └── 03_embeddings.md
├── server.py              RAG MCP 서버 (자체 data/, InMemory) — search / answer + corpus://info
├── server_docs.py         변형: 실제 레포 문서(0.docs)를 Chroma 영속으로 인덱싱 (대용량)
├── 1.client_raw.py        순수 MCP 클라이언트 (수동 호출)
└── 2.client_langchain.py  LangChain 에이전트가 도구를 자동 선택
```

## 서버가 제공하는 것
| 종류 | 이름 | 설명 |
|------|------|------|
| tool | `search(query, k=3)` | 의미적으로 가까운 청크 k개를 출처와 함께 반환 (검색만) |
| tool | `answer(question)` | 검색 + LLM 으로 문서 근거 답변 (완전한 RAG) |
| resource | `corpus://info` | 인덱싱된 문서 목록과 청크 수 |

서버는 시작 시 `data/*.md` 를 청킹·임베딩해 InMemory 벡터 스토어에 올린다.

## 준비
```bash
pip install mcp langchain-mcp-adapters langchain-openai langchain-text-splitters langgraph python-dotenv
# .env 에 OPENAI_API_KEY  (서버 시작 시 임베딩 생성)
```

> ⚠️ **키는 반드시 이 폴더의 `.env` 로**: MCP 클라이언트는 서버를 자식 프로세스로 띄울 때
> 셸 환경변수를 그대로 넘기지 않는다(SDK 가 환경을 최소화). 그래서 `export OPENAI_API_KEY` 만
> 해두면 **서버가 키를 못 받아 임베딩에 실패하고 조용히 멈춘다**. 이 폴더에 `.env` 를 두면
> 서버의 `load_dotenv()` 가 읽는다. (Claude Desktop 등록 시엔 설정의 `env` 로 전달 — `3.anthropic` 참고)

## 실행

### A. 순수 클라이언트 (수동 호출)
```bash
cd "8.mcp/9.projects/3.codebase_qa"
python 1.client_raw.py
# search('코사인 유사도') 결과 + answer('MCP 서버 vs 클라이언트') RAG 답변
```

### B. LangChain 에이전트 (도구 자동 선택)
```bash
python 2.client_langchain.py
# 에이전트가 search/answer 중 무엇을 쓸지 스스로 결정 → 근거 기반 답변
```

### C. Inspector 로 점검 (선택)
```bash
pip install "mcp[cli]"
mcp dev server.py    # Tools 탭에서 search / answer 직접 호출
```

### E. 실레포 문서(`0.docs`)로 QA — 변형 (`server_docs.py`)
자체 `data/` 대신 **레포의 실제 교안 `0.docs/`** 를 코퍼스로 쓴다. Chroma 영속이라 첫 실행만 임베딩.
```bash
pip install langchain-chroma chromadb          # 추가 의존성
# 클라이언트를 server_docs.py 로 향하게 (환경변수)
QA_SERVER=server_docs.py python 2.client_langchain.py
# PowerShell: $env:QA_SERVER="server_docs.py"; python 2.client_langchain.py
# 다른 폴더를 쓰려면:  CORPUS_DIR=/path/to/docs QA_SERVER=server_docs.py python 1.client_raw.py
```
- 코퍼스를 바꾸면 `chroma_db/` 를 지우고 재인덱싱한다. (`chroma_db/` 는 `.gitignore` 처리됨)
- `.venv` / `site-packages` / `pdf_output` 등은 자동 제외된다.

### D. VSCode / Claude Desktop 에서 사용
같은 `server.py` 를 `.vscode/mcp.json`(→ [`../../5.vscode/`](../../5.vscode/)) 또는
Claude Desktop 설정(→ [`../../3.anthropic/1.claude_desktop/`](../../3.anthropic/1.claude_desktop/))에
등록하면, 그 환경의 에이전트가 이 문서 QA 도구를 그대로 쓴다.

## 관전 포인트
- **서버 코드는 하나(server.py)**, 클라이언트는 raw → LangChain → VSCode/Claude 로 바뀐다 — MCP 의 재사용성.
- `search` 와 `answer` 를 분리한 이유: 에이전트가 "근거만 모아서 직접 종합"할지, "바로 답을 받을지" 선택할 수 있게.
- 코퍼스를 바꾸려면 `data/` 에 `.md` 를 더 넣고 서버를 재시작하면 된다 (사내 위키·코드 문서 등으로 확장 가능).

## 확장 아이디어
- 코퍼스를 레포 실제 문서(`0.docs/`)나 코드로 교체 → "이 레포에 대한 QA 서버"
- InMemory → Chroma 영속화로 재시작 시 재임베딩 비용 0
- `answer` 에 출처 인용(`[파일명]`) 강조, 신뢰도 점수 추가
