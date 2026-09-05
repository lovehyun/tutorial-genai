# 18.mcp_ops_hitl — 사내 IT 비서: 웹 챗봇 × 다중 MCP × HITL × 서브에이전트 × 자동승인

챗봇에게 사내 업무(계정 생성·권한 부여·메일 발송)를 말로 시키면, 에이전트가 세 MCP 서버를 써서 처리한다.
**되돌릴 수 없는 작업 앞에서는 멈춰 사람에게 물어보고**, 오래 걸리는 업무는 **백그라운드 담당자(서브에이전트)에게 위임**한다.

4단계 빌드업이며, 각 단계는 딱 하나씩만 더한다. 3·4단계는 그 안에서 또 "설계를 어떻게
자르느냐"의 변형이 갈려서 각자 하위 폴더(`a`/`b`/`c`)로 나뉜다 — 순서상 다음 단계가
아니라 **같은 문제를 푸는 서로 다른 방식**이라서다.

| 단계 | 더해지는 것 | 포트 | 변경점 |
|---|---|---|---|
| `1.web_agent/` | 웹 챗봇 + MCP 서버 3개 (승인 없음) | 5081 | [CHANGES](1.web_agent/CHANGES.md) |
| `2.hitl_approve/` | **승인 게이트** — 위험한 작업 전 정지 → 승인 카드 | 5082 | [CHANGES](2.hitl_approve/CHANGES.md) |
| `3.background_tasks/` | **서브에이전트 위임** — 백그라운드 실행 + 작업 패널 (세 변형 `a`/`b`/`c`) | 5083·5086·5087 | [README](3.background_tasks/README.md) |
| `4.auto_approve/` | **자동승인** — 한 번 승인한 기능은 안 묻기 (두 변형 `a`도구이름/`b`인자수준) | 5084·5085 | [README](4.auto_approve/README.md) |

4단계는 파일이 셋이다(`jobs.py` · `agents.py` · `app.py`, `a`/`b` 둘 다). `app.py` 가 400줄을
넘어서 나눴는데, **코드를 바꾼 게 아니라 자리만 옮겼다** — 각 파일이 '몇 단계에서 배운 것' 에 대응한다.

> 각 폴더의 `CHANGES.md` 에 **이전 단계에서 무엇이 바뀌는지**만 짧게 정리해 뒀다.
> 라이브로 업그레이드하며 진행할 때 이것만 따라가면 된다.

---

## 핵심: 웹에는 `input()` 이 없다

이 프로젝트에서 배울 것 하나만 꼽으면 이것이다.

CLI([5.mcp/4.langchain/6.human_in_loop](../../5.mcp/4.langchain/6.human_in_loop/))에서는 `input()` 으로 그 자리에서 멈추면 됐다.
프로세스가 통째로 기다린다. **웹은 요청/응답이라 블로킹할 수 없고**, 백그라운드 작업이면 물어볼 요청조차 없다.

```
CLI                        웹 (2~4단계)
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
                    │    └ 워커 에이전트 (실제 조치)  ← 3단계~   │
                    └────────────────┬─────────────────────────┘
                                     │ MultiServerMCPClient
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
      directory_server.py      itops_server.py       notify_server.py
        조회 (안전)          계정·권한 (위험)        메일·메시지 (위험)
              └──────────────────────┴──────────────────────┘
                            같은 SQLite(ops.db) 를 본다
```

### MCP 서버는 4단계 내내 그대로다

`servers/` 폴더 하나를 네 단계(하위 변형 포함 일곱 개 앱)가 공유한다. 승인 로직이 붙든 백그라운드가 붙든
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

cd 10.project/18.mcp_ops_hitl/1.web_agent      && python app.py   # → localhost:5081
cd 10.project/18.mcp_ops_hitl/2.hitl_approve   && python app.py   # → localhost:5082

# 3단계는 세 변형 중 하나를 골라 실행 (세 개를 동시에 띄워서 비교해도 된다 — 포트가 다르다)
cd 10.project/18.mcp_ops_hitl/3.background_tasks/a.sequential       && python app.py # → localhost:5083
cd 10.project/18.mcp_ops_hitl/3.background_tasks/b.parallel_unsafe  && python app.py # → localhost:5086
cd 10.project/18.mcp_ops_hitl/3.background_tasks/c.parallel_guarded && python app.py # → localhost:5087

# 4단계도 두 변형 중 하나를 골라 실행 (포트가 달라 동시에 띄워도 된다)
cd 10.project/18.mcp_ops_hitl/4.auto_approve/a.tool_name_only && python app.py # → localhost:5084
cd 10.project/18.mcp_ops_hitl/4.auto_approve/b.scoped_guard   && python app.py # → localhost:5085
```

- MCP 서버는 **stdio 로 자동 실행**된다. 따로 띄울 필요 없다.
- 데모 데이터를 초기화하려면 `servers/ops.db` 를 지운다 (다음 실행 때 다시 시드된다).
  4단계(`a`·`b` 둘 다)는 **DB 현황 패널의 [초기화] 버튼**으로 앱을 끄지 않고도 되돌릴 수 있다 (확인 창을 거친다).
- 승인 대기까지 초기화하려면 각 단계 폴더의 `checkpoints.sqlite` 도 지운다.
- `langgraph-checkpoint-sqlite` 가 없으면 **메모리 체크포인터로 자동 폴백**한다(앱은 정상 동작,
  대신 서버를 재시작하면 대기 중인 승인이 사라진다). 시작 로그에 어느 쪽인지 찍힌다.

### 시드 데이터

| 사번 | 이름 | 부서 | 계정 |
|---|---|---|---|
| E1001 | 김철수 | 개발팀 사원 | **없음** ← 1단계 온보딩 대상 |
| E1002 | 이영희 | 마케팅팀 대리 | 있음 (email, vpn) |
| E1003 | 박민수 | 재무팀 과장 | 있음 (email, payroll) |
| E1004 | 최유진 | 인사팀 사원 | **없음** ← 2단계 온보딩 대상 |
| E1005 | 정다은 | 영업팀 사원 | **없음** ← 3a 온보딩 대상 |
| E1008 | 한소연 | IT팀 사원 | **없음** ← 3b 온보딩 대상 |
| E1009 | 윤도현 | 물류팀 사원 | **없음** ← 3c 온보딩 대상 |
| E1006 | 강태호 | 디자인팀 사원 | **없음** ← 4a 온보딩 대상 |
| E1007 | 오지훈 | 총무팀 사원 | **없음** ← 4b 온보딩 대상 |

> 단계마다 **다른 온보딩 대상**을 쓴다 — 1~4단계가 전부 같은 `ops.db` 를 공유하는데(아래 "실행" 절),
> 김철수 한 명을 모든 단계가 재사용하면 앞 단계에서 이미 만든 계정이 뒷단계에서
> "이미 있습니다" 로 no-op 돼 버려서 데모가 안 산다.

접근 그룹: `email`(low) · `vpn`(medium) · `github`(medium) · **`prod-db`(high)** · **`payroll`(high)**
— high 인 것들은 "승인해도 되나?" 를 실제로 고민하게 만드는 장치다.

---

## 단계별로 무엇을 보나

### 1단계 — 문제를 먼저 겪는다

(계정·email·vpn 을 먼저 만든 뒤) *"김철수한테 prod-db 권한 줘"* 라고 하면 **그냥 준다.** 아무도 안 묻는다.
(계정이 없는 상태에서 곧바로 시도하면 "계정이 없다"는 안내만 돌아온다 — 1단계 화면의 예제 프롬프트 순서대로
계정 생성 → email·vpn 부여를 먼저 거쳐야 한다.)
운영 DB 접근 권한이 대화 한 줄로 나가는 걸 직접 보는 게 이 단계의 목적이다.

### 2단계 — 승인 게이트

조회는 그냥 흐르고, 계정 변경·발송에서만 승인 카드가 뜬다.

- **화이트리스트로 관리** — `SAFE_TOOLS` 에 있는 것만 자동 통과. 블랙리스트로 하면
  MCP 서버에 새 도구가 생겼을 때 '모르는 도구' 가 무사통과한다. 외부 서버는 내가 모르는 사이 도구가 는다.
- **거부는 중단이 아니라 대화** — 거부하면 `ToolMessage` 로 그 사실을 에이전트에게 돌려준다.
  AI 가 이유를 묻거나 대안을 낸다. 그냥 끊으면 에이전트는 왜 멈췄는지도 모른다.
- **`as_node="tools"` 가 핵심** — 거부 시 도구 실행을 *건너뛰는* 장치.
  이게 없으면 상태에 메시지만 얹히고 도구는 그대로 실행된다.
- **전용 이벤트 루프 스레드** — 1단계는 요청마다 `asyncio.run()` 해도 됐지만,
  2단계부터는 체크포인터가 요청을 넘어 살아 있어야 한다. 백그라운드 스레드에 루프를 하나 띄우고
  Flask 가 거기에 일을 맡긴다.

- **"도구가 없다" 를 말하게 강제** — 승인·거부 어휘를 프롬프트에 주입해 두면, 모델이
  *할 수 없는 상황* 까지 그 프레임으로 설명해버린다. 실제로 없는 `delete_account` 를 시켰더니
  *"승인이 필요한데 거부되었습니다"* 라고 지어낸 사례가 있었다. 승인 게이트보다 위험하다 —
  관리자가 그 보고만 보면 "내가 거부했나 보다" 하고 넘어가기 때문이다. 그래서 프롬프트에 못 박았다:

  ```
  - 요청에 맞는 도구가 없으면 "그 작업을 할 수 있는 도구가 없다" 고 그대로 말한다.
    "승인이 필요하다" 거나 "거부되었다" 는 식으로 이유를 지어내지 않는다.
    승인·거부는 실제로 승인 절차를 거친 작업에 대해서만 언급한다.
  ```

  다만 이것도 프롬프트라 100% 는 아니다. **에이전트의 자기 보고를 믿지 말고 실제 흔적을 보라** —
  4단계의 작업 로그·DB 패널이 있는 이유가 이것이다.

**한계**: 승인 카드가 뜨면 대화가 그 자리에서 멈춘다. 승인할 때까지 다른 일을 못 한다.

### 3단계 — 서브에이전트 위임

> 이 폴더는 실제로 `a.sequential`/`b.parallel_unsafe`/`c.parallel_guarded` 세 변형으로
> 나뉜다 — 모델이 한 턴에 도구를 여러 개 계획했을 때 승인 요청을 어떻게 자르느냐가
> 또 하나의 설계 문제라서다. 자세한 내용과 실습 스크립트는
> [`3.background_tasks/README.md`](3.background_tasks/README.md) 참고. 아래는 세 변형
> 모두에 공통인 뼈대(메인/워커 분리, 백그라운드 위임)만 설명한다.

```
사용자 ──대화──▶ 메인 에이전트   (조회 도구 + delegate_task / list_jobs)
                     │ delegate_task("정다은 온보딩")  ← 기다리지 않고 작업번호만 반환
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

**한계**: 온보딩을 열 명 하면 `create_account` 승인을 열 번 누른다. 매번 같은 판단인데도.
그리고 그 승인 요청을 사람에게 어떻게 보여줄 것인가도 그 자체로 문제다 — 병렬로 계획된
호출을 한 카드에 몰아서 보여주면 위험도를 구분 못 하게 된다(`b.parallel_unsafe`가 이걸 보여준다).

### 4단계 — 자동승인, 그리고 통제를 유지하는 법

> 이 폴더도 두 변형(`a.tool_name_only`/`b.scoped_guard`)으로 나뉜다 — 자동승인을
> "도구 이름" 단위로 걸지, "인자" 수준까지 볼지가 또 하나의 설계 문제라서다. 자세한
> 내용은 [`4.auto_approve/README.md`](4.auto_approve/README.md) 참고.

`[항상 승인]` 을 누르면 그 도구가 `AUTO_APPROVED` 에 올라가 다음부터 안 묻는다.
승인 조건에 한 줄이 붙는 게 전부다.

```python
def needs_approval(call):
    return call["name"] not in SAFE_TOOLS and call["name"] not in AUTO_APPROVED
```

여기서 멈추면 그냥 **가드레일을 끄는 것**이다. 그래서 왼쪽에 패널 두 개를 붙였다.

- **⚡ 자동승인 목록** — 무엇을 위임했는지 항상 보이고, 해제할 수 있다.
  작업 로그에도 `⚡ 자동승인: create_account` 로 남는다.
- **🗄 DB 현황** — 계정·권한·발송 기록. **일부러 MCP 를 거치지 않고** DB 를 직접 읽는다.
  에이전트가 정말로 바꿨는지는 MCP 밖에서 봐야 검증이 되기 때문이다.
  묶음마다 접기/펼치기가 되고, 접어도 개수는 보인다.
- **작업 로그** (채팅창 아래) — 워커가 부른 도구 내역. 기본은 접혀 있다.

`high` 배지는 접근 그룹의 위험도(`servers/store.py` 의 `GROUPS`)다 — `prod-db` · `payroll` 이 high.
권한이 늘어났을 때 눈에 띄게 하려는 표시일 뿐, **승인 로직에는 영향이 없다.**

**`a.tool_name_only`: 자동승인이 '도구 이름' 단위라 범위가 너무 넓다.** `grant_access` 를
한 번 자동승인하면 어떤 그룹을 주든 전부 통과한다 — `prod-db` 도 안 묻고 나간다.
실습에서 직접 확인해 보라 — 이게 이 변형의 진짜 교훈이고, `b.scoped_guard`가 이 구멍을 메운다.

**`b.scoped_guard`: 판단을 인자 수준까지 내린다.**

```python
# a.tool_name_only
def needs_approval(call):
    return call["name"] not in SAFE_TOOLS and call["name"] not in AUTO_APPROVED

# b.scoped_guard
def needs_approval(call):
    if call["name"] in SAFE_TOOLS:
        return False
    if _is_high_risk(call):        # grant_access 이고 group 이 risk=high 면
        return True                #   자동승인 여부와 무관하게 항상 재확인
    return call["name"] not in AUTO_APPROVED
```

- **등록은 그대로 관대하게, 실행 직전 판단만 엄격하게** — `[항상 승인]`을 누르면 여전히
  "도구 이름"을 자동승인 목록에 올린다(`a`와 동일). 다만 `needs_approval()`이 실행 직전에
  인자를 한 번 더 확인해서, `grant_access`의 `group`이 `prod-db`·`payroll`(고위험)이면
  자동승인 목록에 있어도 예외 없이 다시 물어본다.
- **고위험 카드에는 `[항상 승인]` 버튼 자체가 없다** — "이번만 승인"은 있어도 "고위험도 앞으로
  자동으로"는 화면에서 아예 뺐다. 그 버튼이 있으면 guardrail을 다시 끌 수 있는 셈이라 의미가 없다.
- **3단계 문제와 같은 뿌리다** — 3단계(`b.parallel_unsafe`)는 "승인 요청 단위"가 너무 굵어서
  (여러 호출이 한 카드에 뭉쳐 나옴), 여기(`a.tool_name_only`)는 "자동승인 등록 단위"가 너무 굵어서
  (도구 이름 하나로 모든 인자가 통과) 문제였다. **굵은 단위의 자동화는 위험도를 못 본다**는
  같은 교훈이 두 층에서 반복되는 것이다.

**한계**: 지금은 규칙이 `grant_access` + `risk=high` 하나뿐이다. 유효기간·횟수 제한·감사 로그까지
가는 법은 [4.auto_approve/a.tool_name_only/CHANGES.md](4.auto_approve/a.tool_name_only/CHANGES.md) 참고.

---

## 시나리오

> ⚠️ **1~4단계는 전부 같은 `servers/ops.db` 를 공유한다** (위 "실행" 절 참고). 리셋 버튼은 4단계(`a`·`b` 둘 다)에만 있다.
> 단계마다 온보딩 대상을 다르게 배정해 뒀으니(위 "시드 데이터" 참고) 보통은 순서대로 밟아도 서로
> 안 겹치지만, **같은 변형을 두 번째로 실습**할 때는 그 온보딩 대상이 이미 완료돼 있어서
> `create_account`/`grant_access` 가 "이미 있습니다" 로 no-op 응답한다 — 처음 상태로 다시 보고 싶다면
> `servers/ops.db` 를 지우고(또는 4단계의 [초기화] 버튼으로) 시작할 것.

**2단계** (localhost:5082)
```
최유진 찾아서 계정 상태 알려줘        ← 조회라 안 물어본다
계정 만들어줘. 아이디는 yujin 으로     ← 승인 카드
email 이랑 vpn 권한 줘                ← 승인
prod-db 권한도 줘                     ← 거부해 보기. AI 가 대안을 낸다
```

**3단계** — 세 변형(`a` 5083 / `b` 5086 / `c` 5087)에 각자 예제 프롬프트가 있다. 셋 다
온보딩 대상은 다르지만(3a=정다은, 3b=한소연, 3c=윤도현 — 변형끼리도 no-op 안 겹치게)
공통 얼개는 같다: "OO 온보딩 해줘. 계정 ..., email·vpn 권한, 환영 메일까지"로 J001을 배정하고,
"박민수한테 prod-db 권한 줘"로 J002를 동시에 띄워 작업 패널에 승인 대기 카드가 **2개** 뜨는 걸
보는 것 — 단, **승인 카드 안이 도구 하나뿐인지 여러 개가 몰려 있는지**는 변형마다 다르다.
직접 비교해 보려면 [`3.background_tasks/README.md`](3.background_tasks/README.md)의 표와
각 폴더의 "예제 프롬프트" 참고.

**4a** (localhost:5084) — 승인 카드의 `[항상 승인]` 을 눌러 보기
```
강태호 온보딩 해줘. 계정 taeho, email·vpn 권한
    → create_account 승인 카드에서 [항상 승인] → 왼쪽 자동승인 목록에 그 기능이 올라간다
    → 이어지는 grant_access 승인 카드에서도 (email 만 있을 수도, vpn 까지 같이 있을 수도 있다) [항상 승인] → grant_access 도 목록에 오른다
이영희한테 github 권한 줘   ← 같은 기능이라 안 묻는다 (작업 로그에 ⚡ 자동승인)
                              왼쪽 DB 현황에서 권한이 실제로 늘어난 것을 확인
자동승인 목록에서 grant_access [해제]
박민수한테 payroll 권한 줘  ← 해제했으니 다시 물어본다 (박민수는 payroll 이 이미 있어 결과는
                              no-op 지만, "다시 묻는지" 를 확인하는 게 목적 — 이번엔 그냥 [승인]만)

이영희한테 prod-db 권한 줘  ← grant_access 가 다시 자동승인 상태가 아니라 또 물어본다.
                              여기서 별 고민 없이 [항상 승인] 을 눌러 보라 — 고위험 권한 하나가
                              그렇게(별생각 없는 클릭 한 번으로) 나간다

박민수한테 github 권한 줘   ← 방금 그 클릭 한 번 때문에, 이것도 안 묻고 그냥 나간다.
                              "도구 이름" 단위 자동승인이 위험한 이유가 이거다
```

**4b** (localhost:5085) — 4a 마지막 두 줄과 똑같은 요청을 다시 해 보기 (온보딩 대상만 다르다)
```
오지훈 온보딩 해줘. 계정 jihoon, email·vpn 권한
    → create_account, grant_access(email) 카드에서 각각 [항상 승인]
      (자동승인 목록: create_account, grant_access)

박민수한테 vpn 권한 줘      ← vpn 은 고위험이 아니라서 4a 처럼 안 묻는다

박민수한테 prod-db 권한 줘  ← grant_access 는 자동승인 상태인데도 승인 카드가 뜬다!
                              게다가 이 카드엔 [항상 승인] 버튼이 아예 없다 —
                              4a 에서는 이 줄이 아무 표시 없이 그냥 나갔던 것과 비교해 볼 것

박민수한테 payroll 권한 줘  ← payroll 도 고위험이라 마찬가지로 매번 재확인된다
```

---

## 이어서 볼 것

| 주제 | 위치 |
|---|---|
| CLI 에서의 HITL (여기의 원형) | [5.mcp/4.langchain/6.human_in_loop](../../5.mcp/4.langchain/6.human_in_loop/) |
| 서버가 직접 되묻는 방식 (elicitation) | [5.mcp/1.basic/4.advanced/3.elicitation](../../5.mcp/1.basic/4.advanced/3.elicitation/) |
| 원격 HTTP MCP 서버로 바꾸기 | [5.mcp/4.langchain/5.remote_http](../../5.mcp/4.langchain/5.remote_http/) |
| 웹 챗봇 + 다중 MCP 의 최소 형태 | [5.mcp/10.projects/6.multi_mcp_concierge](../../5.mcp/10.projects/6.multi_mcp_concierge/) |

## 실무로 가져갈 때

- **단일 프로세스 전제** — `JOBS` 딕셔너리가 메모리에 있어 워커/웹이 한 프로세스여야 한다.
  여러 워커 프로세스로 늘리려면 작업 큐를 Redis/DB 로 빼고 승인 신호도 그쪽으로 옮긴다.
- **`thread_id` 는 사용자별로 발급** — 지금은 데모라 `"web"` 하나를 쓴다.
  로그인 사용자별로 발급하면 같은 코드로 여러 사용자의 대화가 분리된다.
- **승인 권한도 분리해야 한다** — 지금은 누구나 승인 버튼을 누를 수 있다.
  실무에서는 승인자 역할을 따로 두고 감사 로그(누가 언제 무엇을 승인했는지)를 남긴다.
  권한 분리 UI 는 [16.airline_chatbot](../16.airline_chatbot/) 이 참고가 된다.
