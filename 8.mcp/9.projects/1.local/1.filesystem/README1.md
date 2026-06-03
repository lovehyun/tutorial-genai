# 간단한 파일 관리 MCP 시스템

## 개요

AI가 로컬 파일 시스템에 접근하여 파일을 관리할 수 있는 간단한 MCP(Model Context Protocol) 시스템입니다. 강의용으로 제작되어 핵심 기능만 포함하고 있습니다.

## 파일 구조

```
simple-file-mcp/
├── server.py      # MCP 서버 (4개 도구)
├── client.py      # 간단한 클라이언트
└── files/         # 작업 디렉토리 (자동 생성)
```

---

## 서버 코드 (server.py)

```python
import os
import shutil
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# 작업 디렉토리 설정
WORK_DIR = Path("./files")
WORK_DIR.mkdir(exist_ok=True)

mcp = FastMCP("FileManager")

@mcp.tool()
def list_files() -> dict:
    """파일 목록을 조회합니다."""
    files = []
    for item in WORK_DIR.iterdir():
        files.append({
            "name": item.name,
            "type": "파일" if item.is_file() else "폴더",
            "size": item.stat().st_size if item.is_file() else None
        })
    return {"files": files, "count": len(files)}

@mcp.tool()
def read_file(filename: str) -> dict:
    """파일 내용을 읽습니다."""
    file_path = WORK_DIR / filename
    
    if not file_path.exists():
        return {"error": "파일이 없습니다"}
    
    try:
        content = file_path.read_text(encoding='utf-8')
        return {"filename": filename, "content": content}
    except:
        return {"error": "파일을 읽을 수 없습니다"}

@mcp.tool()
def rename_file(old_name: str, new_name: str) -> dict:
    """파일명을 변경합니다."""
    old_path = WORK_DIR / old_name
    new_path = WORK_DIR / new_name
    
    if not old_path.exists():
        return {"error": "원본 파일이 없습니다"}
    
    if new_path.exists():
        return {"error": "새 파일명이 이미 존재합니다"}
    
    old_path.rename(new_path)
    return {"message": f"{old_name} → {new_name} 변경 완료"}

@mcp.tool()
def copy_file(source: str, destination: str) -> dict:
    """파일을 복사합니다."""
    src_path = WORK_DIR / source
    dst_path = WORK_DIR / destination
    
    if not src_path.exists():
        return {"error": "원본 파일이 없습니다"}
    
    if dst_path.exists():
        return {"error": "대상 파일이 이미 존재합니다"}
    
    shutil.copy2(src_path, dst_path)
    return {"message": f"{source} → {destination} 복사 완료"}

if __name__ == "__main__":
    print("파일 관리 MCP 서버 시작")
    print(f"작업 폴더: {WORK_DIR.absolute()}")
    mcp.run()
```

---

## 클라이언트 코드 (client.py)

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json

async def main():
    # MCP 서버 연결
    server_params = StdioServerParameters(command="python", args=["server.py"])
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("파일 관리 MCP 클라이언트")
            print("=" * 40)
            
            while True:
                print("\n명령어:")
                print("1. 파일 목록")
                print("2. 파일 읽기") 
                print("3. 파일명 변경")
                print("4. 파일 복사")
                print("5. 종료")
                
                choice = input("\n선택: ").strip()
                
                if choice == "1":
                    # 파일 목록
                    result = await session.call_tool("list_files")
                    data = json.loads(result.content[0].text)
                    
                    print(f"\n파일 목록 ({data['count']}개)")
                    print("-" * 30)
                    for file in data['files']:
                        size = f"({file['size']} bytes)" if file['size'] else ""
                        print(f"{file['type']}: {file['name']} {size}")
                
                elif choice == "2":
                    # 파일 읽기
                    filename = input("파일명: ")
                    result = await session.call_tool("read_file", {"filename": filename})
                    data = json.loads(result.content[0].text)
                    
                    if "error" in data:
                        print(f"오류: {data['error']}")
                    else:
                        print(f"\n{data['filename']} 내용:")
                        print("-" * 30)
                        print(data['content'])
                
                elif choice == "3":
                    # 파일명 변경
                    old_name = input("현재 파일명: ")
                    new_name = input("새 파일명: ")
                    result = await session.call_tool("rename_file", {
                        "old_name": old_name, 
                        "new_name": new_name
                    })
                    data = json.loads(result.content[0].text)
                    
                    if "error" in data:
                        print(f"오류: {data['error']}")
                    else:
                        print(f"완료: {data['message']}")
                
                elif choice == "4":
                    # 파일 복사
                    source = input("원본 파일명: ")
                    destination = input("복사할 파일명: ")
                    result = await session.call_tool("copy_file", {
                        "source": source,
                        "destination": destination
                    })
                    data = json.loads(result.content[0].text)
                    
                    if "error" in data:
                        print(f"오류: {data['error']}")
                    else:
                        print(f"완료: {data['message']}")
                
                elif choice == "5":
                    print("종료합니다")
                    break
                
                else:
                    print("잘못된 선택입니다")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 설치 및 실행

### 1. 사전 준비
```bash
pip install mcp
```

### 2. 테스트 파일 생성
```bash
mkdir files
echo "안녕하세요 MCP!" > files/test.txt
echo "파일 관리 테스트" > files/sample.txt
echo "Hello World" > files/hello.txt
```

### 3. 서버 실행
```bash
python server.py
```

실행 결과:
```
파일 관리 MCP 서버 시작
작업 폴더: /path/to/files
INFO:     Started server process [12345]
```

### 4. 클라이언트 실행 (새 터미널)
```bash
python client.py
```

---

## 사용 예시

### 시작 화면
```
파일 관리 MCP 클라이언트
========================================

명령어:
1. 파일 목록
2. 파일 읽기
3. 파일명 변경
4. 파일 복사
5. 종료

선택:
```

### 1. 파일 목록 조회
```
선택: 1

파일 목록 (3개)
------------------------------
파일: test.txt (19 bytes)
파일: sample.txt (21 bytes)
파일: hello.txt (11 bytes)
```

### 2. 파일 읽기
```
선택: 2
파일명: test.txt

test.txt 내용:
------------------------------
안녕하세요 MCP!
```

### 3. 파일명 변경
```
선택: 3
현재 파일명: test.txt
새 파일명: greeting.txt
완료: test.txt → greeting.txt 변경 완료
```

### 4. 파일 복사
```
선택: 4
원본 파일명: greeting.txt
복사할 파일명: backup.txt
완료: greeting.txt → backup.txt 복사 완료
```

### 5. 오류 처리
```
선택: 2
파일명: notfound.txt
오류: 파일이 없습니다

선택: 4
원본 파일명: hello.txt
복사할 파일명: hello.txt
오류: 대상 파일이 이미 존재합니다
```

---

## 제공되는 도구

### 1. list_files()
- **기능**: 작업 디렉토리의 파일 목록 조회
- **매개변수**: 없음
- **반환**: 파일 정보 목록과 파일 개수

### 2. read_file(filename)
- **기능**: 지정된 파일의 내용 읽기
- **매개변수**: `filename` (문자열) - 읽을 파일명
- **반환**: 파일 내용 또는 오류 메시지

### 3. rename_file(old_name, new_name)
- **기능**: 파일명 변경
- **매개변수**: 
  - `old_name` (문자열) - 현재 파일명
  - `new_name` (문자열) - 새 파일명
- **반환**: 성공 메시지 또는 오류 메시지

### 4. copy_file(source, destination)
- **기능**: 파일 복사
- **매개변수**:
  - `source` (문자열) - 원본 파일명
  - `destination` (문자열) - 복사할 파일명
- **반환**: 성공 메시지 또는 오류 메시지

---

## 라이브 코딩 가이드

### 1단계: 기본 MCP 서버 (5분)
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("FileManager")

@mcp.tool()
def list_files() -> dict:
    return {"files": ["test.txt", "sample.txt"]}

if __name__ == "__main__":
    mcp.run()
```

### 2단계: 실제 파일 시스템 연동 (5분)
```python
from pathlib import Path

WORK_DIR = Path("./files")
WORK_DIR.mkdir(exist_ok=True)

@mcp.tool()
def list_files() -> dict:
    files = []
    for item in WORK_DIR.iterdir():
        files.append({"name": item.name, "type": "파일"})
    return {"files": files}

@mcp.tool()
def read_file(filename: str) -> dict:
    file_path = WORK_DIR / filename
    content = file_path.read_text()
    return {"content": content}
```

### 3단계: 파일 조작 기능 추가 (10분)
- `rename_file` 함수 구현
- `copy_file` 함수 구현
- 기본적인 오류 처리 추가

### 4단계: 클라이언트 연결 테스트 (5분)
- 간단한 메뉴 방식 클라이언트 구현
- MCP 도구 호출 시연

---

## 주요 특징

### 보안성
- 지정된 `files` 디렉토리 내에서만 작업
- 상위 디렉토리 접근 불가

### 단순성
- 4개 핵심 기능만 제공
- 복잡한 설정 없이 바로 실행 가능

### 확장성
- 새로운 도구 추가 시 `@mcp.tool()` 데코레이터만 사용
- 타입 힌트로 자동 문서화

### 교육성
- MCP 개념 이해에 최적화
- 라이브 코딩에 적합한 분량

---

## 문제 해결

### 서버 실행 오류
```bash
# mcp 패키지 설치 확인
pip install mcp

# Python 버전 확인 (3.8 이상 필요)
python --version
```

### 파일 접근 오류
```bash
# files 디렉토리 권한 확인
ls -la files/

# 테스트 파일 재생성
echo "테스트 내용" > files/test.txt
```

### 클라이언트 연결 오류
- 서버가 먼저 실행되고 있는지 확인
- 터미널을 분리해서 서버와 클라이언트 각각 실행

이 시스템은 MCP의 핵심 개념을 이해하고 실습하기에 최적화된 간단한 파일 관리 시스템입니다.
