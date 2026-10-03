import soundfile as sf, numpy as np, glob, sherpa_onnx, itertools
a,sr=sf.read("/root/.claude/uploads/741c579c-e359-59cc-9755-5022741e80b2/7f317136-___-.wav", dtype="float32")
d=glob.glob('sherpa-onnx-sense-voice-*')[0]
rec=sherpa_onnx.OfflineRecognizer.from_sense_voice(model=f"{d}/model.int8.onnx",tokens=f"{d}/tokens.txt",language="ko",use_itn=True,num_threads=4)
f=int(0.010*sr)
def splice(x,cuts,start,end):
    out=[];prev=start
    for s,e in cuts:
        seg=x[int(prev*sr):int(s*sr)].copy()
        if prev>start: seg[:f]*=np.linspace(0,1,f)
        seg[-f:]*=np.linspace(1,0,f); out.append(seg); prev=e
    seg=x[int(prev*sr):int(end*sr)].copy(); seg[:f]*=np.linspace(0,1,f); out.append(seg)
    return np.concatenate(out)
def asr(y):
    st=rec.create_stream(); st.accept_waveform(sr,y); rec.decode_stream(st); return st.result.text
print("orig A:",asr(a[int(20.87*sr):int(26.63*sr)]))
for s,e in itertools.product([24.74,24.755,24.77],[24.96,24.99,25.01,25.025]):
    y=splice(a,[(s,e),(25.86,26.62)],20.87,26.63); print("A",s,e,asr(y))
print("orig B:",asr(a[int(64.75*sr):int(70.70*sr)]))
for c3,c4 in itertools.product([(67.00,67.30),(67.00,67.28)],[(68.77,69.12),(68.77,69.08),(68.78,69.15),(68.74,69.10)]):
    y=splice(a,[c3,c4],64.75,70.70); print("B",c3,c4,asr(y))
