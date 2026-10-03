#!/usr/bin/env python3
"""Split a full narration into per-frame clips and derive timing data.

Inputs : narration wav, segs JSON (speech segments [[start,end],...]),
         asr JSON (per-segment SenseVoice tokens + timestamps, tools/asr_sensevoice.py),
         groups — which speech segments belong to each storyboard frame.
Outputs: assets/voice/NN.wav, audio_meta.json (frame-local caption words),
         tools/voice_align.json (knots mapping draft-voice cue times → real speech).

usage: align_voice.py NARR.wav SEGS.json ASR.json '[[0],[1,2],...]'
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

P = Path(__file__).resolve().parent.parent
TAIL = 2.6  # hold after the last line for the ending card
# speech span of each frame in the draft TTS the cue times were authored against
OLD_SPAN = {1: (0.46, 6.97), 2: (0.41, 5.94), 3: (0.50, 6.45), 4: (0.43, 5.02), 5: (0.55, 6.51),
            6: (0.41, 6.03), 7: (0.39, 8.63), 8: (0.44, 7.09), 9: (0.42, 8.25), 10: (0.50, 7.28),
            11: (0.50, 4.47)}


def clean(s):
    return re.sub(r"[^\w]", "", s)


def main():
    narr, segs_p, asr_p, groups = sys.argv[1], sys.argv[2], sys.argv[3], json.loads(sys.argv[4])
    a, sr = sf.read(narr)
    segs = json.load(open(segs_p))
    asr = json.load(open(asr_p))
    total_len = len(a) / sr
    cuts = [0.0] + [(segs[g[-1]][1] + segs[g[-1] + 1][0]) / 2 for g in groups[:-1]] + [total_len]
    sb = (P / "STORYBOARD.md").read_text(encoding="utf-8")
    vos = {int(n): v for n, v in re.findall(r'## Frame (\d+) — .+?\n.*?- voiceover: "(.+?)"', sb, re.S)}
    align, meta = {}, []
    for i, g in enumerate(groups):
        n = i + 1
        s, e = cuts[i], cuts[i + 1]
        clip = a[int(s * sr):int(e * sr)]
        if n == len(groups):
            clip = np.concatenate([clip, np.zeros(int(TAIL * sr))])
        path = f"assets/voice/{n:02d}.wav"
        sf.write(P / path, clip, sr)
        dur = len(clip) / sr
        pts, pos = [], 0
        for k in g:
            for tok, t in zip(asr[k]["tokens"], asr[k]["ts"]):
                c = clean(tok)
                if c:
                    pts.append((pos, t - s))
                    pos += len(c)
        sp_start, sp_end = segs[g[0]][0] - s, segs[g[-1]][1] - s
        pts = [(0, sp_start)] + pts[1:] + [(pos, sp_end)]
        fr = [p / pos for p, _ in pts]
        ts = list(np.maximum.accumulate([t for _, t in pts]))
        newt = lambda f: float(np.interp(f, fr, ts))
        os_, oe = OLD_SPAN[n]
        align[n] = {"knots": [[0.0, 0.0]] + [[round(os_ + (oe - os_) * f, 3), round(newt(f), 3)]
                                            for f in np.linspace(0, 1, 21)], "dur": round(dur, 3)}
        words = vos[n].split()
        wt = sum(len(clean(w)) for w in words)
        acc, W = 0, []
        for j, w in enumerate(words):
            a0 = acc / wt
            acc += len(clean(w))
            W.append({"id": f"w{n}-{j}", "text": w.replace("'", ""),
                      "start": round(newt(a0), 3), "end": round(newt(acc / wt) - 0.02, 3)})
        meta.append({"frame": n, "path": path, "duration_s": round(dur, 3), "words": W})
        print(n, round(dur, 2), "speech", round(sp_start, 2), round(sp_end, 2))
    (P / "tools" / "voice_align.json").write_text(json.dumps(align, ensure_ascii=False, indent=1))
    (P / "audio_meta.json").write_text(json.dumps({"bgm": None, "bgm_pending": False, "voices": meta, "sfx": []},
                                                  ensure_ascii=False, indent=2))
    print("total", round(sum(m["duration_s"] for m in meta), 2))


if __name__ == "__main__":
    main()
