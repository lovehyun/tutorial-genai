# 10.tts — 음성 생성 기초 (Text-To-Speech)

**TTS = 텍스트를 입력으로 받아 음성을 생성하는 것** (텍스트 → 오디오).
반대 방향인 **음성 인식(STT, 오디오 → 텍스트)** 은 [`../8.whisper_stt/`](../8.whisper_stt/) 참고.

## 핵심
- `audio.speech.create(model, voice, input)` → 오디오 응답
- `response.write_to_file('output.mp3')` 로 저장 (기본 mp3)
- 모델: `gpt-4o-mini-tts`(최신·경량), `tts-1`, `tts-1-hd`
- `voice`: alloy / nova / onyx / echo / fable / shimmer / coral / sage …
- `gpt-4o-mini-tts` 는 `instructions` 로 **말투·감정**까지 지시 가능

## 파일
| 파일 | 내용 |
|------|------|
| `1.tts_basic.py` | 텍스트 → mp3 (가장 기본) |
| `2.tts_voices.py` | 여러 voice 비교 (각각 mp3 저장) |
| `3.tts_style_format.py` | `instructions`(말투) + `response_format`(mp3/wav 등) |

## 실행
```bash
cd 1.openai/10.multimodal/10.tts
pip install openai python-dotenv
# 1.openai/.env 에 OPENAI_API_KEY

python 1.tts_basic.py        # output.mp3 생성
python 2.tts_voices.py       # voice_alloy.mp3 등
python 3.tts_style_format.py # cheerful.mp3, output.wav
```
> 생성된 오디오 파일(`*.mp3`/`*.wav`)은 `.gitignore` 처리됨.

## 참고
- 음성 인식(STT): [`../8.whisper_stt/`](../8.whisper_stt/) · 실시간 음성 앱: [`../11.webrtc_app/`](../11.webrtc_app/)
