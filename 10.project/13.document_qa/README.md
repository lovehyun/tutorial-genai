# 문서 QA 웹 애플리케이션

PDF/TXT 문서를 업로드하고 내용에 대해 대화형으로 질문할 수 있는 RAG 기반 웹앱입니다.

## 기능

- PDF, TXT 파일 업로드 (드래그 앤 드롭 지원)
- 문서 자동 청킹 및 ChromaDB 임베딩 저장
- SSE 스트리밍 기반 실시간 QA 응답
- 참고 문서 소스 표시
- 업로드 문서 관리 (목록, 삭제)

## 기술 스택

- **Backend**: Flask, LangChain, OpenAI API
- **Vector DB**: ChromaDB (영구 저장)
- **Frontend**: 순수 HTML/CSS/JS (외부 라이브러리 없음)

## 설치 및 실행

```bash
pip install -r requirements.txt

# .env 파일에 OPENAI_API_KEY 설정
python app.py

# 브라우저에서 http://localhost:5000 접속
```

## 프로젝트 구조

```
9.document_qa/
├── app.py              # Flask 서버 + RAG 로직
├── templates/
│   └── index.html      # 프론트엔드 UI
├── requirements.txt    # 의존성
├── uploads/            # 업로드된 파일 (자동 생성)
└── chroma_db/          # ChromaDB 저장소 (자동 생성)
```
