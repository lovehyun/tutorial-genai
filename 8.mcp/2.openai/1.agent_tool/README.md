# 2.openai/1.agent_tool — GPT 로 MCP 도구 쓰기 (도구 선택: 수동 → 키워드 → LLM)

하나의 MCP 서버를 두고, 클라이언트가 **어떤 도구를 부를지 고르는 방식**을 단계적으로 고도화한다.
서버는 그대로 두고, 클라이언트의 '판단'만 똑똑해진다.

## 파일
- `server.py` — 기본 서버 (hello, add, now)
- `server2.py` — 확장 서버 (수학·유틸·텍스트 등 다수 도구)

| 클라이언트 | 도구 선택 방식 | 띄우는 서버 |
|---|---|---|
| `1.client_demo.py` | 수동(도구 목록 + 하드코딩 호출) | `server.py` |
| `2.client_simple_nlp.py` | 키워드/정규식 매칭 | `server.py` |
| `3.client_gpt.py` | **GPT function calling 자동 선택** | `server2.py` |

- `*2_tryexcept.py` = 같은 내용 + 네트워크/도구 오류 예외 처리 강화

## 실행
```bash
cd 8.mcp/2.openai/1.agent_tool        # 상대경로 server.py 를 쓰므로 반드시 폴더 안에서 실행
pip install mcp openai python-dotenv
# .env 에 OPENAI_API_KEY  (gpt 버전만 필요)

python 1.client_demo.py        # 서버 자동 실행 → 도구 목록 + 정해진 호출
python 2.client_simple_nlp.py  # 입력을 키워드로 매칭해 도구 선택
python 3.client_gpt.py         # 자연어 → GPT 가 도구/인자 선택 (server2.py)
```
> 클라이언트가 서버를 stdio 자식 프로세스로 **자동 실행** → 서버를 따로 띄울 필요 없음.

## 관전 포인트
- **서버는 한 벌, 클라이언트의 '도구 선택'만 진화**: 하드코딩 → 키워드 → LLM.
- `3.client_gpt` 는 OpenAI function calling 으로 "어떤 도구를 어떤 인자로" 모델이 결정 →
  `4.langchain` 의 에이전트와 같은 아이디어를 SDK 레벨에서 먼저 본다.
- `_tryexcept` 변형으로, 도구 호출 실패를 어떻게 감싸는지 비교.

## 추천 순서
`1.client_demo` → `2.client_simple_nlp` → `3.client_gpt` (필요 시 각 `_tryexcept`)
