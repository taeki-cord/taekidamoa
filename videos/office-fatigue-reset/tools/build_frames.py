#!/usr/bin/env python3
"""Generate the 11 frame sub-compositions for office-fatigue-reset.

Each frame is a bare <template> fragment (HyperFrames sub-composition contract).
Shared atoms (fonts, cream ground, eyebrow, counter, progress bar) are emitted per
file; every authored class/id is prefixed with the frame prefix (fNN-) so frames
never collide once assembled. Durations are read from STORYBOARD.md so a voice
swap only needs `sync-durations` + a re-run of this script.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SB = (ROOT / "STORYBOARD.md").read_text(encoding="utf-8")
TOTAL = 11

durations = {}
for m in re.finditer(r"## Frame (\d+) — .+?\n(.*?)(?=\n## |\Z)", SB, re.S):
    d = re.search(r"- duration: ([\d.]+)s", m.group(2))
    durations[int(m.group(1))] = float(d.group(1))

FONTS = "".join(
    '@font-face{font-family:"Pretendard";font-weight:%d;font-style:normal;font-display:block;'
    'src:url("assets/fonts/Pretendard-%s.woff2") format("woff2");}' % (w, n)
    for w, n in [(400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold")]
)

BASE_CSS = """
#root{position:absolute;inset:0;width:1920px;height:1080px;overflow:hidden;font-family:"Pretendard",sans-serif;color:#111;container-type:size;word-break:keep-all}
#root *{box-sizing:border-box}
.P-bg{position:absolute;inset:0;background:#fdfae7}
.P-stage{position:absolute;inset:0}
.P-deco{position:absolute;border-radius:50%;pointer-events:none}
.P-deco1{width:760px;height:760px;right:-220px;top:-260px;background:@DECO1@}
.P-deco2{width:420px;height:420px;left:-150px;bottom:-170px;background:@DECO2@}
.P-deco3{width:120px;height:120px;right:110px;bottom:60px;border:14px solid @DECO2@}
.P-eyebrow{position:absolute;left:96px;top:80px;display:flex;align-items:center;gap:20px;color:#1e2bfa;font-weight:700;font-size:32px;letter-spacing:0.02em}
.P-eyebrow i{display:block;width:60px;height:5px;border-radius:3px;background:#1e2bfa}
.P-counter{position:absolute;right:96px;top:84px;font-size:26px;font-weight:600;color:#7a7a7a;letter-spacing:0.06em;font-variant-numeric:tabular-nums}
.P-track{position:absolute;left:0;right:0;bottom:0;height:6px;background:rgba(30,43,250,0.08)}
.P-prog{position:absolute;left:0;bottom:0;height:6px;background:#1e2bfa}
.P-card{background:rgba(30,43,250,0.04);border:1.5px solid rgba(30,43,250,0.2);border-radius:14px}
.P-h1{font-weight:800;letter-spacing:-0.03em;line-height:1.1;color:#111}
.P-muted{color:#6b6b6b;font-weight:600}
.P-w{display:inline-block}
.P-mark{background-image:linear-gradient(@MARK@,@MARK@);background-repeat:no-repeat;background-position:0 88%;background-size:0% 34%}
.P-pill{display:flex;width:fit-content;align-items:center;gap:12px;padding:14px 30px;border-radius:100px;font-weight:700;font-size:34px}
.P-pill.solid{background:#1e2bfa;color:#fdfae7}
.P-pill.soft{background:rgba(30,43,250,0.08);color:#1e2bfa}
.P-step{display:inline-flex;align-items:center;justify-content:center;width:64px;height:64px;border-radius:50%;background:#1e2bfa;color:#fdfae7;font-weight:800;font-size:32px}
svg .ink{fill:none;stroke:#111;stroke-width:8;stroke-linecap:round;stroke-linejoin:round}
svg .cob{fill:none;stroke:#1e2bfa;stroke-width:8;stroke-linecap:round;stroke-linejoin:round}
svg .soft{fill:none;stroke:rgba(30,43,250,0.25);stroke-width:8;stroke-linecap:round}
"""

BASE_JS = """
const tl = gsap.timeline({ paused: true });
const E = "power3.out";
const q = (s) => document.querySelectorAll('[data-composition-id="__ID__"] ' + s);
const up = (s, t, o) => tl.fromTo(q(s), { opacity: 0, y: 40 }, Object.assign({ opacity: 1, y: 0, duration: 0.7, ease: E }, o || {}), t);
const fade = (s, t, o) => tl.fromTo(q(s), { opacity: 0 }, Object.assign({ opacity: 1, duration: 0.6, ease: "power2.out" }, o || {}), t);
const pop = (s, t, o) => tl.fromTo(q(s), { opacity: 0, scale: 0.6 }, Object.assign({ opacity: 1, scale: 1, duration: 0.6, ease: E }, o || {}), t);
const draw = (s, t, d, o) => tl.fromTo(q(s), { strokeDashoffset: 1, opacity: 1 }, Object.assign({ strokeDashoffset: 0, duration: d || 1, ease: "power2.inOut" }, o || {}), t);
const mark = (s, t) => tl.fromTo(q(s), { backgroundSize: "0% 34%" }, { backgroundSize: "100% 34%", duration: 0.7, ease: "power2.inOut" }, t);
q("[pathLength='1']").forEach((p) => { p.style.strokeDasharray = "1"; p.style.strokeDashoffset = "1"; });
tl.fromTo(q(".P-prog"), { width: __PFROM__ }, { width: __PTO__, duration: 0.9, ease: "power2.inOut" }, 0.1);
up(".P-eyebrow", 0.25);
tl.fromTo(q(".P-deco1"), { scale: 0.85, opacity: 0 }, { scale: 1, opacity: 1, duration: 1.2, ease: E }, 0);
tl.fromTo(q(".P-deco2"), { scale: 0.8, opacity: 0 }, { scale: 1, opacity: 1, duration: 1.2, ease: E }, 0.15);
tl.fromTo(q(".P-deco3"), { scale: 0.5, opacity: 0, rotation: -30 }, { scale: 1, opacity: 1, rotation: 0, duration: 1.0, ease: E }, 0.3);
fade(".P-counter", 0.25);
"""


# ── per-scene color themes (lively remix of the blue-professional atoms) ─────
# Each theme maps the base literals the frames are written in (cream / cobalt / ink)
# onto its own palette at generation time, so frame code stays theme-agnostic.
THEMES = {
    "sun":   dict(bg="#FFD43B", ink="#1B1B3A", accent="#2340F5", muted="rgba(27,27,58,0.74)", tint=(255, 255, 255), k=6.0,
                  mark="rgba(255,90,54,0.55)", ok="#12B886", warn="#FF5A36", deco1="rgba(255,255,255,0.30)", deco2="rgba(255,90,54,0.22)"),
    "cream": dict(bg="#FFF4E0", ink="#1B1B3A", accent="#DE3A16", muted="rgba(27,27,58,0.72)", tint=(255, 140, 90), k=1.4,
                  mark="rgba(255,212,59,0.85)", ok="#12B886", warn="#FF5A36", deco1="rgba(255,212,59,0.38)", deco2="rgba(35,64,245,0.12)"),
    "coral": dict(bg="#F2542D", ink="#1B1B3A", accent="#FFFFFF", muted="rgba(27,27,58,0.78)", tint=(255, 255, 255), k=3.0,
                  mark="rgba(255,212,59,0.9)", ok="#12B886", warn="#1B1B3A", deco1="rgba(255,255,255,0.16)", deco2="rgba(255,212,59,0.35)"),
    "blue":  dict(bg="#2340F5", ink="#FFFFFF", accent="#FFD43B", muted="rgba(255,255,255,0.80)", tint=(255, 255, 255), k=3.0,
                  mark="rgba(255,90,54,0.95)", ok="#3DDC97", warn="#FF7A59", deco1="rgba(255,255,255,0.10)", deco2="rgba(255,212,59,0.30)"),
    "mint":  dict(bg="#34D399", ink="#0F2A2A", accent="#2340F5", muted="rgba(15,42,42,0.74)", tint=(255, 255, 255), k=4.0,
                  mark="rgba(255,212,59,0.95)", ok="#2340F5", warn="#FF5A36", deco1="rgba(255,255,255,0.26)", deco2="rgba(35,64,245,0.18)"),
}
THEME_FOR = {1: "sun", 2: "cream", 3: "coral", 4: "blue", 5: "blue", 6: "cream",
             7: "mint", 8: "cream", 9: "mint", 10: "blue", 11: "sun"}


def apply_theme(html, t):
    def rgb(hexv):
        h = hexv.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    ar, ag, ab = rgb(t["accent"])
    ir, ig, ib = rgb(t["ink"])
    tr, tg, tb = t["tint"]
    # low-alpha cobalt tints → theme tint (boosted so cards/pills read on saturated grounds)
    html = re.sub(r"rgba\(30,43,250,([\d.]+)\)",
                  lambda m: "rgba(%d,%d,%d,%.2f)" % (tr, tg, tb, min(1.0, float(m.group(1)) * t["k"])), html)
    html = re.sub(r"rgba\(17,17,17,([\d.]+)\)", lambda m: "rgba(%d,%d,%d,%s)" % (ir, ig, ib, m.group(1)), html)
    for a, b in [("#1e2bfa", t["accent"]), ("#fdfae7", t["bg"]), ("#fbf8e6", "#FFFFFF"),
                 ("#6b6b6b", t["muted"]), ("#7a7a7a", t["muted"]), ("#9a9a9a", t["muted"]),
                 ("@MARK@", t["mark"]), ("@OK@", t["ok"]), ("@WARN@", t["warn"]),
                 ("@DECO1@", t["deco1"]), ("@DECO2@", t["deco2"])]:
        html = html.replace(a, b)
    html = re.sub(r"#111(?![0-9a-fA-F])", t["ink"], html)
    return html


def frame(n, fid, eyebrow, body, css, js, final=False):
    dur = durations[n]
    p = "f%02d-" % n
    pfrom = round((n - 1) / TOTAL * 1920)
    pto = round(n / TOTAL * 1920)
    exit_js = ""
    if final:
        exit_js = 'tl.to(q(".P-stage"), { opacity: 0, duration: 0.6, ease: "power2.in" }, %.2f);\n' % (dur - 0.7)
    html = f"""<template>
<script src="assets/vendor/gsap.min.js"></script>
<style>
{FONTS}
{BASE_CSS}
{css}
</style>
<div id="root" data-composition-id="{fid}" data-width="1920" data-height="1080" data-duration="{dur}">
  <div id="P-bg" class="P-bg clip" data-start="0" data-duration="{dur}" data-track-index="0"><div class="P-deco P-deco1"></div><div class="P-deco P-deco2"></div><div class="P-deco P-deco3"></div></div>
  <div id="P-stage" class="P-stage clip" data-start="0" data-duration="{dur}" data-track-index="1">
    <div class="P-eyebrow"><i></i><span>{eyebrow}</span></div>
    <div class="P-counter">{n:02d} / {TOTAL}</div>
{body}
    <div class="P-track"></div>
    <div class="P-prog"></div>
  </div>
</div>
<script>
(() => {{
{BASE_JS}
{js}
{exit_js}tl.set({{}}, {{}}, {dur});
window.__timelines = window.__timelines || {{}};
window.__timelines["{fid}"] = tl;
}})();
</script>
</template>
"""
    html = html.replace("__ID__", fid).replace("__PFROM__", str(pfrom)).replace("__PTO__", str(pto))
    html = html.replace("P-", p)
    html = apply_theme(html, THEMES[THEME_FOR[n]])
    out = ROOT / "compositions" / "frames" / f"{fid}.html"
    out.write_text(html, encoding="utf-8")
    print("wrote", out.relative_to(ROOT), dur)


# ── reusable SVG pieces ──────────────────────────────────────────────────────
def cup_svg(cls="P-cup"):
    return f"""<svg class="{cls}" viewBox="0 0 400 540" width="400" height="540">
      <path class="P-liquid" d="M88 208 L312 208 L292 500 Q290 516 274 516 L126 516 Q110 516 108 500 Z" fill="rgba(122,74,42,0.88)"/>
      <rect class="P-ice" x="130" y="250" width="70" height="70" rx="10" fill="#ffffff" stroke="#1e2bfa" stroke-width="6" transform="rotate(-12 165 285)"/>
      <rect class="P-ice" x="210" y="290" width="66" height="66" rx="10" fill="#ffffff" stroke="#1e2bfa" stroke-width="6" transform="rotate(10 243 323)"/>
      <rect class="P-ice" x="150" y="350" width="62" height="62" rx="10" fill="#ffffff" stroke="#1e2bfa" stroke-width="6" transform="rotate(6 181 381)"/>
      <path class="ink" pathLength="1" d="M70 150 L330 150 L300 500 Q298 520 276 520 L124 520 Q102 520 100 500 Z"/>
      <path class="ink" pathLength="1" d="M56 150 Q56 112 96 112 L304 112 Q344 112 344 150"/>
      <path class="cob" pathLength="1" d="M236 112 L262 20 L300 20"/>
    </svg>"""


def battery_svg(cls="P-batt"):
    return f"""<svg class="{cls}" viewBox="0 0 520 260" width="520" height="260">
      <rect x="8" y="8" width="460" height="244" rx="34" class="ink"/>
      <rect x="478" y="88" width="34" height="84" rx="10" fill="#111"/>
      <rect class="P-fill" x="34" y="34" width="408" height="192" rx="18" fill="@OK@"/>
    </svg>"""


# ── Frame 1 — hook ───────────────────────────────────────────────────────────
frame(1, "01-hook", "출근길 · AM 08:50",
f"""
    <svg class="P-line" viewBox="0 0 900 60" width="900" height="60">
      <path class="soft" d="M20 30 L880 30"/>
      <path class="cob" pathLength="1" d="M20 30 L880 30"/>
      <circle class="P-dot" cx="20" cy="30" r="14" fill="#fdfae7" stroke="#1e2bfa" stroke-width="6"/>
      <circle class="P-dot" cx="306" cy="30" r="14" fill="#fdfae7" stroke="#1e2bfa" stroke-width="6"/>
      <circle class="P-dot" cx="593" cy="30" r="14" fill="#fdfae7" stroke="#1e2bfa" stroke-width="6"/>
      <circle class="P-dot" cx="880" cy="30" r="18" fill="#1e2bfa"/>
    </svg>
    <div class="P-linelbl"><span class="P-l1">지옥철</span><span class="P-l2">도착 · 착석</span></div>
    <div class="P-cupwrap">{cup_svg()}</div>
    <div class="P-copy">
      <div class="P-sub P-muted">습관처럼, 일단</div>
      <div class="P-h1 P-hero"><span class="P-w P-a">아이스</span><br><span class="P-w P-b">아메리카노</span><span class="P-w P-qm">?</span></div>
    </div>
""",
"""
.P-line{position:absolute;left:96px;top:190px}
.P-linelbl{position:absolute;left:96px;top:250px;width:900px;font-size:30px;font-weight:600;color:#6b6b6b}
.P-l2{position:absolute;right:0;color:#1e2bfa;font-weight:700}
.P-cupwrap{position:absolute;left:250px;top:330px}
.P-copy{position:absolute;left:880px;top:390px;width:960px}
.P-sub{font-size:52px;margin-bottom:22px}
.P-hero{font-size:160px}
.P-qm{color:#1e2bfa;margin-left:12px;font-size:1em}
""",
"""
pop(".P-dot", 0.5, { stagger: 0.45, duration: 0.45 });
draw(".P-line .cob", 0.5, 1.8);
up(".P-l1", 0.9, { y: 20 });
up(".P-l2", 2.3, { y: 20 });
draw(".P-cup [pathLength]", 2.5, 0.9, { stagger: 0.15 });
tl.fromTo(q(".P-liquid"), { scaleY: 0, transformOrigin: "50% 100%" }, { scaleY: 1, duration: 0.8, ease: E }, 3.1);
pop(".P-ice", 3.3, { stagger: 0.12, duration: 0.5 });
up(".P-sub", 3.1);
up(".P-a", 4.0, { y: 60, duration: 0.8 });
up(".P-b", 4.5, { y: 60, duration: 0.8 });
up(".P-qm", 6.4, { y: 50, duration: 0.7 });
""")

# ── Frame 2 — heavy ──────────────────────────────────────────────────────────
frame(2, "02-heavy", "잠은 잤는데",
f"""
    <div class="P-left">
      <div class="P-pill soft P-night">어젯밤 · 푹 잠 ✓</div>
      <div class="P-battwrap">{battery_svg()}<div class="P-pct"><span class="P-num">100</span>%</div></div>
      <div class="P-times"><span class="P-t P-t1">09:00</span><span class="P-t P-t2">10:00</span><span class="P-t P-t3">11:00</span></div>
    </div>
    <div class="P-right">
      <div class="P-sub P-muted">오전부터 몸은</div>
      <div class="P-h1 P-hero">천근만근</div>
      <div class="P-weight"><i></i><i></i><i></i></div>
    </div>
""",
"""
.P-left{position:absolute;left:150px;top:250px;width:640px}
.P-night{margin-bottom:46px}
.P-battwrap{position:relative;width:520px;height:260px}
.P-pct{position:absolute;left:0;width:470px;top:300px;text-align:center;font-size:64px;font-weight:800;color:#1e2bfa;font-variant-numeric:tabular-nums}
.P-times{position:relative;margin-top:120px;width:470px;height:40px;font-size:30px;font-weight:600;color:#6b6b6b}
.P-t{position:absolute;top:0}
.P-t1{left:0}.P-t2{left:180px}.P-t3{right:0}
.P-right{position:absolute;left:960px;top:330px;width:880px}
.P-sub{font-size:56px;margin-bottom:10px}
.P-hero{font-size:230px;line-height:1.05}
.P-weight{display:flex;gap:26px;margin-top:34px;padding-left:12px}
.P-weight i{display:block;width:180px;height:12px;border-radius:6px;background:#111}
""",
"""
up(".P-night", 0.6);
up(".P-battwrap", 0.9);
const pct = { v: 100 };
const num = q(".P-num")[0];
up(".P-pct", 1.1, { y: 20 });
up(".P-t1", 2.6, { y: 16, duration: 0.5 });
up(".P-t2", 3.0, { y: 16, duration: 0.5 });
up(".P-t3", 3.4, { y: 16, duration: 0.5 });
tl.fromTo(q(".P-fill"), { scaleX: 1, transformOrigin: "0% 50%" }, { scaleX: 0.12, duration: 1.4, ease: "power2.inOut" }, 2.6);
tl.fromTo(pct, { v: 100 }, { v: 12, duration: 1.4, ease: "power2.inOut", onUpdate: () => { num.textContent = Math.round(pct.v); } }, 2.6);
tl.to(q(".P-fill"), { fill: "@WARN@", duration: 0.4 }, 3.5);
up(".P-sub", 3.3);
tl.fromTo(q(".P-hero"), { opacity: 0, y: -120 }, { opacity: 1, y: 0, duration: 0.55, ease: "power4.in" }, 3.8);
tl.fromTo(q(".P-hero"), { y: 0 }, { y: 10, duration: 0.18, ease: "power2.out" }, 4.35);
tl.to(q(".P-hero"), { y: 0, duration: 0.4, ease: E }, 4.53);
tl.fromTo(q(".P-weight i"), { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 0.6, ease: E, stagger: 0.12 }, 4.5);
""")

# ── Frame 3 — not only sleep ─────────────────────────────────────────────────
frame(3, "03-not-sleep", "만성 피로의 원인",
"""
    <div class="P-head">
      <div class="P-h1 P-title"><span class="P-w P-a">만성 피로,</span> <span class="P-w P-b">원인은?</span></div>
    </div>
    <div class="P-cards">
      <div class="P-card P-c1">
        <svg viewBox="0 0 120 120" width="120" height="120"><path class="ink" d="M78 18 A44 44 0 1 0 102 78 A36 36 0 0 1 78 18 Z"/></svg>
        <div class="P-cl">수면 부족</div>
        <svg class="P-strike" viewBox="0 0 600 40" width="600" height="40"><path class="cob" pathLength="1" d="M10 22 L590 18" style="stroke-width:10"/></svg>
      </div>
      <div class="P-card P-c2">
        <div class="P-qq">?</div>
        <div class="P-cl P-cl2">진짜 원인</div>
      </div>
    </div>
""",
"""
.P-head{position:absolute;left:96px;top:200px;width:1728px}
.P-title{font-size:120px}
.P-b{color:#111}
.P-cards{position:absolute;left:96px;top:470px;width:1728px;display:flex;gap:40px}
.P-card{position:relative;height:330px;display:flex;align-items:center;gap:40px;padding:0 64px}
.P-c1{width:900px}
.P-c2{width:788px;border-style:dashed;border-width:3px;justify-content:center}
.P-cl{font-size:96px;font-weight:800;letter-spacing:-0.03em}
.P-cl2{color:#1e2bfa}
.P-qq{font-size:150px;font-weight:800;color:#1e2bfa;line-height:1}
.P-strike{position:absolute;left:170px;top:146px;width:640px}
""",
"""
up(".P-a", 0.8, { y: 50 });
up(".P-b", 3.6, { y: 50 });
up(".P-c1", 4.6, { y: 60, duration: 0.8 });
draw(".P-strike [pathLength]", 5.8, 0.5);
tl.to(q(".P-c1 svg:first-child, .P-c1 .P-cl"), { opacity: 0.35, duration: 0.5, ease: "power2.out" }, 6.0);
up(".P-c2", 6.2, { y: 60, duration: 0.8 });
""")

# ── Frame 4 — eye strain (stage A: 범인 01) ───────────────────────────────────
STAGE_CSS = """
.P-tag{position:absolute;left:96px;top:170px;display:flex;align-items:center;gap:22px;font-size:44px;font-weight:800}
.P-art{position:absolute;left:96px;top:290px;width:900px;height:600px}
.P-label{position:absolute;left:1060px;top:380px;width:780px}
.P-label .P-h1{font-size:150px}
.P-label .P-sub{font-size:48px;margin-bottom:18px}
"""
frame(4, "04-eye-strain", "진짜 범인",
"""
    <div class="P-tag"><span class="P-step">1</span><span>눈</span></div>
    <div class="P-art">
      <div class="P-win P-xl P-card">
        <div class="P-bar"><i></i><i></i><i></i><b>엑셀</b></div>
        <div class="P-grid"></div>
      </div>
      <div class="P-win P-msg P-card">
        <div class="P-bar"><i></i><i></i><i></i><b>메신저</b></div>
        <div class="P-bub P-bub1"></div><div class="P-bub P-bub2"></div><div class="P-bub P-bub3"></div>
      </div>
      <svg class="P-eye" viewBox="0 0 220 130" width="220" height="130">
        <path class="ink" d="M10 65 Q110 -20 210 65 Q110 150 10 65 Z"/>
        <circle class="P-pupil" cx="110" cy="65" r="26" fill="#1e2bfa"/>
      </svg>
    </div>
    <div class="P-label">
      <div class="P-sub P-muted">하루 종일 번갈아 보며</div>
      <div class="P-h1"><span class="P-mark P-m">시각적 피로</span></div>
    </div>
""",
STAGE_CSS + """
.P-win{position:absolute;width:560px;height:380px;background:#fdfae7;overflow:hidden}
.P-win.P-card{background:#fbf8e6}
.P-xl{left:0;top:150px}
.P-msg{left:300px;top:230px}
.P-bar{height:54px;display:flex;align-items:center;gap:10px;padding:0 20px;border-bottom:1.5px solid rgba(35,64,245,0.2)}
.P-bar i{display:block;width:14px;height:14px;border-radius:50%;background:rgba(35,64,245,0.3)}
.P-bar b{margin-left:14px;font-size:26px;font-weight:700;color:#2340F5}
.P-grid{position:absolute;left:20px;right:20px;top:74px;bottom:20px;background-image:linear-gradient(rgba(27,27,58,0.18) 2px,transparent 2px),linear-gradient(90deg,rgba(27,27,58,0.18) 2px,transparent 2px);background-size:86px 46px}
.P-bub{position:absolute;height:52px;border-radius:26px}
.P-bub1{left:24px;top:86px;width:300px;background:rgba(35,64,245,0.14)}
.P-bub2{right:24px;top:160px;width:240px;background:#2340F5}
.P-bub3{left:24px;top:234px;width:360px;background:rgba(35,64,245,0.14)}
.P-eye{position:absolute;left:330px;top:0}
""",
"""
up(".P-tag", 0.35);
up(".P-xl", 1.2, { y: 50 });
up(".P-msg", 1.7, { y: 50 });
pop(".P-bub", 1.9, { stagger: 0.12, duration: 0.4 });
up(".P-eye", 2.4, { y: 20 });
// alternating focus: hard-cut z-order swaps + the pupil darting between windows
const xl = q(".P-xl")[0], msg = q(".P-msg")[0];
[2.6, 3.0, 3.4, 3.8].forEach((t, i) => {
  tl.set(i % 2 === 0 ? xl : msg, { zIndex: 3 }, t);
  tl.set(i % 2 === 0 ? msg : xl, { zIndex: 1 }, t);
  tl.to(q(".P-pupil"), { x: i % 2 === 0 ? -44 : 44, duration: 0.16, ease: "power3.out" }, t);
});
tl.to(q(".P-pupil"), { x: 0, duration: 0.3, ease: E }, 4.2);
up(".P-label .P-sub", 3.4);
up(".P-label .P-h1", 4.1, { y: 60, duration: 0.8 });
mark(".P-m", 4.7);
""")

# ── Frame 5 — brain overload (stage A: 범인 02) ───────────────────────────────
frame(5, "05-brain-overload", "진짜 범인",
"""
    <div class="P-tag"><span class="P-step">2</span><span>뇌</span></div>
    <div class="P-art">
      <div class="P-pill soft P-off">퇴근 후에도</div>
      <svg class="P-brain" viewBox="0 0 360 320" width="360" height="320">
        <path class="ink" pathLength="1" d="M180 40 C120 0 50 40 60 100 C10 120 10 200 70 220 C70 280 150 300 180 260 C210 300 290 280 290 220 C350 200 350 120 300 100 C310 40 240 0 180 40 Z"/>
        <path class="ink" pathLength="1" d="M180 40 L180 260"/>
        <path class="ink" pathLength="1" d="M110 120 Q140 140 120 170 M250 120 Q220 140 240 170"/>
      </svg>
      <div class="P-chip P-k1">보고서</div>
      <div class="P-chip P-k2">내일 회의</div>
      <div class="P-chip P-k3">미확인 메시지</div>
      <div class="P-chip P-k4">실적</div>
    </div>
    <div class="P-label">
      <div class="P-sub P-muted">업무 스트레스로</div>
      <div class="P-h1"><span class="P-mark P-m">뇌의 과부하</span></div>
      <div class="P-pill solid P-culprit">진짜 범인</div>
    </div>
""",
STAGE_CSS + """
.P-off{position:absolute;left:0;top:0}
.P-brain{position:absolute;left:270px;top:150px}
.P-chip{position:absolute;padding:14px 26px;border-radius:100px;background:rgba(30,43,250,0.08);border:1.5px solid rgba(30,43,250,0.2);color:#1e2bfa;font-size:32px;font-weight:700;white-space:nowrap}
.P-k1{left:40px;top:150px}
.P-k2{left:640px;top:190px}
.P-k3{left:0;top:420px}
.P-k4{left:660px;top:440px}
.P-culprit{margin-top:80px}
""",
"""
up(".P-tag", 0.35);
up(".P-off", 1.0);
draw(".P-brain [pathLength]", 1.9, 1.0, { stagger: 0.2 });
// worries orbit: each chip arrives on the beat, then drifts a finite arc around the head
[[".P-k1", 2.5], [".P-k2", 2.9], [".P-k3", 3.3], [".P-k4", 3.7]].forEach(([s, t], i) => {
  pop(s, t, { duration: 0.5 });
  const dx = [40, -30, 30, -40][i], dy = [30, 40, -30, -30][i];
  tl.to(q(s), { x: dx, y: dy, duration: 7.1 - t, ease: "sine.inOut" }, t + 0.5);
});
tl.to(q(".P-brain .ink"), { stroke: "#1e2bfa", duration: 0.5 }, 4.5);
up(".P-label .P-sub", 3.1);
up(".P-label .P-h1", 4.5, { y: 60, duration: 0.8 });
mark(".P-m", 5.0);
pop(".P-culprit", 5.5, { duration: 0.6 });
""")

# ── Frame 6 — body still, brain running a marathon ────────────────────────────
frame(6, "06-marathon", "몸 vs 뇌",
"""
    <div class="P-split">
      <div class="P-card P-side P-body">
        <div class="P-who">몸</div>
        <svg viewBox="0 0 260 300" width="208" height="240">
          <circle cx="120" cy="50" r="34" class="ink"/>
          <path class="ink" d="M120 88 L120 180 L200 180 L200 270 M60 130 L120 150 M40 180 L40 290 M40 180 L230 180"/>
        </svg>
        <div class="P-meter"><span class="P-num0">0</span> km</div>
        <div class="P-pill soft P-badge P-b1">가만히 앉아 있음</div>
      </div>
      <div class="P-card P-side P-mind">
        <div class="P-who P-cob">뇌</div>
        <svg viewBox="0 0 260 300" width="208" height="240">
          <circle cx="150" cy="44" r="34" class="cob"/>
          <path class="cob" d="M140 84 L110 170 L170 210 L150 290 M110 170 L50 230 M130 110 L200 140 L240 110 M130 110 L70 120 L40 160"/>
        </svg>
        <div class="P-meter P-cob"><span class="P-num">0</span> km</div>
        <div class="P-runbar"><i class="P-runfill"></i></div>
        <div class="P-pill solid P-badge P-b2">하루 종일 풀코스</div>
      </div>
    </div>
""",
"""
.P-split{position:absolute;left:96px;top:190px;width:1728px;height:700px;display:flex;gap:48px;perspective:1600px}
.P-side{position:relative;flex:1;height:680px;display:flex;flex-direction:column;align-items:center;padding-top:40px}
.P-who{font-size:84px;font-weight:800;letter-spacing:-0.03em}
.P-cob{color:#1e2bfa}
.P-side svg{margin-top:10px}
.P-meter{font-size:76px;font-weight:800;margin-top:6px;font-variant-numeric:tabular-nums}
.P-runbar{position:absolute;left:80px;right:80px;bottom:140px;height:16px;border-radius:8px;background:rgba(30,43,250,0.08);overflow:hidden}
.P-runfill{display:block;height:100%;width:100%;background:#1e2bfa;border-radius:8px}
.P-badge{position:absolute;bottom:40px}
.P-mind .P-meter{margin-bottom:40px}
""",
"""
tl.fromTo(q(".P-body"), { opacity: 0, x: -160, rotationY: 18 }, { opacity: 1, x: 0, rotationY: 6, duration: 0.9, ease: E }, 0.4);
tl.fromTo(q(".P-mind"), { opacity: 0, x: 160, rotationY: -18 }, { opacity: 1, x: 0, rotationY: -6, duration: 0.9, ease: E }, 3.0);
pop(".P-b1", 1.6, { duration: 0.5 });
tl.fromTo(q(".P-runfill"), { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 2.0, ease: "power2.inOut" }, 4.0);
const km = { v: 0 }, kmEl = q(".P-num")[0];
tl.fromTo(km, { v: 0 }, { v: 42.195, duration: 2.0, ease: "power2.inOut", onUpdate: () => { kmEl.textContent = km.v.toFixed(km.v >= 42.19 ? 3 : 1); } }, 4.0);
pop(".P-b2", 5.6, { duration: 0.5 });
tl.to(q(".P-body, .P-mind"), { rotationY: 0, duration: 0.8, ease: E }, 6.0);
""")

# ── Frame 7 — the answer: small breaks ───────────────────────────────────────
frame(7, "07-small-break", "그렇다면",
"""
    <div class="P-ask P-h1"><span class="P-w P-a">어떻게</span> <span class="P-w P-b">덜어낼까?</span></div>
    <div class="P-card P-gym">
      <svg viewBox="0 0 200 80" width="200" height="80"><path class="ink" d="M20 20 L20 60 M44 10 L44 70 M44 40 L156 40 M156 10 L156 70 M180 20 L180 60"/></svg>
      <span>거창한 헬스장 등록</span>
    </div>
    <div class="P-answer">
      <div class="P-sub P-muted">중요한 건 일상 속</div>
      <div class="P-h1 P-hero">작은 끊어내기</div>
      <div class="P-cut"><i class="P-cl"></i><i class="P-cr"></i></div>
    </div>
""",
"""
.P-ask{position:absolute;left:96px;top:180px;font-size:110px;transform-origin:0 0}
.P-gym{position:absolute;left:96px;top:290px;height:150px;display:flex;align-items:center;gap:30px;padding:0 50px;font-size:56px;font-weight:700}
.P-answer{position:absolute;left:96px;top:470px;width:1728px}
.P-sub{font-size:48px;margin-bottom:6px}
.P-hero{font-size:170px;line-height:1.15}
.P-cut{position:relative;height:14px;width:1000px;margin-top:84px}
.P-cut i{position:absolute;top:0;height:14px;width:494px;border-radius:7px;background:#1e2bfa}
.P-cl{left:0}.P-cr{left:506px}
""",
"""
up(".P-a", 0.4, { y: 50 });
up(".P-b", 2.3, { y: 50 });
tl.to(q(".P-ask"), { scale: 0.55, y: -30, color: "#6b6b6b", duration: 0.8, ease: E }, 4.1);
up(".P-gym", 4.6, { y: 50 });
tl.to(q(".P-gym"), { opacity: 0.3, scale: 0.86, transformOrigin: "0% 50%", duration: 0.6, ease: E }, 5.9);
up(".P-sub", 6.1);
up(".P-hero", 7.0, { y: 60, duration: 0.8 });
tl.fromTo(q(".P-cut i"), { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 0.5, ease: "power2.inOut", stagger: 0.25 }, 7.3);
// the snap: the continuous line breaks open in the middle
tl.to(q(".P-cl"), { x: -28, rotation: -3, duration: 0.45, ease: E }, 8.0);
tl.to(q(".P-cr"), { x: 28, rotation: 3, duration: 0.45, ease: E }, 8.0);
""")

# ── Frame 8 — 50 minutes, then 5 ─────────────────────────────────────────────
frame(8, "08-50-5", "실천 하나",
"""
    <div class="P-ringwrap">
      <svg class="P-ring" viewBox="0 0 520 520" width="520" height="520">
        <circle cx="260" cy="260" r="220" class="soft" style="stroke-width:34"/>
        <circle class="P-r50" cx="260" cy="260" r="220" fill="none" stroke="#1e2bfa" stroke-width="34" pathLength="55" stroke-dasharray="50 55" stroke-dashoffset="50" transform="rotate(-90 260 260)"/>
        <circle class="P-r5" cx="260" cy="260" r="220" fill="none" stroke="#111" stroke-width="34" pathLength="55" stroke-dasharray="4.6 55" stroke-dashoffset="-50.2" transform="rotate(-90 260 260)"/>
      </svg>
      <div class="P-center"><span class="P-num">0</span><small>분</small></div>
      <div class="P-pill solid P-five">+ 5분 쉬기</div>
    </div>
    <div class="P-right">
      <div class="P-devs">
        <svg class="P-mon" viewBox="0 0 240 200" width="240" height="200"><rect x="10" y="10" width="220" height="140" rx="14" class="ink"/><path class="ink" d="M120 150 L120 186 M70 188 L170 188"/></svg>
        <svg class="P-phone" viewBox="0 0 120 200" width="120" height="200"><rect x="10" y="10" width="100" height="180" rx="20" class="ink"/><path class="ink" d="M48 166 L72 166"/></svg>
        <svg class="P-x" viewBox="0 0 120 120" width="120" height="120"><path class="cob" pathLength="1" d="M20 20 L100 100"/><path class="cob" pathLength="1" d="M100 20 L20 100"/></svg>
      </div>
      <div class="P-far">
        <svg viewBox="0 0 700 200" width="700" height="200">
          <path class="soft" d="M0 190 L700 190"/>
          <path class="cob" pathLength="1" d="M0 190 L170 70 L280 150 L420 30 L560 140 L700 80"/>
          <path class="ink" d="M40 100 Q80 60 120 100 Q80 140 40 100 Z"/><circle cx="80" cy="100" r="10" fill="#1e2bfa"/>
        </svg>
        <div class="P-h1 P-farlbl">먼 곳 보기</div>
      </div>
    </div>
""",
"""
.P-ringwrap{position:absolute;left:150px;top:230px;width:520px;height:520px}
.P-center{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:8px;color:#1e2bfa;font-weight:800}
.P-num{font-size:190px;letter-spacing:-0.04em;font-variant-numeric:tabular-nums}
.P-center small{font-size:64px;margin-top:80px}
.P-five{position:absolute;left:300px;top:-30px;font-size:40px;white-space:nowrap}
.P-right{position:absolute;left:880px;top:220px;width:940px;height:680px}
.P-devs{position:relative;display:flex;align-items:flex-end;gap:50px;height:220px}
.P-x{position:absolute;left:140px;top:40px}
.P-far{position:absolute;left:0;top:300px}
.P-farlbl{font-size:120px;margin-top:20px}
""",
"""
const r50 = q(".P-r50")[0];
tl.fromTo(r50, { strokeDashoffset: 50 }, { strokeDashoffset: 0, duration: 1.4, ease: "power2.inOut" }, 1.0);
const n = { v: 0 }, el = q(".P-num")[0];
fade(".P-center", 0.9, { duration: 0.3 });
tl.fromTo(n, { v: 0 }, { v: 50, duration: 1.4, ease: "power2.inOut", onUpdate: () => { el.textContent = Math.round(n.v); } }, 1.0);
tl.fromTo(q(".P-r5"), { opacity: 0 }, { opacity: 1, duration: 0.4 }, 2.6);
pop(".P-five", 2.6, { duration: 0.6 });
up(".P-mon", 3.1);
up(".P-phone", 3.8);
draw(".P-x [pathLength]", 4.9, 0.35, { stagger: 0.12 });
tl.to(q(".P-mon, .P-phone"), { opacity: 0.3, duration: 0.5 }, 5.1);
draw(".P-far .cob", 5.6, 1.0);
up(".P-farlbl", 5.8, { y: 50 });
""")

# ── Frame 9 — stretch ────────────────────────────────────────────────────────
frame(9, "09-stretch", "실천 둘",
"""
    <div class="P-fig">
      <svg viewBox="0 0 600 640" width="600" height="640">
        <g class="P-o2">
          <circle cx="170" cy="560" r="14" fill="#1e2bfa"/><circle cx="430" cy="590" r="12" fill="#1e2bfa"/>
          <circle cx="300" cy="620" r="16" fill="#1e2bfa"/><circle cx="235" cy="600" r="10" fill="#1e2bfa"/>
          <circle cx="370" cy="570" r="13" fill="#1e2bfa"/>
        </g>
        <path class="ink" d="M190 540 L410 540 M210 540 L210 620 M390 540 L390 620"/>
        <path class="ink" d="M300 300 L300 520"/>
        <g class="P-upper">
          <g class="P-head">
            <circle class="P-glow" cx="300" cy="190" r="96" fill="rgba(30,43,250,0.12)"/>
            <circle cx="300" cy="196" r="58" class="ink"/>
          </g>
          <path class="P-shoulders ink" d="M210 304 L390 304"/>
          <g class="P-armL"><path class="ink" d="M212 304 L170 420 L222 476"/></g>
          <g class="P-armR"><path class="ink" d="M388 304 L430 420 L378 476"/></g>
        </g>
      </svg>
      <div class="P-dot P-dneck"><i></i>목</div>
      <div class="P-dot P-dsh"><i></i>어깨</div>
    </div>
    <div class="P-label">
      <div class="P-sub P-muted">앉은 채로, 가볍게</div>
      <div class="P-h1 P-hero">기지개 한 번</div>
      <div class="P-pill soft P-oxy">뇌에 산소 공급 ↑</div>
    </div>
""",
"""
.P-fig{position:absolute;left:180px;top:240px;width:600px;height:640px}
.P-dot{position:absolute;display:flex;align-items:center;gap:12px;font-size:34px;font-weight:700;color:#1e2bfa}
.P-dot i{display:block;width:22px;height:22px;border-radius:50%;background:#1e2bfa}
.P-dneck{left:330px;top:250px}
.P-dsh{left:410px;top:300px}
.P-label{position:absolute;left:960px;top:360px;width:880px}
.P-sub{font-size:52px;margin-bottom:14px}
.P-hero{font-size:150px}
.P-oxy{margin-top:80px;font-size:40px}
""",
"""
// hunched start: head dropped forward, shoulders rolled in
tl.set(q(".P-head"), { y: 34 }, 0);
tl.set(q(".P-shoulders"), { scaleX: 0.82, svgOrigin: "300 304" }, 0);
tl.set(q(".P-armL"), { x: 16, y: 10 }, 0);
tl.set(q(".P-armR"), { x: -16, y: 10 }, 0);
fade(".P-fig", 0.5, { duration: 0.6 });
up(".P-sub", 1.5);
up(".P-hero", 2.2, { y: 60, duration: 0.8 });
pop(".P-dneck", 3.2, { duration: 0.45 });
pop(".P-dsh", 3.6, { duration: 0.45 });
// open up: head lifts, shoulders widen, both arms sweep overhead
tl.to(q(".P-head"), { y: 0, duration: 1.0, ease: "power2.inOut" }, 4.2);
tl.to(q(".P-shoulders"), { scaleX: 1, svgOrigin: "300 304", duration: 1.0, ease: "power2.inOut" }, 4.2);
tl.to(q(".P-armL"), { x: 0, y: 0, rotation: 150, svgOrigin: "212 304", duration: 1.2, ease: "power2.inOut" }, 4.4);
tl.to(q(".P-armR"), { x: 0, y: 0, rotation: -150, svgOrigin: "388 304", duration: 1.2, ease: "power2.inOut" }, 4.4);
tl.to(q(".P-dneck, .P-dsh"), { opacity: 0, duration: 0.4 }, 5.4);
// oxygen rises into the head
tl.fromTo(q(".P-o2 circle"), { opacity: 0, y: 0 }, { opacity: 1, y: -340, duration: 1.6, ease: "power2.out", stagger: 0.15 }, 6.0);
tl.to(q(".P-o2 circle"), { opacity: 0, duration: 0.4, stagger: 0.15 }, 7.4);
tl.fromTo(q(".P-glow"), { opacity: 0, scale: 0.6, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, transformOrigin: "50% 50%", duration: 0.9, ease: E }, 6.9);
pop(".P-oxy", 6.9, { duration: 0.6 });
""")

# ── Frame 10 — not caffeine, real rest ───────────────────────────────────────
frame(10, "10-real-rest", "오늘부터는",
f"""
    <div class="P-left">
      <div class="P-battwrap">{battery_svg()}</div>
      <div class="P-cupmini">{cup_svg("P-cup")}
        <svg class="P-x" viewBox="0 0 200 200" width="200" height="200"><path class="cob" pathLength="1" d="M20 20 L180 180" style="stroke-width:12"/><path class="cob" pathLength="1" d="M180 20 L20 180" style="stroke-width:12"/></svg>
      </div>
      <div class="P-state" data-layout-allow-overlap><span class="P-s1">방전</span><span class="P-s2">충전 완료</span></div>
    </div>
    <div class="P-right">
      <div class="P-sub P-muted"><span class="P-w P-no">차가운 카페인 말고</span></div>
      <div class="P-h1 P-hero"><span class="P-w P-a">짧지만</span><br><span class="P-w P-b">진짜인</span> <span class="P-w P-c P-mark">휴식</span></div>
    </div>
""",
"""
.P-left{position:absolute;left:130px;top:250px;width:760px;height:640px}
.P-battwrap{position:absolute;left:0;top:60px}
.P-cupmini{position:absolute;left:560px;top:0;width:200px;height:270px}
.P-cupmini .P-cup{width:200px;height:270px}
.P-x{position:absolute;left:0;top:40px}
.P-state{position:absolute;left:0;top:380px;width:470px;height:80px;font-size:60px;font-weight:800;text-align:center}
.P-state span{position:absolute;left:0;right:0}
.P-s1{color:@WARN@}.P-s2{color:#1e2bfa}
.P-right{position:absolute;left:960px;top:300px;width:880px}
.P-sub{font-size:52px;margin-bottom:20px}
.P-hero{font-size:150px}
""",
"""
tl.set(q(".P-fill"), { scaleX: 0.12, fill: "@WARN@", transformOrigin: "0% 50%" }, 0);
up(".P-battwrap", 0.5);
up(".P-s1", 1.0, { y: 20 });
fade(".P-cupmini", 2.6, { duration: 0.5 });
q(".P-cup [pathLength]").forEach((p) => { p.style.strokeDashoffset = "0"; });
up(".P-no", 2.6);
draw(".P-x [pathLength]", 3.7, 0.4, { stagger: 0.12 });
tl.to(q(".P-cupmini .P-cup"), { opacity: 0.3, duration: 0.5 }, 3.8);
up(".P-a", 4.2, { y: 60, duration: 0.8 });
up(".P-b", 4.7, { y: 60, duration: 0.8 });
up(".P-c", 5.2, { y: 60, duration: 0.8 });
mark(".P-c", 5.8);
tl.to(q(".P-fill"), { scaleX: 1, fill: "@OK@", duration: 1.6, ease: "power2.inOut" }, 5.2);
tl.to(q(".P-s1"), { opacity: 0, y: -20, duration: 0.4 }, 6.2);
up(".P-s2", 6.4, { y: 20 });
""")

# ── Frame 11 — cheer (final; the only exit) ──────────────────────────────────
frame(11, "11-cheer", "오늘도 수고하셨습니다",
"""
    <svg class="P-rings" viewBox="0 0 1920 1080" width="1920" height="1080">
      <circle class="P-ring" cx="960" cy="470" r="220" fill="none" stroke="rgba(30,43,250,0.18)" stroke-width="3"/>
      <circle class="P-ring" cx="960" cy="470" r="360" fill="none" stroke="rgba(30,43,250,0.13)" stroke-width="3"/>
      <circle class="P-ring" cx="960" cy="470" r="500" fill="none" stroke="rgba(30,43,250,0.09)" stroke-width="3"/>
      <circle class="P-ring" cx="960" cy="470" r="640" fill="none" stroke="rgba(30,43,250,0.06)" stroke-width="3"/>
    </svg>
    <div class="P-center">
      <div class="P-sub P-muted"><span class="P-w P-a">오늘도</span> <span class="P-w P-b">버텨낸</span> <span class="P-w P-c">당신을</span></div>
      <div class="P-h1 P-hero">응원합니다</div>
      <div class="P-pill solid P-sub2">구독하고 함께 쉬어가요</div>
    </div>
""",
"""
.P-rings{position:absolute;left:0;top:0}
.P-center{position:absolute;left:0;right:0;top:260px;text-align:center}
.P-sub{font-size:64px}
.P-hero{font-size:180px;margin-top:10px}
.P-sub2{margin:84px auto 0;font-size:38px}
""",
"""
tl.fromTo(q(".P-ring"), { opacity: 0, scale: 0.7, transformOrigin: "960px 470px" }, { opacity: 1, scale: 1, duration: 1.6, ease: E, stagger: 0.18 }, 0.3);
up(".P-a", 0.5, { y: 40 });
up(".P-b", 1.9, { y: 40 });
up(".P-c", 2.4, { y: 40 });
up(".P-hero", 3.0, { y: 60, duration: 0.9 });
pop(".P-sub2", 4.4, { duration: 0.6 });
""", final=True)
