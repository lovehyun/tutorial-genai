# 18.mcp_ops_assistant — 사내 IT 비서: 웹 챗봇 × 다중 MCP × HITL × 서브에이전트

챗봇에게 사내 업무(계정 생성·권한 부여·메일 발송)를 말로 시키면, 에이전트가 세 MCP 서버를 써서 처리한다.
**되돌릴 수 없는 작업 앞에서는 멈춰 사람에게 물어보고**, 오래 걸리는 업무는 **백그라운드 담당자(서브에이전트)에게 위임**한다.

3단계 빌드업이며, 각 단계는 딱 하나씩만 더한다.

| 단계 | 더해지는 것 | 포트 | 변경점 |
|---|---|---|---|
| `1.web_agent/` | 웹 챗봇 + MCP 서버 3개 (승인 없음) | 5081 | [CHANGES](1.web_agent/CHANGES.md) |
| `2.hitl_approve/` | **승인 게이트** — 위험한 작업 전 정지 → 승인 카드 | 5082 | [CHANGES](2.hitl_approve/CHANGES.md) |
| `3.background_tasks/` | **서브에이전트 위임** — 백그라운드 실행 + 작업 패널 | 5083 | [CHANGES](3.background_tasks/CHANGES.md) |

> 각 폴더의 `CHANGES.md` 에 **이전 단계에서 무엇이 바뀌는지**만 짧게 정리해 뒀다.
> 라이브로 업그레이드하며 진행할 때 이것만 따라가면 된다.

---

## 핵심: 웹에는 `input()` 이 없다

이 프로젝트에서 배울 것 하나만 꼽으면 이것이다.

CLI([8.mcp/4.langchain/6.human_in_loop](../../8.mcp/4.langchain/6.human_in_loop/))에서는 `input()` 으로 그 자리에서 멈추면 됐다.
프로세스가 통째로 기다린다. **웹은 요청/응답이라 블로킹할 수 없고**, 백그라운드 작업이면 물어볼 요청조차 없다.

```
CLI                        웹 (2·3단계)
──────────────             ────────────────────────────────────────
input() 블로킹        →    ① 에이전트가 도구 호출 직전 정지 (interrupt_before)
프로세스가 그 자리에서       ② 멈춘 상태가 checkpointer 에 통째로 저장된다  ← 전부의 열쇠
기다린다                    ③ /chat 은 "승인 대기" 라고 응답하고 끝 (연결을 안 붙잡는다)
                           ④ 승인 버튼 → /approve 가 그 상태를 꺼내 재개
```

**기다림을 프로세스가 아니라 저장소가 담당한다.** `thread_id` 가 사실상 작업 티켓 번호이고,
영속 체크포인터를 쓰면 브라우저를 닫아도 서버를 재시작해도 승인 대기가 살아남는다.
CLI 예제에서 `MemorySaver` 를 쓰며 "실무에선 SqliteSaver" 라고 적어둔 이유가 여기서 드러난다.

---

## 구조

```
                    ┌──────────────────────────────────────────┐
사용자 ──웹 채팅──▶ │  Flask app.py                            │
                    │    ├ 메인 에이전트 (대화·조회·위임)        │
                    │    └ 워커 에이전트 (실제 조치)  ← 3단계    │
                    └────────────────┬─────────────────────────┘
                                     │ MultiServerMCPClient
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
      directory_server.py      itops_server.py       notify_server.py
        조회 (안전)          계정·권한 (위험)        메일·메시지 (위험)
              └──────────────────────┴──────────────────────┘
                            같은 SQLite(ops.db) 를 본다
```

### MCP 서버는 3단계 내내 그대로다

`servers/` 폴더 하나를 세 단계가 공유한다. 승인 로직이 붙든 백그라운드가 붙든
**서버 코드는 한 줄도 바뀌지 않는다.** 이게 MCP 를 쓰는 이유다 —
안전장치는 서버가 아니라 **서버를 쓰는 쪽**이 건다. 서버를 고칠 수 없는 상황(다른 팀 소유, 외부 벤더)이 실제로 흔하다.

| 서버 | 도구 | 성격 |
|---|---|---|
| `directory_server.py` | `find_employee` · `get_account_status` · `list_groups` | 읽기 전용 → **자동 통과** |
| `itops_server.py` | `create_account` · `grant_access` · `revoke_access` · `reset_password` | ⚠️ 되돌리기 어려움 |
| `notify_server.py` | `send_email` · `post_message` · (`list_sent` 는 조회) | ⚠️ 회수 불가 |

세 서버는 **별개 프로세스**라 메모리를 공유할 수 없다. itops 가 만든 계정이 directory 조회에 안 보이면
데모가 성립하지 않으므로, 같은 `ops.db` 를 보게 했다(사내 시스템들이 같은 DB 를 바라보는 구조).

---

## 실행

```bash
pip install flask langchain langchain-openai langchain-mcp-adapters langgraph \
            langgraph-checkpoint-sqlite python-dotenv mcp
# .env 에 OPENAI_API_KEY

cd 10.project/18.mcp_ops_assistant/1.web_agent      && python app.py   # → localhost:5081
cd 10.project/18.mcp_ops_assistant/2.hitl_approve   && python app.py   # → localhost:5082
cd 10.project/18.mcp_ops_assistant/3.background_tasks && python app.py # → localhost:5083
```

- MCP 서버는 **stdio 로 자동 실행**된다. 따로 띄울 필요 없다.
- 데모 데이터를 초기화하려면 `servers/ops.db` 를 지운다 (다음 실행 때 다시 시드된다).
- 승인 대기까지 초기화하려면 각 단계 폴더의 `checkpoints.sqlite` 도 지운다.
- `langgraph-checkpoint-sqlite` 가 없으면 **메모리 체크포인터로 자동 폴백**한다(앱은 정상 동작,
  대신 서버를 재시작하면 대기 중인 승인이 사라진다). 시작 로그에 어느 쪽인지 찍힌다.

### 시드 데이터

| 사번 | 이름 | 부서 | 계정 |
|---|---|---|---|
| E1001 | 김철수 | 개발팀 사원 | **없음** ← 온보딩 대상 |
| E1002 | 이영희 | 마케팅팀 대리 | 있음 (email, vpn) |
| E1003 | 박민수 | 재무팀 과장 | 있음 (email, payroll) |

접근 그룹: `email`(low) · `vpn`(medium) · `github`(medium) · **`prod-db`(high)** · **`payroll`(high)**
— high 인 것들은 "승인해도 되나?" 를 실제로 고민하게 만드는 장치다.

---

## 단계별로 무엇을 보나

### 1단계 — 문제를 먼저 겪는다

*"김철수한테 prod-db 권한 줘"* 라고 하면 **그냥 준다.** 아무도 안 묻는다.
운영 DB 접근 권한이 대화 한 줄로 나가는 걸 직접 보는 게 이 단계의 목적이다.

### 2단계 — 승인 게이트

조회는 그냥 흐르고, 계정 변경·발송에서만 승인 카드가 뜬다.

- **화이트리스트로 관리** — `SAFE_TOOLS` 에 있는 것만 자동 통과. 블랙리스트로 하면
  MCP 서버에 새 도구가 생겼을 때 '모르는 도구' 가 무사통과한다. 외부 서버는 내가 모르는 사이 도구가 는다.
- **거부는 중단이 아니라 대화** — 거부하면 `ToolMessage` 로 그 사실을 에이전트에게 돌려준다.
  비서가 이유를 묻거나 대안을 낸다. 그냥 끊으면 에이전트는 왜 멈췄는지도 모른다.
- **`as_node="tools"` 가 핵심** — 거부 시 도구 실행을 *건너뛰는* 장치.
  이게 없으면 상태에 메시지만 얹히고 도구는 그대로 실행된다.
- **전용 이벤트 루프 스레드** — 1단계는 요청마다 `asyncio.run()` 해도 됐지만,
  2단계부터는 체크포인터가 요청을 넘어 살아 있어야 한다. 백그라운드 스레드에 루프를 하나 띄우고
  Flask 가 거기에 일을 맡긴다.

**한계**: 승인 카드가 뜨면 대화가 그 자리에서 멈춘다. 승인할 때까지 다른 일을 못 한다.

### 3단계 — 서브에이전트 위임

```
사용자 ──대화──▶ 메인 에이전트   (조회 도구 + delegate_task / list_jobs)
                     │ delegate_task("김철수 온보딩")  ← 기다리지 않고 작업번호만 반환
                     ▼
                 작업 큐 ──▶ 워커 에이전트 (MCP 도구 전부)  ← 백그라운드 루프에서 실행
                     │           │ 위험한 도구를 만나면 정지
                     │           ▼
                     └──▶ 작업 패널에 "승인 대기" ──▶ 승인/거부 ──▶ Event.set() 으로 워커를 깨움
```

- **메인과 워커는 `thread_id` 가 다르다** = 완전히 분리된 대화. 워커가 여럿이면 각자 동시에 진행하고
  각자 따로 승인을 기다린다.
- **`asyncio.Event` 로 재운다** — 워커는 스레드를 붙잡지 않고 잠들어 있으므로,
  그 사이 채팅도 다른 워커도 같은 루프에서 자유롭게 돈다.
- **권한 분리** — 메인 에이전트에는 조회 도구만 준다. 계정을 바꾸는 도구는 아예 손에 쥐어주지 않는다.
  프롬프트로 부탁하는 것보다 **도구를 안 주는 게** 확실하다.
- 작업 패널은 **1초 폴링**([16.airline_chatbot](../16.airline_chatbot/) 과 같은 방식)으로 상태를 가져온다.

---

## 시나리오

**2단계** (localhost:5082)
```
김철수 찾아서 계정 상태 알려줘        ← 조회라 안 물어본다
계정 만들어줘. 아이디는 chulsoo 로     ← 승인 카드
email 이랑 vpn 권한 줘                ← 승인
prod-db 권한도 줘                     ← 거부해 보기. 비서가 대안을 낸다
```

**3단계** (localhost:5083)
```
김철수 온보딩 해줘. 계정 chulsoo, email·vpn 권한, 환영 메일까지
    → 작업번호가 나오고 채팅이 바로 풀린다
이영희 계정 상태 알려줘               ← 작업이 도는 동안에도 대화가 된다
                                      (2단계였다면 승인할 때까지 막혀 있었다)
박민수 prod-db 권한 줘                ← 두 작업이 동시에 진행되고 각자 승인을 기다린다
진행 상황 알려줘                      ← 메인이 list_jobs 로 조회해 답한다
```

---

## 이어서 볼 것

| 주제 | 위치 |
|---|---|
| CLI 에서의 HITL (여기의 원형) | [8.mcp/4.langchain/6.human_in_loop](../../8.mcp/4.langchain/6.human_in_loop/) |
| 서버가 직접 되묻는 방식 (elicitation) | [8.mcp/1.basic/4.advanced/3.elicitation](../../8.mcp/1.basic/4.advanced/3.elicitation/) |
| 원격 HTTP MCP 서버로 바꾸기 | [8.mcp/4.langchain/5.remote_http](../../8.mcp/4.langchain/5.remote_http/) |
| 웹 챗봇 + 다중 MCP 의 최소 형태 | [8.mcp/9.projects/5.multi_mcp_concierge](../../8.mcp/9.projects/5.multi_mcp_concierge/) |

## 실무로 가져갈 때

- **단일 프로세스 전제** — `JOBS` 딕셔너리가 메모리에 있어 워커/웹이 한 프로세스여야 한다.
  여러 워커 프로세스로 늘리려면 작업 큐를 Redis/DB 로 빼고 승인 신호도 그쪽으로 옮긴다.
- **`thread_id` 는 사용자별로 발급** — 지금은 데모라 `"web"` 하나를 쓴다.
  로그인 사용자별로 발급하면 같은 코드로 여러 사용자의 대화가 분리된다.
- **승인 권한도 분리해야 한다** — 지금은 누구나 승인 버튼을 누를 수 있다.
  실무에서는 승인자 역할을 따로 두고 감사 로그(누가 언제 무엇을 승인했는지)를 남긴다.
  권한 분리 UI 는 [16.airline_chatbot](../16.airline_chatbot/) 이 참고가 된다.
