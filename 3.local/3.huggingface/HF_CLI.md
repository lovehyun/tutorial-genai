# Hugging Face CLI 사용법

## Hugging Face란?
Hugging Face는 자연어 처리(NLP)를 포함한 다양한 머신러닝 모델을 제공하는 플랫폼으로, 주로 **Transformers 라이브러리**를 통해 강력한 사전 학습된 모델을 쉽게 사용할 수 있도록 지원합니다. 또한, **Hugging Face Hub**를 통해 사용자들이 모델, 데이터셋, 코드 스니펫을 공유할 수 있도록 합니다.

Hugging Face는 다음과 같은 주요 도구들을 제공합니다:
1. **Transformers**: 사전 학습된 NLP 모델 라이브러리
2. **Datasets**: 대규모 데이터셋 라이브러리
3. **Tokenizers**: 빠른 토큰화 라이브러리
4. **Accelerate**: 분산 학습을 위한 도구
5. **Hub**: 모델과 데이터셋을 공유하는 플랫폼
6. **CLI (Command Line Interface)**: 명령줄에서 Hugging Face Hub를 쉽게 사용할 수 있는 도구

---

## Hugging Face CLI 설치 및 설정

### 1. CLI 설치
Hugging Face의 CLI 도구를 사용하려면 `huggingface_hub` 패키지를 설치해야 합니다.

```bash
pip install huggingface_hub
```

또는 `transformers` 라이브러리를 설치하면 자동으로 CLI도 설치됩니다.

```bash
pip install transformers
```

### 2. 로그인 (Authentication)
Hugging Face Hub에 연결하려면 **액세스 토큰**을 사용해야 합니다.

1. Hugging Face 웹사이트에서 [Access Tokens](https://huggingface.co/settings/tokens) 페이지에 접속하여 `Write` 권한이 있는 토큰을 생성합니다.
2. 다음 명령어로 로그인합니다.

```bash
huggingface-cli login
```

3. 프롬프트에 토큰을 입력하면 로그인됩니다.

로그인이 성공하면 `~/.huggingface/token` 파일에 저장됩니다.

---

## Hugging Face CLI 명령어

### 1. 모델 관련 명령어

#### (1) 모델 업로드
```bash
huggingface-cli upload <model_path> --repo-type model --repo-id <your-username>/<repo-name>
```

예제:
```bash
huggingface-cli upload my_model/ --repo-type model --repo-id johndoe/my-awesome-model
```

#### (2) 모델 삭제
```bash
huggingface-cli delete --repo-id <your-username>/<repo-name> --repo-type model
```

예제:
```bash
huggingface-cli delete --repo-id johndoe/my-awesome-model --repo-type model
```

---

### 2. 데이터셋 관련 명령어

#### (1) 데이터셋 업로드
```bash
huggingface-cli upload <dataset_path> --repo-type dataset --repo-id <your-username>/<repo-name>
```

예제:
```bash
huggingface-cli upload my_dataset/ --repo-type dataset --repo-id johndoe/my-dataset
```

#### (2) 데이터셋 삭제
```bash
huggingface-cli delete --repo-id <your-username>/<repo-name> --repo-type dataset
```

---

### 3. Spaces 관련 명령어 (Hugging Face에서 앱 배포)

#### (1) Space 생성
```bash
huggingface-cli space create <repo-name> --sdk <streamlit|gradio|static>
```

예제 (Gradio 기반 Space 생성):
```bash
huggingface-cli space create my-cool-app --sdk gradio
```

#### (2) Space 삭제
```bash
huggingface-cli delete --repo-id <your-username>/<repo-name> --repo-type space
```

---

### 4. 캐시 정리

Hugging Face는 다운로드한 모델과 데이터셋을 캐시(기본적으로 `~/.cache/huggingface/`)에 저장합니다. 캐시가 너무 커지면 정리할 수 있습니다.

```bash
huggingface-cli delete-cache
```

특정 모델 캐시만 삭제하려면:
```bash
huggingface-cli delete-cache --pattern "bert-base-uncased"
```

---

## Python에서 Hugging Face 사용 예제

### 1. 모델 로드 및 추론
```python
from transformers import pipeline

# 사전 학습된 텍스트 분류 모델 로드
classifier = pipeline("sentiment-analysis")

# 문장 감성 분석 실행
result = classifier("I love using Hugging Face!")[0]
print(result)  # {'label': 'POSITIVE', 'score': 0.9998}
```

### 2. 모델 업로드 (Python 코드에서)
```python
from huggingface_hub import HfApi

api = HfApi()

api.upload_folder(
    folder_path="my_model",
    repo_id="johndoe/my-awesome-model",
    repo_type="model"
)
```

---

## 정리
Hugging Face CLI를 사용하면 명령줄에서 쉽게 **모델**, **데이터셋**, **Spaces**를 업로드하고 관리할 수 있습니다.

주요 명령어:
- `huggingface-cli login`: Hugging Face 로그인
- `huggingface-cli upload <path> --repo-type <model|dataset|space>`: 업로드
- `huggingface-cli delete --repo-id <repo-name> --repo-type <model|dataset|space>`: 삭제
- `huggingface-cli delete-cache`: 캐시 정리

또한, Python 코드에서 `transformers`와 `huggingface_hub` 라이브러리를 사용하면 다양한 기능을 활용할 수 있습니다.
