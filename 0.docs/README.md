# 강의 교안 도구 모음

2026 생성형 AI 에이전틱 웹 서비스 개발자 양성과정 교안 및 도구.

---

## 환경 설정

### 1. 가상환경 생성 및 패키지 설치

```bash
cd 0.docs/

# 가상환경 생성 (uv 사용)
uv venv .venv

# 패키지 설치
uv pip install -r requirements-pdf.txt      # PDF 생성 도구
uv pip install -r requirements-notion.txt   # Notion 동기화 도구

# Playwright 브라우저 설치 (PDF 생성 시 필요)
.venv/bin/playwright install chromium
```

### 2. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 아래 값을 입력:

| 변수 | 설명 | 발급 방법 |
|------|------|----------|
| `NOTION_API_KEY` | Notion Internal Integration 토큰 | [My Integrations](https://www.notion.so/my-integrations) 에서 생성 |
| `NOTION_PARENT_PAGE_ID` | 교안이 위치할 상위 페이지 ID | 페이지 URL 마지막 32자리 |

> Notion 페이지에서 `...` → **Connections** → Integration을 연결해야 API로 접근 가능합니다.

---

## PDF 핸드아웃 생성

### 개별 파일 PDF

```bash
# 단일 파일
.venv/bin/python generate_pdf.py 07_cloud/01_cloud_computing_fundamentals.md

# 모듈 전체
.venv/bin/python generate_pdf.py 07_cloud/

# 전체 모듈
.venv/bin/python generate_pdf.py --all
```

### 모듈별 통합 PDF 북 (타이틀 + 간지 포함)

```bash
# 특정 모듈
.venv/bin/python generate_pdf_book.py 07_cloud/

# 전체 모듈
.venv/bin/python generate_pdf_book.py --all
```

출력 위치: `pdf_output/` (개별), `pdf_output/books/` (통합)

---

## Notion 동기화

### 페이지 목록 조회

```bash
# 상위 페이지의 하위 목록
.venv/bin/python notion_sync.py list

# 특정 페이지의 하위 목록
.venv/bin/python notion_sync.py list --page-id <PAGE_ID>
```

### 워크스페이스 검색

```bash
.venv/bin/python notion_sync.py search "클라우드"
```

---

## 디렉토리 구조

```
0.docs/
├── 00_OT/                  # 오리엔테이션
├── 01_genai_intro/         # 생성형 AI 입문
├── 02_web_basics/          # 웹 기초
├── 03_python_webdev/       # Python 웹 개발
├── 04_database/            # 데이터베이스
├── 05_genai_advanced/      # 생성형 AI 심화
├── 06_genai_applied/       # 생성형 AI 응용
├── 07_cloud/               # 클라우드
├── 08_team_project/        # 팀 프로젝트
├── generate_pdf.py         # 개별 PDF 생성기
├── generate_pdf_book.py    # 통합 PDF 북 생성기
├── notion_sync.py          # Notion 동기화 도구
├── requirements-pdf.txt    # PDF 도구 의존성
├── requirements-notion.txt # Notion 도구 의존성
├── .env.example            # 환경변수 템플릿
└── .env                    # 환경변수 (git 제외)
```
