# 자연어 파일 관리 챗봇 설치 및 사용 가이드

## 설치

### 1. 기본 설치 (패턴 매칭 모드)
```bash
# Python 파일만 있으면 바로 실행 가능
python nlp_file_manager.py
```

### 2. AI 모드 설치 (OpenAI API 사용)
```bash
# 필요한 라이브러리 설치 (OpenAI 1.0+)
pip install openai>=1.0.0 python-dotenv

# .env 파일 생성 (프로젝트 폴더에)
echo OPENAI_API_KEY=your_api_key_here > .env

# 또는 환경변수로 API 키 설정
set OPENAI_API_KEY=your_api_key_here

python nlp_file_manager.py
```

### 3. .env 파일 사용법
프로젝트 폴더에 `.env` 파일을 만들고:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
WORK_DIRECTORY=C:\WORK\프로젝트
```

## 사용 예시

### 기본 명령들
```
[Documents] > 현재 폴더에 있는 파일들을 보여줘
  파일: report.hwp (2,048 bytes)
  파일: data.xlsx (15,360 bytes)
  폴더: images/

[Documents] > hwp 확장자 파일을 찾아줘
  파일: report.hwp
  파일: memo.hwp

[Documents] > 1주차 파일을 12주차까지 복사해줘
  원본 파일: report_1주차.hwp
    파일 복사 완료: report_1주차.hwp -> report_2주차.hwp
    파일 복사 완료: report_1주차.hwp -> report_3주차.hwp
    ...

[Documents] > backup이라는 폴더를 만들어줘
  폴더 생성 완료: backup

[Documents] > backup 폴더로 들어가자
  디렉토리 변경: C:\Users\User\Documents\backup

[backup] > 상위 폴더로 가자
  디렉토리 변경: C:\Users\User\Documents
```

### 자연어 명령 예시

**파일 목록 조회:**
- "현재 폴더 파일들 보여줘"
- "여기 뭐가 있지?"
- "파일 목록"
- "ls"

**파일 검색:**
- "hwp 파일 찾아줘"
- "보고서라는 이름이 들어간 파일 있나?"
- "김철수 검색해줘"

**파일 복사:**
- "1주차 파일을 12주차까지 복사해줘"
- "report.txt를 backup.txt로 복사해"

**디렉토리 이동:**
- "Documents 폴더로 이동해"
- "상위 폴더로 가자"
- "cd .."

**폴더 생성:**
- "새폴더라는 디렉토리 만들어줘"
- "backup 폴더 생성해"

**파일 삭제:**
- "temp.txt 파일 삭제해줘"
- "불필요한 파일들 지워"

## 두 가지 모드

### 1. 기본 모드 (패턴 매칭)
- OpenAI API 없이 동작
- 미리 정의된 패턴으로 명령 인식
- 빠르고 무료
- 제한적인 자연어 이해

### 2. AI 모드 (OpenAI API)
- 진짜 자연어 이해
- 복잡한 명령도 처리 가능
- 컨텍스트 이해
- API 비용 발생

## 장점

1. **직관적**: "1주차 파일을 12주차까지 복사해줘" 같은 자연어 명령
2. **안전**: 현재 디렉토리 내에서만 작업
3. **확장가능**: 새로운 명령 쉽게 추가
4. **유연**: AI 모드와 기본 모드 선택 가능

## 제한사항

- 현재 디렉토리 기반 작업만 지원
- 복잡한 배치 작업은 제한적
- AI 모드는 인터넷 연결 필요

이제 정말 자연어로 파일 관리를 할 수 있습니다!
