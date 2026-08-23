# 7.video_generation — 동영상 생성

공식 문서: https://ai.google.dev/gemini-api/docs/veo

텍스트로 영상을 생성합니다. `6.video_understanding/`(영상 이해)의 반대 방향 — Veo 3.1이
오디오까지 포함된 영상을 만듭니다.

## 순서

| 파일 | 내용 |
|------|------|
| `1.video_generation.py` | 텍스트 → 영상, `veo-3.1-generate-preview` + 비동기 폴링 패턴 |
| `2.video_config.py` | 분량(`duration_seconds`)·화면비·해상도·제외 요소(`negative_prompt`)·`seed` 제어 |
| `3.image_to_video.py` | 이미지 → 영상 — 정지 이미지를 첫 프레임으로 주고 그 다음 동작만 지시 |
| `4.extend_video(deprecated).py` | 🛑 **실행하면 DeprecationWarning** — `prompt=`/`video=` 직접 전달 방식, 학습 히스토리로 보존 |
| `5.extend_video.py` | 영상 이어붙이기 — `source=GenerateVideosSource(...)` 현재 권장 방식 |

## API가 또 바뀌었습니다 — `source=` 인자

`4.extend_video(deprecated).py`를 실제로 실행하면 이런 경고가 뜹니다:

```
DeprecationWarning: The generate_videos method with prompt/image/video arguments is
deprecated and will be removed in a future major release (not before 2026-07-31).
Please use the source argument instead.
```

`2026-07-31` 이후 아무 때나 제거될 수 있다는 뜻인데 오늘(2026-08-23)은 이미 그 시점을 지났습니다 —
당장 안 되는 건 아니고(경고만 뜨고 실행은 됨, `generated_extended.mp4`가 실제로 생성되는 것까지
확인함) 그래서 Imagen 3처럼 파일을 죽이지 않고 "동작하되 경고가 뜨는" 상태로 남겨뒀습니다.

| | 예전 (`4.extend_video(deprecated).py`) | 지금 (`1~3`, `5.extend_video.py`) |
|---|---|---|
| 호출 | `generate_videos(model=..., prompt=..., image=..., video=...)` | `generate_videos(model=..., source=types.GenerateVideosSource(prompt=..., image=..., video=...))` |

`1.video_generation.py`, `2.video_config.py`, `3.image_to_video.py`는 처음부터 `source=` 방식으로
작성돼 있어 이 경고가 뜨지 않습니다 — 이 폴더에서 진짜로 "예전 방식 vs 지금 방식"을 비교하고
싶다면 `4.extend_video(deprecated).py` ↔ `5.extend_video.py`를 나란히 열어보세요.

Veo API가 preview 단계에서 빠르게 바뀌고 있다는 방증이기도 합니다 — 이 폴더를 만들던 중
Imagen 3 서비스 종료(`5.image_generation/`)에 이어 이번 세션에서만 두 번째로 마주친 API 변경입니다.

## 왜 폴링(polling)이 필요한가

지금까지 쓴 `generate_content()`/`interactions.create()`는 응답이 바로 옵니다. 영상은 생성에
수십 초~몇 분이 걸리기 때문에, API가 결과 대신 **작업(operation) 객체**를 먼저 돌려주고
`client.operations.get()`으로 완료 여부를 주기적으로 확인해야 합니다 — 동기 호출만 쓰던
지금까지의 패턴과 다른 지점입니다. OpenAI Sora, Runway 등 다른 영상 생성 API도 같은 방식이라
Veo만의 특이한 설계는 아닙니다.

## 분량 조정 · 디테일 제어는 어떻게 하나

두 갈래로 나뉩니다.

- **정량적 제어(`GenerateVideosConfig`)**: `duration_seconds`(4/6/8초), `aspect_ratio`,
  `resolution`, `negative_prompt`(빼고 싶은 요소), `seed`(재현성) — `2.video_config.py` 참고.
- **씬/카메라 워크 같은 "디테일"**: 여전히 프롬프트 텍스트로 지시합니다. 이미지 생성과 마찬가지로
  자연어가 곧 컨트롤입니다 — "트래킹 샷", "줌인", "노을이 지고 있다" 같은 표현이 그대로 반영됩니다.

한 번에 최대 8초라는 근본 제약은 config로도 못 넘습니다. 더 긴 이야기가 필요하면
`5.extend_video.py`처럼 여러 번 나눠서 이어 붙입니다.

## ⚠️ 비용 · 접근 제한

- **초당 $0.40**(720p/1080p, 오디오 포함가) · **초당 $0.60**(4K) — 2026-08 기준,
  [공식 가격표](https://ai.google.dev/gemini-api/docs/pricing)(Veo 3.1 Standard) 확인. 실행할
  때마다 실제 과금이 발생합니다. 이 저장소의 다른 예제와 달리 반복 실행을 권장하지 않습니다.
  `5.extend_video.py`는 호출을 두 번 하므로 비용도 두 배입니다.
- **API 응답에 비용·소요 시간 필드가 없습니다** — 텍스트 API의 `usage_metadata` 같은 게 Veo엔
  없습니다. 그래서 각 예제 파일이 우리가 요청한 `duration_seconds`로 비용을 직접 계산하고,
  `time.time()`으로 소요 시간을 직접 측정해서 실행 끝에 함께 출력합니다.
- `veo-3.1-generate-preview`는 preview 모델이라 계정/지역에 따라 접근이 제한될 수 있습니다.
- 1080p/4k는 8초 고정이고, 영상 확장(extend)은 720p로만 지원됩니다.
- 이 폴더의 코드는 [공식 문서](https://ai.google.dev/gemini-api/docs/veo)의 예제와 대조해서
  작성했지만, 비용 문제로 라이브 실행 검증은 하지 않았습니다 — 실행 전 가격 정책을 다시
  확인하세요.

## 설치

```bash
pip install google-genai python-dotenv
```

API 키는 `4.google/.env`에 설정합니다: `GOOGLE_API_KEY=...`
