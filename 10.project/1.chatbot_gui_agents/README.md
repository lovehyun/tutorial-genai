# AI Agent Chatbot

Flask 기반의 다중 Agent 시스템을 활용한 ChatGPT 클론 웹서비스입니다.

## 🚀 주요 기능

### 🤖 다중 Agent 시스템
- **Memory Agent**: 대화 기록을 메모리에 저장하고 관리
- **Search Agent**: 외부 웹 검색을 통한 최신 정보 제공
- **Calculation Agent**: 수학적 계산 및 통계 처리
- **Chat Agent**: 자연스러운 대화 응답 생성

### 💬 실시간 채팅 인터페이스
- WebSocket을 통한 실시간 통신
- Agent들의 처리 과정을 실시간으로 시각화
- 모던하고 반응형 웹 디자인

### 🔍 Agent 동작 시각화
- 각 Agent의 활성화 상태 실시간 표시
- 처리 과정과 결과를 웹 페이지에서 확인
- 사용된 Agent들과 생각 과정 표시

## 📁 프로젝트 구조

```
1.chatbot_gui_agents/
├── app.py                 # Flask 메인 애플리케이션
├── requirements.txt       # Python 의존성
├── README.md             # 프로젝트 설명서
├── agents/               # Agent 모듈들
│   ├── __init__.py
│   ├── agent_manager.py  # Agent 관리 및 조율
│   ├── memory_agent.py   # 메모리 관리 Agent
│   ├── search_agent.py   # 검색 Agent
│   ├── calculation_agent.py # 계산 Agent
│   └── chat_agent.py     # 채팅 Agent
└── templates/            # HTML 템플릿
    └── index.html        # 메인 웹 인터페이스
```

## 🛠️ 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 서버 실행
```bash
python app.py
```

### 3. 웹 브라우저에서 접속
```
http://localhost:5000
```

## 🎯 사용 예시

### 기본 대화
```
사용자: 안녕하세요
AI: 안녕하세요! 무엇을 도와드릴까요?
```

### 계산 요청
```
사용자: 15 + 27 계산해줘
AI: 계산이 성공적으로 수행되었습니다. 15 + 27 = 42
```

### 검색 요청
```
사용자: 파이썬 프로그래밍에 대해 검색해줘
AI: "파이썬 프로그래밍"에 대한 검색 결과를 찾았습니다.
```

### 복합 요청
```
사용자: 인공지능 뉴스를 검색하고 관련 통계도 계산해줘
AI: 검색과 계산을 모두 수행하여 결과를 제공합니다.
```

## 🔧 Agent 상세 설명

### Memory Agent
- **기능**: 대화 기록 저장 및 컨텍스트 유지
- **활성화**: 모든 대화에서 자동 활성화
- **저장**: 최대 100개의 대화 기록 유지

### Search Agent
- **기능**: 외부 웹 검색 및 정보 수집
- **활성화 조건**: "검색", "찾아", "정보", "뉴스" 등 키워드 감지
- **결과**: 검색 결과를 구조화하여 제공

### Calculation Agent
- **기능**: 수학적 계산 및 통계 처리
- **지원 연산**: 기본 사칙연산, 거듭제곱, 삼각함수, 통계
- **활성화 조건**: 숫자와 연산자 패턴 감지

### Chat Agent
- **기능**: 자연스러운 대화 응답 생성
- **역할**: 다른 Agent들의 결과를 통합하여 최종 응답 생성
- **특징**: 감정 인식 및 컨텍스트 이해

## 🎨 웹 인터페이스 특징

### 실시간 Agent 상태 표시
- 각 Agent의 활성화/비활성화 상태
- 처리 중인 Agent의 실시간 애니메이션
- 완료된 작업의 결과 표시

### 대화 기록 시각화
- 사용자와 AI의 메시지 구분
- 사용된 Agent들 태그 표시
- 검색 결과와 계산 결과 별도 표시

### 반응형 디자인
- 데스크톱과 모바일 모두 지원
- 실시간 연결 상태 표시
- 직관적인 사용자 인터페이스

## 🔮 확장 가능성

### 새로운 Agent 추가
1. `agents/` 디렉토리에 새로운 Agent 클래스 생성
2. `AgentManager`에 등록
3. 웹 인터페이스에 상태 표시 추가

### API 연동
- Google Custom Search API
- Bing Web Search API
- OpenAI API 연동 가능

### 데이터베이스 연동
- PostgreSQL, MongoDB 등으로 메모리 확장
- 대화 기록 영구 저장

## 🐛 문제 해결

### 연결 오류
- Flask 서버가 실행 중인지 확인
- 포트 5000이 사용 가능한지 확인

### Agent 동작 안함
- 필요한 Python 패키지가 설치되었는지 확인
- 브라우저 콘솔에서 JavaScript 오류 확인

## 📝 라이선스

이 프로젝트는 교육 및 학습 목적으로 제작되었습니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**즐거운 AI Agent 체험을 위해 만들어졌습니다! 🚀**
