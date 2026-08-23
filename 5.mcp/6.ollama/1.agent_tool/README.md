# 6.ollama/1.agent_tool — 로컬 모델(Ollama)로 MCP 도구 쓰기

`2.openai/1.agent_tool/`, `3.anthropic/2.anthropic_api/`와 완전히 대칭 구조 — 같은 서버, 같은
질문, **API 키도 인터넷도 필요 없는 로컬 모델**로 도구를 자동 선택·호출한다. 도구 선택 방식을
수동→키워드→LLM 순으로 고도화하는 흐름은 동일하다.

## 파일
- `server.py` — 다른 두 벤더 폴더와 **완전히 같은 도구 3개**(hello, add, now)

| 클라이언트 | 도구 선택 방식 |
|---|---|
| `1.client_demo.py` | 수동(하드코딩) — 다른 벤더판과 코드 100% 동일 |
| `2.client_manual_nlp.py` | 키워드/정규식 매칭 — 다른 벤더판과 코드 100% 동일 |
| `3.client_ollama.py` | **로컬 모델(qwen2.5:7b) 자동 선택** — 여기서부터 갈린다 |

## 사전 준비
```bash
# https://ollama.com 에서 설치(또는 앱 실행 — 로컬 서버가 자동으로 뜬다)
ollama pull qwen2.5:7b     # 4.7GB, 도구 호출을 비교적 안정적으로 지원
pip install mcp ollama
```

## 실행
```bash
cd 5.mcp/6.ollama/1.agent_tool
python 1.client_demo.py         # 서버 자동 실행 → 도구 목록 + 정해진 호출
python 2.client_manual_nlp.py   # 입력을 키워드로 매칭해 도구 선택
python 3.client_ollama.py       # 자연어 → 로컬 모델이 도구/인자 선택
```

## 관전 포인트
- **Ollama의 tool calling은 OpenAI 포맷을 그대로 따른다** — `to_ollama_tools()`가
  `2.openai/1.agent_tool/3.client_gpt.py`의 `to_openai()`와 사실상 같은 모양이다. 벤더가
  자발적으로 같은 wire format을 쓰기로 한 드문 사례.
- **완전 무료·오프라인** — API 키도, 인터넷 연결도 필요 없다. 비용 걱정 없이 반복 테스트할 때,
  민감한 데이터를 외부로 보내면 안 될 때 특히 유용하다(자세한 건 `2.langchain/1.llm_models/
  3.1_ollama.py` 참고 — 같은 이유가 여기도 적용된다).
- **`temperature=0`이 상용 모델보다 더 중요하다** — 기본 설정으로 실행했을 때 qwen2.5:7b가
  구조화된 도구 호출 대신 `{"name": "add", ...}` 같은 텍스트를 **본문에 그대로 새어나오게**
  응답한 걸 실제로 확인했다(재현 실패). `temperature=0`으로 고정하니 반복 실행에서 안정적으로
  재현됐다 — 로컬 오픈웨이트 모델은 상용 모델보다 도구 호출 형식이 덜 안정적일 수 있다는 걸
  직접 겪은 사례.
- **약한 모델의 한계도 정직하게 보임** — "오늘 날씨는?"(맞는 도구 없음)에 대한 응답이
  GPT-4o-mini/Claude보다 덜 깔끔하다. 무료·로컬의 트레이드오프를 감추지 않는다.
- **더 큰 모델(`qwen3.6`, 23GB)은 이 환경에서 응답이 2분 넘게 걸려 실습엔 부적합** — 로컬 모델은
  "더 크면 무조건 낫다"가 아니라 **하드웨어에 맞는 크기**를 골라야 한다는 것도 확인된 사실.

## 다음
- 같은 서버, 다른 벤더 비교 → [`../../2.openai/1.agent_tool/`](../../2.openai/1.agent_tool/),
  [`../../3.anthropic/2.anthropic_api/`](../../3.anthropic/2.anthropic_api/)
- LangChain으로 Ollama를 쓰는 법(체인/에이전트) → [`../../../2.langchain/1.llm_models/3.1_ollama.py`](../../../2.langchain/1.llm_models/3.1_ollama.py)
