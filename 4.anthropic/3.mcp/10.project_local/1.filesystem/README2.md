# 파일 시스템 MCP 사용 가이드

## 개요

이 가이드는 로컬 파일 시스템에 접근할 수 있는 MCP (Model Context Protocol) 서버와 클라이언트의 사용법을 설명합니다. 안전한 파일 작업을 위해 특정 workspace 디렉토리 내에서만 동작합니다.

## 보안 특징

- **샌드박스 환경**: `./workspace` 디렉토리 내에서만 작업
- **디렉토리 탈출 방지**: `../` 등을 이용한 상위 디렉토리 접근 차단
- **파일 크기 제한**: 10MB 이상의 대용량 파일 읽기 제한
- **안전한 인코딩**: UTF-8 기본, 자동 인코딩 감지

---

## 설치 및 실행

### 1. 서버 실행
```bash
python server/server.py
```

실행 시 `workspace` 디렉토리가 자동으로 생성됩니다.

### 2. 클라이언트 실행
```bash
python client/client.py
```

실행 모드 선택:
- **1. 자동 데모**: 파일 시스템 기능 자동 테스트
- **2. 대화형 모드**: 명령어로 파일 시스템 조작

---

## 사용 가능한 도구

### 1. list_files
**설명**: 디렉토리 내용 조회

**매개변수**:
- `directory` (문자열, 선택): 조회할 디렉토리 경로 (기본값: ".")

**예시**:
```python
result = await client.list_files(".")
result = await client.list_files("subfolder")
```

**응답**:
```json
{
  "directory": ".",
  "file_count": 3,
  "directory_count": 1,
  "files": [
    {
      "name": "test.txt",
      "path": "test.txt",
      "type": "file",
      "size": 1024,
      "modified": "2025-07-21T10:30:45",
      "mime_type": "text/plain"
    }
  ]
}
```

### 2. read_file
**설명**: 파일 내용 읽기

**매개변수**:
- `file_path` (문자열, 필수): 읽을 파일 경로
- `encoding` (문자열, 선택): 문자 인코딩 (기본값: "utf-8")

**예시**:
```python
result = await client.read_file("test.txt")
result = await client.read_file("korean.txt", encoding="cp949")
```

### 3. write_file
**설명**: 파일에 내용 쓰기

**매개변수**:
- `file_path` (문자열, 필수): 저장할 파일 경로
- `content` (문자열, 필수): 파일 내용
- `encoding` (문자열, 선택): 문자 인코딩 (기본값: "utf-8")
- `overwrite` (불린, 선택): 기존 파일 덮어쓰기 허용 (기본값: false)

**예시**:
```python
await client.write_file("new.txt", "Hello World!", overwrite=True)
```

### 4. create_directory
**설명**: 새 디렉토리 생성

**매개변수**:
- `directory_path` (문자열, 필수): 생성할 디렉토리 경로

**예시**:
```python
await client.create_directory("new_folder")
await client.create_directory("parent/child")  # 중첩 디렉토리
```

### 5. delete_file
**설명**: 파일 또는 디렉토리 삭제

**매개변수**:
- `file_path` (문자열, 필수): 삭제할 파일/디렉토리 경로
- `force` (불린, 선택): 디렉토리 강제 삭제 (기본값: false)

**예시**:
```python
await client.delete_file("test.txt")
await client.delete_file("old_folder", force=True)
```

### 6. search_files
**설명**: 파일 검색 (와일드카드 지원)

**매개변수**:
- `pattern` (문자열, 필수): 검색 패턴 (*, ? 와일드카드 사용 가능)
- `directory` (문자열, 선택): 검색 시작 디렉토리 (기본값: ".")
- `file_type` (문자열, 선택): "all", "files", "directories" (기본값: "all")

**예시**:
```python
await client.search_files("*.txt")        # 모든 txt 파일
await client.search_files("test*")        # test로 시작하는 모든 파일
await client.search_files("*", file_type="directories")  # 모든 디렉토리
```

### 7. get_file_info
**설명**: 파일/디렉토리 상세 정보 조회

**매개변수**:
- `file_path` (문자열, 필수): 정보를 조회할 파일/디렉토리 경로

**예시**:
```python
info = await client.get_file_info("test.txt")
```

**응답**:
```json
{
  "path": "test.txt",
  "name": "test.txt",
  "type": "file",
  "size": 1024,
  "created": "2025-07-21T09:30:45",
  "modified": "2025-07-21T10:30:45",
  "permissions": {
    "readable": true,
    "writable": true,
    "executable": false
  },
  "mime_type": "text/plain",
  "line_count": 15,
  "encoding": "utf-8"
}
```

---

## 대화형 모드 명령어

### 기본 명령어

```bash
ls [directory]              # 디렉토리 내용 조회
cat <file>                  # 파일 내용 보기
write <file> <content>      # 파일 쓰기
write <file> multi          # 여러 줄 입력 모드
mkdir <directory>           # 디렉토리 생성
rm <file> [force]          # 파일/디렉토리 삭제
find <pattern>             # 파일 검색
info <file>                # 파일 정보 조회
quit                       # 종료
```

### 사용 예시

```bash
fs> ls
📁 documents (N/A bytes)
📄 readme.txt (1024 bytes)
📄 config.json (512 bytes)

fs> cat readme.txt
파일: readme.txt (1024 bytes)
----------------------------------------
이것은 테스트 파일입니다.
MCP를 통해 파일 시스템에 접근하고 있습니다.

fs> write hello.txt Hello World!
파일 저장 완료: 파일이 성공적으로 저장되었습니다.

fs> write long.txt multi
여러 줄 입력 모드 (빈 줄로 종료):
첫 번째 줄
두 번째 줄
세 번째 줄

파일 저장 완료: 파일이 성공적으로 저장되었습니다.

fs> find *.txt
검색 결과: '*.txt' - 3개 발견
----------------------------------------
📄 readme.txt (1024 bytes)
📄 hello.txt (12 bytes)
📄 long.txt (36 bytes)

fs> info hello.txt
파일 정보: hello.txt
----------------------------------------
경로: hello.txt
타입: file
크기: 12 bytes
생성: 2025-07-21T10:30:45
수정: 2025-07-21T10:30:45
권한: R(True) W(True) X(False)
줄 수: 1
MIME 타입: text/plain
```

---

## 프로그래밍 예제

### 기본 파일 작업
```python
import asyncio
from filesystem_client import FileSystemMCPClient

async def basic_file_operations():
    client = FileSystemMCPClient()
    await client.connect()
    
    try:
        # 파일 쓰기
        await client.write_file("sample.txt", "Hello MCP!", overwrite=True)
        
        # 파일 읽기
        content = await client.read_file("sample.txt")
        print(f"파일 내용: {content['content']}")
        
        # 디렉토리 생성
        await client.create_directory("data")
        
        # 파일 검색
        results = await client.search_files("*.txt")
        print(f"txt 파일 {results['found_count']}개 발견")
        
    finally:
        await client.close()

asyncio.run(basic_file_operations())
```

### 설정 파일 관리
```python
import json

async def config_manager():
    client = FileSystemMCPClient()
    await client.connect()
    
    try:
        # 설정 생성
        config = {
            "server_url": "http://localhost:8000",
            "timeout": 30,
            "debug": True
        }
        
        # JSON 파일로 저장
        config_json = json.dumps(config, indent=2, ensure_ascii=False)
        await client.write_file("config/app.json", config_json, overwrite=True)
        
        # 설정 읽기
        result = await client.read_file("config/app.json")
        loaded_config = json.loads(result['content'])
        print(f"로드된 설정: {loaded_config}")
        
    finally:
        await client.close()
```

### 로그 파일 처리
```python
async def log_processor():
    client = FileSystemMCPClient()
    await client.connect()
    
    try:
        # 로그 디렉토리 생성
        await client.create_directory("logs")
        
        # 로그 파일 생성
        log_content = f"""[2025-07-21 10:30:45] INFO: 애플리케이션 시작
[2025-07-21 10:30:46] DEBUG: 설정 로드 완료
[2025-07-21 10:30:47] INFO: 서버 연결 성공
[2025-07-21 10:30:48] WARNING: 메모리 사용량 높음
"""
        
        await client.write_file("logs/app.log", log_content, overwrite=True)
        
        # 로그 파일 검색
        log_files = await client.search_files("*.log", directory="logs")
        print(f"로그 파일 {log_files['found_count']}개 발견")
        
        # 로그 파일 정보
        for log_file in log_files['results']:
            info = await client.get_file_info(log_file['path'])
            print(f"로그: {info['name']} ({info['size']} bytes, {info.get('line_count', 'N/A')} 줄)")
        
    finally:
        await client.close()
```

---

## 오류 처리

모든 MCP 도구는 오류 발생 시 다음 형식으로 응답합니다:

```json
{
  "error": "오류 메시지"
}
```

### 일반적인 오류들

- **"디렉토리 탈출 시도가 감지되었습니다"**: `../` 등으로 workspace 밖에 접근 시도
- **"파일이 존재하지 않습니다"**: 없는 파일에 접근
- **"파일이 이미 존재합니다"**: overwrite=false 상태에서 기존 파일에 쓰기 시도
- **"파일이 너무 큽니다"**: 10MB 이상의 파일 읽기 시도
- **"텍스트 파일을 읽을 수 없습니다"**: 인코딩 문제로 파일 읽기 실패

---

## 보안 고려사항

1. **작업 디렉토리 제한**: `./workspace` 디렉토리 밖으로 접근 불가
2. **파일 크기 제한**: 대용량 파일 읽기 방지
3. **바이너리 파일 보호**: 실행 파일 등의 내용은 읽기 제한
4. **안전한 경로 처리**: 디렉토리 탈출 공격 방지

이 시스템을 통해 AI 에이전트가 안전하게 로컬 파일 시스템과 상호작용할 수 있습니다.
