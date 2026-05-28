# 항공 예약 + 챗봇 + 상담사 연결 — 3단계 빌드업

가상 항공사 예약 시스템에 챗봇/에이전트를 점진적으로 결합. 마지막에는 사용자↔관리자 실시간 채팅까지.

## 폴더 구조

```
16.airline_chatbot/
├── 1.system_base/             포트 6001 — 챗봇 없이 시스템 기본 (사용자/관리자 뷰)
├── 2.chatbot_each_view/       포트 6002 — 각 뷰에 챗봇/에이전트 (권한 분리)
├── 3.consultant_relay/        포트 6003 — + 상담사 연결 실시간 채팅
└── README.md
```

## 데이터 모델 (SQLite)

```
flights       : 항공편 카탈로그 (code, origin, dest, depart_at, seats_left, price)
bookings      : 사용자 예약 (user_id, flight_id, status=BOOKED/CANCELED)
booking_log   : 상태 변경 이력 (action, actor, at)
consultations : (#3) 상담 세션 (REQUESTED/ACTIVE/CLOSED, admin_id)
consultation_messages : (#3) 상담 안 오간 메시지 (sender=user/admin/system)
```

## 단계별 빌드업

### 1.system_base — 기본 시스템 (포트 6001)

| | 사용자 뷰 (`/`) | 관리자 뷰 (`/admin`) |
|---|---|---|
| 항공편 | 검색 (출발/도착) | — |
| 예약 | 클릭으로 예약 / 본인 예약 취소 | 강제 취소 |
| 조회 | 내 예약 + 상태 | 전체 예약 / 시스템 통계 / 예약 이력 |

REST API 가 두 뷰 공통:
```
GET    /api/flights?origin=&dest=
GET    /api/my-bookings          (사용자)
POST   /api/bookings             {flight_id}
POST   /api/bookings/<id>/cancel
GET    /api/all-bookings         (관리자)
GET    /api/stats                (관리자)
GET    /api/bookings/<id>/history(관리자)
```

### 2.chatbot_each_view — 각 뷰에 챗봇 추가 (포트 6002)

각 뷰에 **다른 도구 세트**를 가진 에이전트가 들어감 — 권한 분리.

| | 사용자 챗봇 | 관리자 챗봇 |
|---|---|---|
| 도구 | `search_flights`, `book_flight`, `my_bookings`, `cancel_my_booking` | `admin_stats`, `admin_all_bookings`, `admin_booking_history`, `admin_force_cancel` |
| 권한 | **본인 예약만** | 전체 시스템 |
| 라우트 | `POST /chat/user` | `POST /chat/admin` |
| 메모리 | `thread_id=user-{user_id}` | `thread_id=admin` |

자연어 예:
- 사용자: "ICN→NRT 가장 싼 거 예약해줘"
- 관리자: "취소된 예약 몇 건이야?", "#3 강제 취소"

### 3.consultant_relay — 상담사 연결 실시간 채팅 (포트 6003)

챗봇 한계를 넘는 요청 → 사람 상담사로 에스컬레이션.

**흐름:**
```
1) 사용자 챗봇이 request_consultation 도구 호출
   → consultations 테이블에 REQUESTED 레코드 생성
   → 사용자 화면에 "상담사 대기 중..." 패널 등장
2) 관리자 화면이 활성 상담 목록을 폴링 (2초)
   → "수락" 클릭하면 status=ACTIVE
3) 사용자측 / 관리자측 양쪽 폴링으로 새 메시지 송수신
4) 어느 쪽이든 "종료" 누르면 status=CLOSED
```

**추가 도구 / API**:
```
사용자 도구: + request_consultation(topic)

REST API:
  POST   /api/consultations/<id>/accept   (관리자 수락)
  POST   /api/consultations/<id>/close    (양쪽 종료)
  POST   /api/consultations/<id>/messages {text, sender}
  GET    /api/consultations/<id>/messages?since=<id>     (폴링)
  GET    /api/consultations                              (관리자 활성 목록)
  GET    /api/my-consultation                            (사용자 현재 상담)
```

**기술 선택**:
- WebSocket 대신 **2초 폴링** — 코드 가벼움, 동일한 사용 경험
- `since=<last_id>` 로 새 메시지만 가져오기 (전체 재조회 X)

## 실행

```bash
pip install flask langchain langchain-openai langgraph python-dotenv
# .env 에 OPENAI_API_KEY (2, 3단계)

cd 1.system_base       && python app.py   # → http://localhost:6001
cd ../2.chatbot_each_view && python app.py # → http://localhost:6002
cd ../3.consultant_relay  && python app.py # → http://localhost:6003
```

각 단계는 자체 `airline.db` 가 폴더에 생성됨 (단계 간 격리).

## 시연 시나리오 (3단계)

1. 브라우저 두 개 열기
2. 한 쪽에서 `http://localhost:6003/` → 사용자 로그인 (예: `alice`)
3. 다른 쪽에서 `http://localhost:6003/admin` → 관리자 화면
4. 사용자 챗봇에 "환불 문의인데 상담사 연결해줘" 입력
5. 관리자 화면 "활성 상담" 목록에 새 요청 등장 → **수락** 클릭
6. 양쪽이 실시간으로 메시지 주고받기
7. 종료

## 학습 포인트

1. **권한 분리 (2단계)** — 같은 LLM 도 도구 세트로 권한이 강제됨. 사용자가 admin 도구 못 부름.
2. **에이전트 → 사람 에스컬레이션 (3단계)** — 챗봇이 답할 수 없는 영역을 인지하고 다른 채널로 인계.
3. **실시간 동기화** — WebSocket 없이 폴링만으로도 충분한 UX 가능.
4. **상태 머신** — `REQUESTED → ACTIVE → CLOSED` 의 간단한 상태 전이 + UI 가 그 상태 따라 변함.
