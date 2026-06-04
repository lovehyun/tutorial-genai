# 12.audio_chat — gpt-4o-audio (오디오 입출력 단일 모델)

`gpt-4o-audio` 는 **오디오를 직접 입력/출력하는 멀티모달 챗 모델**이다.
지금까지의 음성은 **STT(`8.whisper_stt`) + TTS(`10.tts`) 2단계 파이프라인**이었는데,
여기선 그 일을 **모델 하나**가 한다 (오디오 in → 이해/추론 → 오디오 out).

## 핵심
- `chat.completions` + `modalities=['text','audio']` → **음성 답변**(`message.audio.data` base64 + `message.audio.transcript`)
- 오디오 입력: `content` 블록에 `{'type':'input_audio','input_audio':{'data':b64,'format':'wav'}}`
- 모델: `gpt-4o-audio-preview` (신형 별칭 `gpt-audio`), `voice`/`format` 지정 가능

## 파일 (기본 → 고도화 → 실용)
| 파일 | 내용 |
|------|------|
| `1.audio_output.py` | 텍스트 질문 → **음성 답변**(answer.wav) |
| `2.audio_input.py` | **오디오 파일 입력** → 이해·요약·답변 (단순 STT 아님) |
| `3.voice_chat.py` | **마이크 음성 → 음성 답변** 한 턴 (개념: 한 번 녹음→파일 저장) |
| `4.voice_chat_loop.py` | **연속 음성 대화** — 답변 **자동 재생**(`sd.play`) + 히스토리 누적으로 **맥락 유지**, 계속 묻고 듣기 |

## 실행
```bash
cd 1.openai/10.multimodal/12.audio_chat
pip install openai python-dotenv
pip install sounddevice scipy   # 3.voice_chat (마이크 녹음)
# 1.openai/.env 에 OPENAI_API_KEY

python 1.audio_output.py    # answer.wav
python 2.audio_input.py     # 같은 폴더에 question.wav 두고 실행
python 3.voice_chat.py      # 5초 녹음 → reply.wav (한 턴)
python 4.voice_chat_loop.py # 연속 대화: Enter 녹음 → 답변 자동 재생 → 반복 (q 종료)
```
> 생성 오디오(`*.wav`)는 `.gitignore` 처리됨.

## STT/TTS vs gpt-4o-audio
| | STT(`8.whisper_stt`) | TTS(`10.tts`) | **gpt-4o-audio(여기)** |
|---|---|---|---|
| 방향 | 오디오→텍스트 | 텍스트→오디오 | **오디오↔오디오(이해+생성)** |
| 호출 | 받아쓰기만 | 읽어주기만 | **한 모델이 이해하고 답까지** |

실시간 스트리밍 음성 대화 앱은 [`../11.webrtc_app/`](../11.webrtc_app/) 참고.
