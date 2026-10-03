---
workflow: faceless-explainer
flow: automation
storyboard: no
message: "직장인의 만성 피로는 수면 부족이 아니라 쉬지 못한 눈과 뇌 때문 — 커피 대신 짧지만 진짜인 휴식으로 채우자"
destination: youtube
aspect: 1920x1080
language: ko
audience: 40~50대 직장인
length: 75s
angle: narrative
vo_mode: verbatim
---

## Intent

40~50대 직장인 대상 유튜브 채널의 첫 그래픽 영상. 사용자가 쓴 나레이션 원고를 그대로(verbatim) 쓰고,
그 음성에 맞춘 모션 그래픽을 얹는다. 요청 원문: "15년차 모션 그래픽 편집 전문가로서 가독성 좋고 미니멀한 디자인으로".

## Assets

- (대기) 사용자 본인 목소리 나레이션 — 사용자 PC의 Voicebox 프로필(profile-taeki.voicebox.zip\samples). 아직 미전달.

## Customizations

- 임시 나레이션: 오프라인 한국어 TTS(sherpa-onnx, vits-mimic3 ko_KO-kss). 사용자 음성이 오면 교체 후 싱크 재조정.
- 한글 폰트: Pretendard (assets/fonts).
- 2차 수정(사용자 요청 "생동감 없고 단조로움 → 생기찬 느낌"): 장면별 컬러 배경 테마(sun/cream/coral/blue/mint) + 장식 원형 도형. tools/build_frames.py THEMES.

## Notes

- "일단 보고 나서 상의" — 스토리보드 검토 없이 한 번에 만들어 보여주는 시안.
- 40~50대 시청자: 큰 글씨, 화면당 핵심 단어 1~2개, 높은 대비, 과한 효과 금지.
