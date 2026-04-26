# 파일 처리, 로깅, 환경변수/설정 관리

> 프로그램이 데이터를 기억하고, 스스로를 진단하고, 환경에 적응하는 방법을 배워봅니다.
> 파일은 프로그램의 "일기장", 로깅은 "건강 검진표", 환경변수는 "상황별 의상"과 같습니다.

---

## 1. 파일 I/O 기초

### 왜 파일 처리가 중요한가?

프로그램은 실행되는 동안 메모리에 데이터를 저장합니다. 하지만 프로그램이 종료되면 메모리의 데이터는 사라집니다. 이를 **휘발성(volatile)**이라고 합니다. 파일은 데이터를 **영구적으로 저장**할 수 있는 가장 기본적인 방법입니다.

실생활에 비유하면, 메모리는 칠판에 적는 메모이고, 파일은 노트에 적는 기록입니다. 칠판은 지우면 사라지지만, 노트는 책장에 꽂아두면 언제든 다시 볼 수 있습니다.

### open() 함수와 파일 모드

Python에서 파일을 다루려면 먼저 `open()` 함수로 파일을 열어야 합니다.

```python
# 기본 문법
파일객체 = open("파일경로", "모드", encoding="인코딩")
```

```mermaid
graph LR
    A["open() 파일 모드"]
    B["r (read): 읽기 전용, 파일 없으면 에러"]
    C["w (write): 쓰기 전용, 파일 없으면 생성, 기존 내용 삭제"]
    D["a (append): 추가 모드, 파일 없으면 생성, 기존 내용 유지"]
    E["rb / wb: 바이너리 모드, 이미지/PDF 등"]
    F["r+ / w+: 읽기+쓰기 동시 처리"]

    A --> B
    A --> C
    A --> D
    A --> E
    A --> F

    style A fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style B fill:#0984e3,stroke:#74b9ff,color:#fff
    style C fill:#e17055,stroke:#d63031,color:#fff
    style D fill:#55efc4,stroke:#00b894,color:#2d3436
    style E fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style F fill:#a29bfe,stroke:#6c5ce7,color:#fff
```

| 모드 | 설명 | 파일 없을 때 | 기존 내용 |
|------|------|-------------|----------|
| `r` | 읽기 전용 | FileNotFoundError | 유지 |
| `w` | 쓰기 전용 | 새로 생성 | **삭제** |
| `a` | 추가 모드 | 새로 생성 | 유지 (끝에 추가) |
| `rb` | 바이너리 읽기 | FileNotFoundError | 유지 |
| `wb` | 바이너리 쓰기 | 새로 생성 | **삭제** |

### with 문 (컨텍스트 매니저)

파일을 열면 반드시 닫아야 합니다. `with` 문을 사용하면 블록이 끝날 때 **자동으로 파일이 닫힙니다**.

```python
# 나쁜 방법: 수동으로 닫기 (까먹기 쉬움)
f = open("data.txt", "r")
content = f.read()
f.close()  # 이걸 잊으면 문제 발생!

# 좋은 방법: with 문 사용 (자동으로 닫힘)
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()
# 여기서 f는 이미 닫혀 있음
```

> **핵심 포인트:** `with` 문은 "자동 문 닫기 장치"와 같습니다. 파일을 열 때는 **항상** `with` 문을 사용하는 습관을 들이세요.

### 텍스트 파일 읽기/쓰기

```python
# 파일 쓰기
with open("greeting.txt", "w", encoding="utf-8") as f:
    f.write("안녕하세요!\n")
    f.write("Python 파일 처리를 배우고 있습니다.\n")

# 파일 전체 읽기
with open("greeting.txt", "r", encoding="utf-8") as f:
    content = f.read()  # 전체 내용을 문자열로

# 한 줄씩 읽기 (대용량 파일에 적합)
with open("greeting.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())  # strip()으로 줄바꿈 제거

# 모든 줄을 리스트로 읽기
with open("greeting.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()  # ["안녕하세요!\n", "Python 파일 처리를...\n"]
```

### 인코딩 (UTF-8)

한글이 포함된 파일을 다룰 때는 반드시 `encoding="utf-8"`을 지정해야 합니다. 지정하지 않으면 운영체제 기본 인코딩이 사용되어 **한글이 깨질 수 있습니다**.

```python
# Windows: cp949, macOS/Linux: utf-8 -- OS마다 기본값이 다름
# 안전한 방법: 항상 UTF-8 명시
with open("한글파일.txt", "w", encoding="utf-8") as f:
    f.write("한글도 안전하게 저장됩니다.")
```

---

## 2. CSV와 JSON 파일 처리

### CSV 파일 처리

CSV(Comma-Separated Values)는 데이터를 쉼표로 구분하여 저장하는 형식입니다. 엑셀과 호환되기 때문에 실무에서 매우 자주 사용됩니다.

```python
import csv

# CSV 파일 쓰기
with open("students.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["이름", "나이", "점수"])  # 헤더
    writer.writerow(["김철수", 25, 95])
    writer.writerow(["이영희", 23, 88])

# CSV 파일 읽기
with open("students.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)  # ['이름', '나이', '점수'], ['김철수', '25', '95'], ...
```

### DictReader와 DictWriter

헤더가 있는 CSV 파일은 `DictReader`와 `DictWriter`를 사용하면 딕셔너리 형태로 편리하게 처리할 수 있습니다.

```python
import csv

# DictWriter로 쓰기
fieldnames = ["이름", "나이", "점수"]
with open("students.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({"이름": "김철수", "나이": 25, "점수": 95})

# DictReader로 읽기 (각 행이 딕셔너리)
with open("students.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['이름']}님의 점수: {row['점수']}")
```

### JSON 파일 처리

JSON은 05장에서 API 데이터 포맷으로 이미 학습했습니다. 여기서는 **파일 I/O 관점**에서 다시 살펴봅니다.

```python
import json

# 딕셔너리를 JSON 파일로 저장
data = {
    "서비스명": "AI 학습 도우미",
    "버전": "1.0.0",
    "사용자": [
        {"이름": "김철수", "역할": "관리자"},
        {"이름": "이영희", "역할": "사용자"}
    ]
}

with open("config.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# JSON 파일 읽기
with open("config.json", "r", encoding="utf-8") as f:
    loaded_data = json.load(f)
    print(loaded_data["서비스명"])  # "AI 학습 도우미"
```

### 실무 예: 데이터 파일 읽기 -> API 응답

```python
from fastapi import FastAPI
import csv

app = FastAPI()

@app.get("/students")
def get_students():
    """CSV 파일의 학생 데이터를 API로 제공"""
    students = []
    with open("students.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            students.append(row)
    return {"students": students, "total": len(students)}
```

> **핵심 포인트:** CSV는 표 형태 데이터에, JSON은 계층 구조 데이터에 적합합니다. 실무에서는 데이터 파일을 읽어 API 응답으로 변환하는 패턴이 매우 자주 사용됩니다.

---

## 3. FastAPI에서 파일 업로드/다운로드

### UploadFile 클래스

FastAPI는 `UploadFile` 클래스를 통해 파일 업로드를 간편하게 처리합니다. `UploadFile`은 파일 전체를 메모리에 올리지 않고 **스트리밍 방식**으로 처리하기 때문에 대용량 파일에도 적합합니다.

```mermaid
flowchart TB
    A["클라이언트<br/>파일 선택"] --> B["HTTP POST<br/>multipart/form-data"]
    B --> C["FastAPI 서버<br/>UploadFile 수신"]
    C --> D{"파일 검증<br/>크기/타입 확인"}
    D -->|통과| E["파일 저장<br/>서버 디스크"]
    D -->|실패| F["에러 응답<br/>400 Bad Request"]
    E --> G["성공 응답<br/>파일 정보 반환"]

    style A fill:#0984e3,stroke:#74b9ff,color:#fff
    style B fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style C fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style D fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style E fill:#55efc4,stroke:#00b894,color:#2d3436
    style F fill:#e17055,stroke:#d63031,color:#fff
    style G fill:#55efc4,stroke:#00b894,color:#2d3436
```

### 파일 업로드/다운로드 엔드포인트

```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os, shutil

app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """단일 파일 업로드"""
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "content_type": file.content_type}

@app.get("/download/{filename}")
async def download_file(filename: str):
    """파일 다운로드"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
    return FileResponse(path=file_path, filename=filename)
```

### 다중 파일 업로드

```python
from typing import List

@app.post("/upload-multiple")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """여러 파일 동시 업로드"""
    results = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        results.append({"filename": file.filename, "size": os.path.getsize(file_path)})
    return {"uploaded_files": results, "count": len(results)}
```

### 파일 크기 제한과 타입 검증

```python
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@app.post("/upload-safe")
async def upload_safe(file: UploadFile = File(...)):
    """파일 크기와 타입을 검증하는 안전한 업로드"""
    # 확장자 검증
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"허용되지 않는 파일 형식: {ext}")

    # 파일 크기 검증
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기가 10MB를 초과합니다")

    # 검증 통과 후 저장
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    return {"filename": file.filename, "size": len(content)}
```

> **핵심 포인트:** 파일 업로드 시 반드시 **확장자 검증**과 **크기 제한**을 구현해야 합니다. 악의적인 파일 업로드는 서버 보안에 심각한 위협이 될 수 있습니다.

---

## 4. 로깅(Logging) 기초

### print() vs logging

개발 중에 `print()`로 디버깅하는 것은 자연스러운 일입니다. 하지만 운영 환경에서는 `print()`만으로는 한계가 있습니다. `print()`는 "메모지에 적는 것"이고 `logging`은 "체계적인 업무 일지를 작성하는 것"입니다.

| 항목 | print() | logging |
|------|---------|---------|
| 출력 대상 | 콘솔만 | 콘솔, 파일, 외부 서비스 등 다양 |
| 레벨 구분 | 없음 | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| 시간 정보 | 없음 | 자동 기록 가능 |
| 포맷 지정 | 수동 | 자동 포맷터 |
| 운영 환경 | 부적합 | 적합 |
| 성능 | 항상 실행 | 레벨별 필터링 가능 |

### logging 모듈 기본 사용

```python
import logging

logging.basicConfig(level=logging.DEBUG)

logging.debug("이것은 디버그 메시지입니다")      # 개발 중 상세 정보
logging.info("서버가 시작되었습니다")            # 일반적인 정보
logging.warning("디스크 공간이 부족합니다")       # 경고
logging.error("데이터베이스 연결에 실패했습니다")  # 에러
logging.critical("시스템이 다운되었습니다!")       # 치명적 오류
```

### 로그 레벨

로그 레벨은 메시지의 심각도를 나타냅니다. 레벨을 설정하면 해당 레벨 이상의 메시지만 출력됩니다.

| 레벨 | 숫자 값 | 용도 | 사용 예시 |
|------|--------|------|----------|
| `DEBUG` | 10 | 개발 중 상세 디버깅 | 변수 값 확인, 함수 호출 추적 |
| `INFO` | 20 | 일반적인 동작 확인 | 서버 시작, 사용자 로그인 |
| `WARNING` | 30 | 잠재적 문제 경고 | 디스크 부족, 재시도 발생 |
| `ERROR` | 40 | 에러 발생 | DB 연결 실패, API 호출 실패 |
| `CRITICAL` | 50 | 치명적 시스템 장애 | 서비스 중단, 데이터 손실 |

```mermaid
graph LR
    A["DEBUG (10)<br/>가장 상세"]
    B["INFO (20)<br/>일반 정보"]
    C["WARNING (30)<br/>주의 필요"]
    D["ERROR (40)<br/>에러 발생"]
    E["CRITICAL (50)<br/>치명적 장애"]

    A --> B --> C --> D --> E

    style A fill:#dfe6e9,stroke:#b2bec3,color:#2d3436
    style B fill:#74b9ff,stroke:#0984e3,color:#2d3436
    style C fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style D fill:#e17055,stroke:#d63031,color:#fff
    style E fill:#d63031,stroke:#c0392b,color:#fff
```

### 로그 포맷 설정

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logging.info("사용자가 로그인했습니다")
# 출력: 2024-01-15 14:30:00 - root - INFO - 사용자가 로그인했습니다
```

| 포맷 코드 | 설명 | 예시 |
|-----------|------|------|
| `%(asctime)s` | 로그 시간 | 2024-01-15 14:30:00 |
| `%(name)s` | 로거 이름 | root, myapp |
| `%(levelname)s` | 로그 레벨 | INFO, ERROR |
| `%(message)s` | 로그 메시지 | 사용자가 로그인했습니다 |
| `%(filename)s` | 파일 이름 | main.py |
| `%(lineno)d` | 줄 번호 | 42 |

---

## 5. 로깅 심화

### 핸들러 (Handler)

핸들러는 로그 메시지를 **어디로 보낼지** 결정합니다. 하나의 로거에 여러 핸들러를 연결할 수 있습니다.

```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)

# 콘솔 핸들러 (화면 출력)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 파일 핸들러 (파일 저장)
file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

# 회전 파일 핸들러 (파일 크기 자동 관리)
rotating_handler = RotatingFileHandler(
    "app_rotating.log",
    maxBytes=5*1024*1024,  # 5MB마다 새 파일 생성
    backupCount=3,          # 최대 3개 백업 유지
    encoding="utf-8"
)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(rotating_handler)
```

### 포매터 (Formatter)

포매터는 로그 메시지의 **출력 형식**을 결정합니다. 핸들러마다 다른 포매터를 지정할 수 있습니다.

```python
# 콘솔용 간결한 포맷
console_fmt = logging.Formatter("%(levelname)s: %(message)s")
console_handler.setFormatter(console_fmt)

# 파일용 상세 포맷
file_fmt = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s"
)
file_handler.setFormatter(file_fmt)
```

### 로거 계층 구조

Python의 로거는 점(`.`)으로 구분된 **계층 구조**를 가집니다. 자식 로거에서 처리하지 않은 로그는 부모 로거로 전파됩니다.

```mermaid
graph TD
    ROOT["root 로거<br/>최상위 로거<br/>logging.getLogger()"]
    APP["myapp 로거<br/>애플리케이션 로거<br/>logging.getLogger('myapp')"]
    API["myapp.api 로거<br/>API 모듈 로거"]
    DB["myapp.db 로거<br/>데이터베이스 모듈 로거"]
    AUTH["myapp.api.auth 로거<br/>인증 모듈 로거"]

    ROOT --> APP
    APP --> API
    APP --> DB
    API --> AUTH

    style ROOT fill:#e17055,stroke:#d63031,color:#fff
    style APP fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style API fill:#0984e3,stroke:#74b9ff,color:#fff
    style DB fill:#0984e3,stroke:#74b9ff,color:#fff
    style AUTH fill:#55efc4,stroke:#00b894,color:#2d3436
```

```python
# 계층 구조 활용 예시
app_logger = logging.getLogger("myapp")      # myapp
api_logger = logging.getLogger("myapp.api")  # myapp.api

# myapp.api 로거의 로그는 myapp -> root 순으로 전파
api_logger.info("API 요청 처리 중")
```

### 로깅 설정 (dictConfig)

실전에서는 `dictConfig`를 사용하여 로깅 설정을 **딕셔너리**로 관리합니다.

```python
import logging, logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler", "formatter": "default", "level": "INFO"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed", "filename": "logs/app.log",
            "maxBytes": 10485760, "backupCount": 5, "encoding": "utf-8", "level": "DEBUG"
        }
    },
    "loggers": {
        "myapp": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False}
    },
    "root": {"handlers": ["console"], "level": "WARNING"}
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("myapp")
```

> **핵심 포인트:** `dictConfig`는 로깅 설정의 "청사진"입니다. 포매터, 핸들러, 로거를 한 곳에서 선언적으로 관리할 수 있어 대규모 프로젝트에 적합합니다.

---

## 6. FastAPI 로깅 설정

### uvicorn 로깅 구조

FastAPI 애플리케이션은 uvicorn이라는 ASGI 서버 위에서 실행됩니다. uvicorn은 자체 로깅 시스템을 가지고 있으므로, FastAPI 로깅을 설정할 때는 이 구조를 이해해야 합니다.

```python
# uvicorn의 기본 로거들
# uvicorn         - uvicorn 서버 자체 로그
# uvicorn.access  - HTTP 접근 로그 (요청/응답)
# uvicorn.error   - 에러 로그
```

### 커스텀 로깅이 적용된 FastAPI 앱

```python
import logging
import logging.config
from fastapi import FastAPI

logging.config.dictConfig(LOGGING_CONFIG)  # 5장의 dictConfig 재사용
logger = logging.getLogger("myapp")

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    logger.info(f"사용자 조회 요청: user_id={user_id}")
    return {"user_id": user_id, "name": "김철수"}
```

### 요청/응답 로깅 미들웨어

모든 HTTP 요청과 응답을 자동으로 로깅하는 미들웨어를 만들어봅니다.

```python
import time
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """모든 요청/응답을 자동으로 로깅하는 미들웨어"""
    start_time = time.time()
    logger.info(f"요청 시작: {request.method} {request.url.path}")

    response = await call_next(request)
    duration = time.time() - start_time

    logger.info(
        f"요청 완료: {request.method} {request.url.path} "
        f"- 상태: {response.status_code} - 소요시간: {duration:.3f}s"
    )

    # 느린 요청 경고 (1초 이상)
    if duration > 1.0:
        logger.warning(f"느린 요청 감지: {request.url.path} ({duration:.3f}s)")

    return response
```

### 실전 로깅 패턴: 에러 추적

```python
import traceback
from fastapi import HTTPException

@app.get("/data/{item_id}")
async def get_data(item_id: int):
    """에러 추적을 위한 로깅 패턴"""
    try:
        logger.debug(f"데이터 조회 시작: item_id={item_id}")
        if item_id < 0:
            raise ValueError("음수 ID는 허용되지 않습니다")
        result = {"id": item_id, "name": f"아이템_{item_id}"}
        logger.info(f"데이터 조회 성공: {result}")
        return result
    except ValueError as e:
        logger.warning(f"잘못된 요청: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"데이터 조회 실패: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="내부 서버 오류")
```

> **핵심 포인트:** 로깅 미들웨어는 "CCTV"와 같습니다. 모든 요청과 응답을 기록하여 문제가 발생했을 때 원인을 빠르게 추적할 수 있도록 도와줍니다.

---

## 7. 환경변수와 설정 관리

### 왜 환경변수가 필요한가?

개발 환경과 운영 환경은 다릅니다. 데이터베이스 주소, API 키, 디버그 모드 등이 환경마다 다르기 때문에, 이런 값들을 코드에 직접 적으면 안 됩니다. 환경변수는 프로그램의 "상황별 의상"과 같습니다 -- 같은 사람이라도 출근할 때와 운동할 때 옷이 다른 것처럼, 같은 코드라도 개발/운영 환경에서 설정이 달라야 합니다.

```mermaid
graph TD
    CODE["애플리케이션 코드<br/>하나의 코드베이스"]
    DEV["개발 환경<br/>DEBUG=True<br/>DB=localhost"]
    STAGING["스테이징 환경<br/>DEBUG=False<br/>DB=staging-server"]
    PROD["운영 환경<br/>DEBUG=False<br/>DB=prod-server"]

    CODE --> DEV
    CODE --> STAGING
    CODE --> PROD

    style CODE fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style DEV fill:#55efc4,stroke:#00b894,color:#2d3436
    style STAGING fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style PROD fill:#e17055,stroke:#d63031,color:#fff
```

### os.environ

Python의 `os` 모듈로 운영체제의 환경변수에 접근할 수 있습니다.

```python
import os

# 환경변수 읽기 (기본값 지정 가능)
db_host = os.environ.get("DB_HOST", "localhost")
api_key = os.environ.get("API_KEY")  # 없으면 None

# 환경변수가 필수인 경우
secret_key = os.environ["SECRET_KEY"]  # 없으면 KeyError 발생
```

### .env 파일과 python-dotenv

매번 터미널에서 환경변수를 설정하는 것은 번거롭습니다. `.env` 파일에 환경변수를 저장하고, `python-dotenv`로 자동으로 불러올 수 있습니다.

```bash
# .env 파일 (프로젝트 루트에 생성)
APP_NAME=AI학습도우미
DEBUG=true
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
OPENAI_API_KEY=sk-your-api-key-here
SECRET_KEY=your-super-secret-key-12345
```

```python
# pip install python-dotenv
from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일 로드

app_name = os.environ.get("APP_NAME")
debug = os.environ.get("DEBUG", "false").lower() == "true"
```

### Pydantic Settings (BaseSettings)

FastAPI 프로젝트에서는 `pydantic-settings`를 사용하면 환경변수를 **타입 안전하게** 관리할 수 있습니다.

```python
# pip install pydantic-settings
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """애플리케이션 설정"""
    app_name: str = "My App"
    debug: bool = False
    database_url: str = "sqlite:///./app.db"
    openai_api_key: str = Field(..., description="OpenAI API 키")
    secret_key: str = Field(..., min_length=16)
    max_upload_size: int = 10 * 1024 * 1024  # 10MB

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

# 설정 인스턴스 생성 (.env 파일 자동 로드)
settings = Settings()

# FastAPI에서 사용
app = FastAPI(title=settings.app_name, debug=settings.debug)

@app.get("/info")
def get_info():
    return {"app_name": settings.app_name, "debug": settings.debug}
```

### 환경별 설정 분리

실전 프로젝트에서는 환경별로 `.env` 파일을 분리하여 관리합니다.

```
project/
├── .env                # 기본 환경변수 (공통)
├── .env.development    # 개발 환경
├── .env.staging        # 스테이징 환경
├── .env.production     # 운영 환경
├── .env.example        # 환경변수 템플릿 (커밋 대상)
└── .gitignore          # .env 파일 제외
```

```python
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    app_name: str = "My App"
    debug: bool = False
    database_url: str = "sqlite:///./app.db"
    log_level: str = "INFO"

    model_config = {
        "env_file": f".env.{os.getenv('APP_ENV', 'development')}",
        "env_file_encoding": "utf-8"
    }

# 실행 시 환경 지정: APP_ENV=production uvicorn main:app
```

### 보안: 비밀 정보 관리 원칙

```mermaid
graph LR
    A["설정 관리 계층 구조"]
    B["1단계: 코드 기본값 - 기본 포트, 앱 이름 등"]
    C["2단계: .env 파일 - API 키, DB 비밀번호 (커밋 금지!)"]
    D["3단계: 환경변수 - 서버에 직접 설정 (가장 안전)"]
    E["4단계: 비밀 관리 서비스 - AWS Secrets Manager 등"]

    A --> B
    A --> C
    A --> D
    A --> E

    style A fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style B fill:#55efc4,stroke:#00b894,color:#2d3436
    style C fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style D fill:#0984e3,stroke:#74b9ff,color:#fff
    style E fill:#e17055,stroke:#d63031,color:#fff
```

`.env` 파일에는 API 키, 데이터베이스 비밀번호 등 민감한 정보가 담겨 있으므로, 반드시 `.gitignore`에 등록해야 합니다.

```bash
# .gitignore에 반드시 추가
.env
.env.*
!.env.example
```

```bash
# .env.example (팀원에게 필요한 변수 목록을 알려주는 템플릿)
APP_NAME=YourAppName
DEBUG=true
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=change-this-to-a-random-string
```

> **핵심 포인트:** API 키나 비밀번호가 GitHub에 올라가면 몇 분 내에 악의적인 봇이 이를 탐지하고 악용합니다. `.env` 파일은 **절대 커밋하지 마세요**. `.env.example` 파일로 필요한 변수 목록만 공유합니다.

---

## 8. 핵심 정리

### 파일 I/O 요약

| 항목 | 핵심 내용 |
|------|----------|
| open() | `with open(path, mode, encoding="utf-8") as f:` 패턴 사용 |
| 파일 모드 | `r`(읽기), `w`(쓰기/덮어쓰기), `a`(추가), `rb/wb`(바이너리) |
| CSV | `csv.DictReader`/`DictWriter`로 딕셔너리 형태 처리 |
| JSON | `json.dump()`/`json.load()`로 파일 입출력 |
| FastAPI 업로드 | `UploadFile` + `File()`, 크기/타입 검증 필수 |

### 로깅 모범 사례 체크리스트

- `print()` 대신 `logging` 모듈을 사용하고 있는가?
- 적절한 로그 레벨(DEBUG, INFO, WARNING, ERROR, CRITICAL)을 사용하고 있는가?
- 로그에 시간, 모듈명, 레벨 등 필수 정보가 포함되어 있는가?
- `RotatingFileHandler`로 로그 파일 크기를 관리하고 있는가?
- 요청/응답 로깅 미들웨어가 설정되어 있는가?
- 에러 로그에 스택 트레이스가 포함되어 있는가?
- `dictConfig`로 로깅 설정을 체계적으로 관리하고 있는가?

### 환경변수 관리 요약

| 항목 | 핵심 내용 |
|------|----------|
| os.environ | 환경변수 직접 접근 (기본 방법) |
| python-dotenv | `.env` 파일에서 환경변수 자동 로드 |
| Pydantic Settings | 타입 검증 + .env 로드 (FastAPI 추천) |
| 환경 분리 | `.env.development`, `.env.production` 등으로 분리 |
| 보안 원칙 | `.env`를 `.gitignore`에 등록, `.env.example`만 커밋 |

### 오늘 배운 내용의 흐름

```mermaid
flowchart LR
    A["파일 I/O<br/>데이터 영구 저장"]
    B["CSV/JSON<br/>구조화된 데이터"]
    C["파일 업/다운로드<br/>FastAPI 연동"]
    D["로깅<br/>시스템 모니터링"]
    E["환경변수<br/>설정 관리"]

    A --> B --> C
    D --> E

    A -.-> |"기반 기술"| C
    D -.-> |"운영 필수"| C

    style A fill:#0984e3,stroke:#74b9ff,color:#fff
    style B fill:#55efc4,stroke:#00b894,color:#2d3436
    style C fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style D fill:#fdcb6e,stroke:#f39c12,color:#2d3436
    style E fill:#e17055,stroke:#d63031,color:#fff
```

---

## 다음 강의 미리보기

> 다음 강의 **[13. 외부 API 연동과 GPT 활용](13_external_api_and_gpt.md)**에서는 `httpx`/`requests`를 사용하여 외부 API를 호출하고, OpenAI GPT API를 연동하는 방법을 배웁니다.
> 오늘 배운 파일 처리(응답 저장), 로깅(API 호출 추적), 환경변수(API 키 관리)가 모두 활용됩니다!

```python
# 다음 시간 미리보기: 외부 API 호출 맛보기
import httpx
import os

api_key = os.environ.get("OPENAI_API_KEY")

async with httpx.AsyncClient() as client:
    response = await client.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": "gpt-4", "messages": [{"role": "user", "content": "안녕!"}]}
    )
    print(response.json())
```

---

[이전 강의: 11. 인증과 세션 관리](11_auth_and_session.md) | [다음 강의: 13. 외부 API 연동과 GPT 활용](13_external_api_and_gpt.md)
