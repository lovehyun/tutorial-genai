# Todo + Chatbot — 3단계 빌드업

Flask + SQLite Todo 앱에 챗봇을 점진적으로 결합하는 실전 예제.

## 폴더 구조

```
15.todo_chatbot/
├── 1.basic_crud/         포트 5001 — 챗봇 없음, 그냥 CRUD
├── 2.chatbot_readonly/   포트 5002 — 챗봇 추가 (조회만 가능)
├── 3.chatbot_full/       포트 5003 — 챗봇이 CRUD 다 가능 + 화면 자동 갱신
└── README.md
```

각 단계 폴더 구조 (동일):
```
N.이름/
├── app.py                Flask 진입점 + 챗봇 (있다면)
├── templates/index.html
└── static/style.css
```

## 단계별 빌드업

| 단계 | 도구 / 기능 | 챗봇 권한 | UI 자동 갱신 |
|---|---|---|---|
| **1.basic_crud** | UI 만 (form / checkbox / 삭제 버튼) | — | — |
| **2.chatbot_readonly** | + `list_todos` 도구 | 조회 / 요약 | — |
| **3.chatbot_full** | + `add_todo` / `toggle_done` / `delete_todo` | **전부** | ✅ |

### 1단계 (1.basic_crud)
**무엇**: Flask + sqlite3 로 todo 모델 만들고 REST API + 기본 UI.

**API**:
```
GET    /api/todos          전체 목록
POST   /api/todos          {text} 추가
PATCH  /api/todos/<id>     {done} 또는 {text} 수정
DELETE /api/todos/<id>     삭제
```

→ 다음 단계의 챗봇이 같은 REST API 를 호출 (도구로 감싸서).

### 2단계 (2.chatbot_readonly)
**추가된 것**:
- `@tool` 로 `list_todos` 1개 정의 (읽기만)
- `create_react_agent` 로 에이전트 생성
- POST `/chat` 라우트
- UI 우측에 챗봇 패널 (메시지 박스 + 입력)

**프롬프트 정책**:
- "이번 단계는 조회 전용" 명시
- 사용자가 "추가/삭제" 를 요청해도 안내만 (실제 변경 X)

### 3단계 (3.chatbot_full)
**추가된 것**:
- 도구 3개 더: `add_todo`, `toggle_done`, `delete_todo`
- POST `/chat` 응답에 `changed: bool` 포함
- 프런트가 `changed=true` 면 todo 목록 자동 `fetch('/api/todos')` 재호출 → 화면 즉시 갱신

**프롬프트 정책**:
- "OO 완료" / "OO 추가" / "OO 삭제" 같은 자연어를 도구 호출로 매핑
- 변경 작업 전에 `list_todos` 로 id 확인하도록 가이드

**대화 예시**:
```
나:  회의 자료 준비 추가해줘
AI:  [add_todo] '회의 자료 준비' 추가했습니다.    ← 화면 자동 새로고침

나:  회의 자료 끝났어
AI:  [list_todos → toggle_done] #N '회의 자료 준비' 를 완료로 표시했습니다. ← 자동 새로고침

나:  완료한 거 다 지워줘
AI:  [list_todos → delete_todo x N] 완료된 N 개를 삭제했습니다.        ← 자동 새로고침
```

## 실행

```bash
pip install flask langchain langchain-openai langgraph python-dotenv
# .env 에 OPENAI_API_KEY 필요 (2, 3 단계)

# 각 단계에서 디렉토리 들어가서 실행
cd 1.basic_crud     && python app.py    # → http://localhost:5001
cd ../2.chatbot_readonly && python app.py # → http://localhost:5002
cd ../3.chatbot_full     && python app.py # → http://localhost:5003
```

> 각 단계는 자체 디렉토리에 `todo.db` 가 따로 생성됨. 단계 간 데이터는 공유 안 됨 (의도).

## 학습 포인트

1. **단계 분리 = REST API 우선 설계의 가치**
   1단계에서 만든 API 를 2/3단계 챗봇 도구가 그대로 호출. 같은 백엔드 위에 챗봇 레이어만 얹는 패턴.

2. **읽기 → 쓰기 권한 분리**
   2단계의 "조회 전용" 챗봇은 위험 0. 3단계에서 쓰기 도구를 추가하며 권한 확대.

3. **UI 자동 갱신의 단순한 신호**
   복잡한 WebSocket 없이도 `changed: true` 한 줄로 충분. 챗봇 변경 → 프런트 fetch → 동기화.
