# 2.openai/2.multi_tools — 여러 MCP 서버를 한 클라이언트에서

도구를 기능별 서버로 나누고(math / utility), 한 클라이언트가 **여러 서버에 동시에 붙어** 도구를 모아 쓴다.

## 파일
- `math_server.py` — hello, add
- `utility_server.py` — current_time, weather
- `1.math_client.py` / `2.utility_client.py` — 서버 1개씩 단독 점검
- `3.smart_client_manual.py` — 두 서버 동시 연결 + 키워드로 도구 선택
- `4.smart_client_gpt.py` — 두 서버 동시 연결 + **GPT 가 도구 선택 + 인자 파싱**

## 실행
```bash
cd 5.mcp/2.openai/2.multi_tools
pip install mcp openai python-dotenv
# .env 에 OPENAI_API_KEY  (gpt 버전만 필요)

python 1.math_client.py           # math_server 단독
python 2.utility_client.py        # utility_server 단독
python 3.smart_client_manual.py   # math + utility 동시, 키워드 라우팅
python 4.smart_client_gpt.py      # math + utility 동시, GPT 라우팅
```
> 모든 클라이언트가 서버를 stdio 로 **자동 실행**. `3`/`4` 는 `AsyncExitStack` 으로 두 서버를 동시에 관리.

## 관전 포인트
- **멀티 서버**: 도구를 서버 단위로 쪼개고 클라이언트가 합쳐 쓴다 →
  `4.langchain/1.quickstart/4.multi_server.py` 와 같은 그림을 langchain 없이.
- 단독 점검 → 키워드 라우팅(manual) → LLM 라우팅(gpt) 으로 고도화.
- `4.smart_client_gpt` 는 도구 스키마를 보고 **인자까지 파싱** — function calling 의 실전 형태.

## 추천 순서
`1.math_client` → `2.utility_client` → `3.smart_client_manual` → `4.smart_client_gpt`
