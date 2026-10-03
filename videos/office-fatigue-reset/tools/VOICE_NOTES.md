# 나레이션 처리 기록

- 현재: assets/voice/narration-full.wav — 사용자 Voicebox 재생성본(73.6s, `**` 표시 없이). 편집 없음.
- 장면 분할: 문장 사이 쉼(무음 ≥0.35s)의 중간점에서 11개로 분할 → assets/voice/NN.wav
- 단어 타이밍: tools/asr_sensevoice.py(sherpa-onnx SenseVoice, ko) → tools/asr.json → tools/align_voice.py
  → audio_meta.json(자막 단어 시각), tools/voice_align.json(애니메이션 큐 재배치)
- 재실행: python3 tools/align_voice.py assets/voice/narration-full.wav tools/segs.json tools/asr.json '<groups>'
  → audio.mjs sync-durations → tools/build.sh
- 이전 버전(1차 녹음, `**` 낭독 4곳 잘라냄)은 git 기록에 있음.
