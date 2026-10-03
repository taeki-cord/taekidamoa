# 나레이션 처리 기록

- 원본: 사용자 Voicebox 생성 음성 (74.8s, 24kHz mono)
- 원고의 `**굵게**` 표시가 음성으로 읽혀 들어간 4곳을 잘라냄 (원본 기준 초):
  24.755–25.025, 25.86–26.62, 67.00–67.28, 68.77–69.12
- 결과: assets/voice/narration-full-clean.wav (73.14s) → 문장 사이 쉼 지점에서 11개 장면으로 분할 (assets/voice/NN.wav)
- 단어 타이밍: sherpa-onnx SenseVoice(ko) 인식 토큰 시각 → 원고 글자 비율로 보간 → audio_meta.json words, tools/voice_align.json(애니메이션 큐 재배치)
- 확인 필요: 24초 부근 "생기는 시각적 피로", 67초 부근 "짧지만 진짜인 휴식으로" — 잘라낸 경계 (최종 영상 기준 약 24초 / 66초)
