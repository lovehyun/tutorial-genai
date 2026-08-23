# 1.vision — 비전 (이미지 이해)

이미지를 입력으로 받아 **설명·분석**합니다 (이미지 *생성*이 아니라 이미지 → 텍스트).
`1.vision/`(기본 스크립트) → `2.vision_app*`(웹앱, 단계별 진화) 순서로 구성됩니다.

| 디렉토리 | 구분 | 내용 |
|----------|------|------|
| [`1.vision/`](1.vision/) | 기본 | URL/로컬 이미지 분석, 여러 질문(OCR·색상·분위기 등) — 3개 스크립트 |
| [`2.vision_app/`](2.vision_app/) | 앱 1단계 | 이미지 업로드 → 설명 (가장 단순, 한 페이지) |
| [`2.vision_app2_design/`](2.vision_app2_design/) | 앱 2단계 | 라우트 분리 + JSON 응답 + UI 개선 |
| [`2.vision_app3_clipboard/`](2.vision_app3_clipboard/) | 앱 3단계 | 사용자 질문 입력 + 클립보드 붙여넣기(Ctrl+V) |
| [`2.vision_app4_micinput/`](2.vision_app4_micinput/) | 앱 4단계 | 마이크 음성 질문(브라우저 STT) + 업로드 제한/에러 처리 |
| [`2.vision_app5_micinputoutput/`](2.vision_app5_micinputoutput/) | 앱 5단계 | 답변 음성 출력(TTS) — 백엔드는 4단계와 동일 |
| [`2.vision_app6_micrealtime/`](2.vision_app6_micrealtime/) | 앱 6단계 | 실시간 음성 대화(스트리밍) — Flask 대신 Quart(비동기) |

앱 시리즈는 매 단계 **한 가지 기능만** 더하며 진화합니다. 4~6단계의 음성 입력은 브라우저 `SpeechRecognition`(클라이언트 STT)이며,
서버에서 Whisper로 인식하는 방식은 [`../3.stt/`](../3.stt/)에서 다룹니다.
