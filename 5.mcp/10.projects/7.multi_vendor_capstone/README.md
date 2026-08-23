# 10.projects/7.multi_vendor_capstone — 서버 하나, 벤더 셋

`6.multi_mcp_concierge/`가 "**서버 여러 개**를 한 클라이언트가 쓴다"를 보여줬다면, 여기는 정반대
방향 — "**서버 하나**를 벤더가 다른 클라이언트 여럿이 그대로 쓴다"를 보여준다. `server.py`는
단 한 벌이고, 그 코드는 한 글자도 안 바뀐 채로 OpenAI·Anthropic·LangChain 세 클라이언트에
동시에 붙는다. MCP가 "도구 제공자 ↔ LLM 클라이언트 사이의 USB"(레포 최상위 README의 비유)라는
게 말뿐이 아니라는 걸 실제로 확인하는 자리다.

## 파일
| 파일 | 내용 |
|---|---|
| `server.py` | 도구 2개(`get_weather`, `calculate`) — 이후 아무 파일도 이 코드를 고치지 않는다 |
| `1.client_openai.py` | GPT function calling으로 호출 |
| `2.client_anthropic.py` | Claude tool_use로 호출 |
| `3.client_langchain.py` | `langchain-mcp-adapters`로 호출 |
| `4.compare_all.py` | **같은 질문을 세 벤더에게 동시에 던져 답을 나란히 비교** — 이 폴더의 결론 |

## 실행
```bash
pip install mcp openai anthropic langchain-mcp-adapters langchain-openai langgraph python-dotenv
# .env 에 OPENAI_API_KEY, ANTHROPIC_API_KEY

python 1.client_openai.py       # 벤더 하나씩 먼저 확인
python 2.client_anthropic.py
python 3.client_langchain.py
python 4.compare_all.py         # 셋을 동시에 — 이 폴더가 보여주려는 것
```

## 실행 결과 (실측)
```
질문: 서울 날씨 어때?
[OpenAI]     현재 서울 날씨는 맑고, 기온은 22도입니다.
[Anthropic]  현재 서울의 날씨는... 🌤️ 맑음, 🌡️ 22도... (이모지 섞어 풍부하게 답함)
[LangChain]  서울의 현재 날씨는 맑고, 기온은 22도입니다.

질문: 23 곱하기 7은?
[OpenAI]     23 곱하기 7은 161입니다.
[Anthropic]  23 곱하기 7은 161입니다! 😊
[LangChain]  23 곱하기 7은 161입니다.
```
세 벤더 모두 **같은 도구(`get_weather`/`calculate`)를 같은 인자로 호출**해서 같은 사실을
가져왔다 — 답변 문체(Anthropic이 이모지를 더 쓰는 것 같은)만 벤더 성격 차이지, 근거 데이터는
`server.py` 하나에서 나온 동일한 값이다.

## 관전 포인트
- **서버 코드는 정말 하나도 안 바뀐다** — 세 클라이언트 파일을 diff 해보면 "MCP 도구 스키마를
  어느 벤더 형식으로 바꾸는가"만 다르다: OpenAI는 `inputSchema`를 그대로 `parameters`로,
  Anthropic은 `input_schema`(snake_case)로, LangChain은 어댑터가 알아서 `BaseTool`로.
- **어댑터가 뭘 대신 해주는지**: `1`/`2`번은 스키마 변환 함수(`to_openai_tools`/`to_anthropic_tools`)를
  직접 짰다. `3`번(LangChain)은 그 변환을 `langchain-mcp-adapters`가 대신 한다 — 앞의 두 파일을
  먼저 보고 오면 어댑터의 존재 가치가 훨씬 잘 보인다.
- `4.compare_all.py`는 `asyncio.gather`로 세 서버 프로세스를 **동시에** 띄운다 — stdio 세션은
  1클라이언트:1서버라 프로세스는 3개가 뜨지만, 그 3개가 실행하는 코드(`server.py`)는 완전히 같다.

## 다음 단계
- 서버를 여러 개 쓰는 반대 방향 → [`../6.multi_mcp_concierge/`](../6.multi_mcp_concierge/)
- 벤더별 스키마 변환을 더 자세히 → [`../../2.openai/1.agent_tool/`](../../2.openai/1.agent_tool/),
  [`../../4.langchain/1.quickstart/`](../../4.langchain/1.quickstart/)
