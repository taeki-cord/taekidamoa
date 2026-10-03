import sys, json, sherpa_onnx, soundfile as sf, numpy as np
d = [p for p in __import__('glob').glob('sherpa-onnx-sense-voice-*')][0]
rec = sherpa_onnx.OfflineRecognizer.from_sense_voice(model=f"{d}/model.int8.onnx", tokens=f"{d}/tokens.txt", language="ko", use_itn=True, num_threads=4)
a, sr = sf.read(sys.argv[1], dtype="float32")
segs = json.loads(sys.argv[2])
out = []
for s, e in segs:
    st = rec.create_stream(); st.accept_waveform(sr, a[int(s*sr):int(e*sr)]); rec.decode_stream(st)
    r = st.result
    out.append({"start": s, "end": e, "text": r.text, "tokens": list(r.tokens), "ts": [round(s+t,2) for t in r.timestamps]})
    print(f"{s:6.2f}-{e:6.2f} {r.text}")
json.dump(out, open("asr.json","w"), ensure_ascii=False)
