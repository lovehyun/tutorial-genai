# 4.mini_context7 — Context7 같은 "라이브러리 문서 검색" MCP 서버 직접 만들기

실제 [context7](https://context7.com)이 하는 일의 핵심만 떼어내 MCP 서버로 재현한다:
**`resolve_library_id`(이름) → `get_library_docs`(정확한 ID)** 2단계 조회 흐름.

> 핵심 메시지: context7은 "라이브러리 이름 → 정확한 ID 확인 → 그 ID로만 문서 조회"라는
> **모호함 해소(disambiguation) 계약**을 도구 두 개로 나눠 강제한다. [`3.codebase_qa`](../3.codebase_qa/)(RAG)와
> 다른 점은 "의미로 검색"이 아니라 "정확한 식별자로 찾기"가 핵심이라는 것 — 그래서 이 서버는
> 임베딩도 LLM도 필요 없다.

## 왜 굳이 2단계인가

`"react"` 라는 이름만으로는 서버가 뭘 원하는지 모른다 — Facebook의 React인지, 다른 동명
패키지인지. 그래서 진짜 context7은:
1. `resolve-library-id("react")` → 후보 여러 개를 순위(관련성/신뢰도)와 함께 반환한다. 모호하면
   에이전트가 그중 하나를 고른다.
2. `get-library-docs("/facebook/react")` → **정확한 ID**로만 문서를 내준다.

이 서버도 같은 계약을 흉내낸다. `get_library_docs`는 등록되지 않았거나 부정확한 ID가 오면
문서 대신 "먼저 `resolve_library_id`를 부르라"는 메시지를 돌려준다.

## 구성

```
4.mini_context7/
├── data/
│   ├── requests/            requests 라이브러리 문서 2개
│   ├── fastapi/              FastAPI 문서 2개
│   └── mcp-python-sdk/       MCP Python SDK 문서 2개
├── server.py                 mini-context7 서버 — resolve_library_id / get_library_docs
├── 1.client_raw.py           순수 MCP 클라이언트 (수동 호출, 가드레일 확인 포함)
└── 2.client_langchain.py     LangChain 에이전트가 2단계를 스스로 순서대로 호출
```

## 서버가 제공하는 것

| 종류 | 이름 | 설명 |
|------|------|------|
| tool | `resolve_library_id(libraryName)` | 이름/별칭으로 후보 라이브러리 ID를 유사도 점수순으로 반환 |
| tool | `get_library_docs(context7_compatible_library_id, topic="", tokens=4000)` | 정확한 ID로 문서를 가져온다. `topic`으로 좁히기, `tokens`로 길이 제한. 모르는 ID면 거부 |
| resource | `context7://libraries` | 등록된 라이브러리 전체 목록 (실제 context7의 카탈로그에 해당) |

등록된 라이브러리는 데모용으로 손으로 채운 3개: `requests`, `fastapi`, `mcp-python-sdk`
(`server.py`의 `LIBRARIES` 딕셔너리).

## 준비

```bash
pip install mcp
# 2.client_langchain.py 를 쓸 때만 추가로:
pip install langchain-mcp-adapters langchain-openai langgraph python-dotenv
# 그리고 이 폴더에 .env (OPENAI_API_KEY)
```

> **서버 자체는 API 키가 필요 없다** — LLM도 임베딩도 안 쓴다. `3.codebase_qa`(RAG)와 가장
> 다른 점이다. 문서를 찾는 방식이 "의미 검색"이 아니라 "이름 유사도 + 키워드 필터"라 가볍다.

## 실행

### A. 순수 클라이언트 (수동, 2단계 + 가드레일)

```bash
cd "5.mcp/10.projects/4.mini_context7"
python 1.client_raw.py
```

`resolve_library_id('fastapi')` → 후보 목록 → `get_library_docs('/tiangolo/fastapi', topic='쿼리')`
→ 문서, 그리고 마지막에 등록 안 된 ID(`/facebook/react`)로 바로 호출해 **거부 메시지**를 확인한다.

### B. LangChain 에이전트 (자동으로 순서대로 호출)

```bash
python 2.client_langchain.py
```

자연어 질문만 주면 에이전트가 `resolve_library_id`를 먼저 부르고, 거기서 얻은 ID로
`get_library_docs`를 부르는 걸 콘솔 로그(`→ 도구 호출: ...`)로 확인할 수 있다 —
**도구 docstring이 호출 순서를 유도**했기 때문이다.

### C. Inspector로 점검 (선택)

```bash
pip install "mcp[cli]"
mcp dev server.py    # Tools 탭에서 resolve_library_id / get_library_docs 직접 호출
```

### D. VSCode / Claude Code에 등록해서 써보기

```json
{
  "mcpServers": {
    "mini-context7": { "command": "python", "args": ["server.py"] }
  }
}
```

`.vscode/mcp.json`(Copilot Agent Mode)에 넣거나, Claude Code라면:

```powershell
claude mcp add mini-context7 -- "C:\...\tutorial-genai\.venv\Scripts\python.exe" "C:\...\4.mini_context7\server.py"
```

등록 후 채팅에서: *"mini-context7으로 FastAPI 쿼리 파라미터 문서 찾아줘"*.
자세한 등록 절차는 [`../../5.vscode/1.dev_helpers/README.md`](../../5.vscode/1.dev_helpers/README.md) 참고 —
거기 나온 `dev-helper` 서버와 등록 방식이 완전히 동일하다.

## 동작 원리 (관전 포인트)

1. `resolve_library_id`는 입력 문자열을 라이브러리별 **이름+별칭**과 대조해 유사도 점수를
   매기고(`difflib`), 상위 후보를 `"Context7-compatible library ID"` 형식(`/org/project`)으로
   반환한다.
2. `get_library_docs`는 **그 정확한 ID만 신뢰**한다 — 등록되지 않은 ID가 오면 문서 대신 "먼저
   resolve하라"는 에러 문자열을 돌려준다. 이건 프로토콜이 강제하는 게 아니라 **서버 코드가
   스스로 검증**하는 것이다. [`10.project/18.mcp_ops_hitl`](../../../10.project/18.mcp_ops_hitl/README.md)에서
   "도구 설명(프롬프트)만으론 100% 강제가 안 된다"고 배운 것과 같은 이유로, 여기서는
   *서버가 직접 최후 방어선* 역할을 한다.
3. `topic` 파라미터는 문서 전체가 아니라 관련 파일만 필터링한다 — 실제 context7이 토큰 예산을
   아끼려고 관련 섹션만 주는 것과 같은 목적이다.
4. `tokens`는 실제로는 **"문자 수 상한"**이다(진짜 토큰 카운트가 아님) — 데모를 단순화한
   지점이라고 수업에서 짚어주면 좋다.

## 실제 context7과 다른 점 (이 데모의 한계)

- **카탈로그 크기** — 진짜 context7은 수천 개 라이브러리의 **최신 공식 문서를 지속적으로
  크롤링**한다. 여기는 3개 라이브러리, 손으로 쓴 마크다운 6개뿐. 늘리려면 `data/<lib>/`에
  폴더를 추가하고 `LIBRARIES`에 등록하면 된다 — `3.codebase_qa`의 `server_docs.py`처럼 실제
  문서 폴더를 통째로 인덱싱하는 방식으로도 확장 가능하다.
- **버전 인식** — context7은 라이브러리 **버전별**로 문서가 다르다(예: FastAPI 0.100 vs
  0.115). 여기는 버전 개념이 없다.
- **검색 방식** — 여기는 이름 유사도(`difflib`) + 키워드 substring. 진짜 context7이나 RAG형
  문서 검색은 임베딩 기반 의미 검색을 쓴다 → 이 레포에선 `3.codebase_qa`가 그 예시.
- **배포 형태** — context7은 **원격 HTTP MCP 서버**(누구나 URL로 접속)다. 여기는 로컬 stdio.
  원격으로 바꾸려면 [`../2.remote/1.intro`](../2.remote/1.intro/README.md) 패턴대로
  `mcp.run(transport="streamable-http")`로 바꾸고 배포하면 된다.

## 확장 아이디어

- `LIBRARIES`에 사내 라이브러리/사내 SDK를 등록해 "사내 context7" 만들기
- 버전 파라미터 추가: `get_library_docs(id, version="1.0")` → `data/<lib>/<version>/` 하위 탐색
- 키워드 매칭 대신 임베딩 검색으로 바꿔 `3.codebase_qa`와 합치기
- HTTP로 배포해 여러 팀이 같은 문서 서버를 공유 (`../2.remote` 패턴)
