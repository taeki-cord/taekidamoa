# -*- coding: utf-8 -*-
"""사고 사례·이달의 안전·점검표 페이지와 사이트맵을 만듭니다.

사용법 (저장소 맨 위 폴더에서):  python tools/build.py

- 글 내용은 tools/content.py 에서 고칩니다. 만들어진 html 을 직접 고치면 다음 빌드 때 덮어써집니다.
- index.html 과 로또번호/index.html 은 직접 고치는 파일입니다. 다만 그 안의
  <!-- @header --> … <!-- /@header -->, <!-- @footer --> … <!-- /@footer --> 구간은
  여기서 만든 공통 메뉴·꼬리말로 바뀝니다.
"""
import datetime
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from content import CASES, SEASONS, ROOMS, SITE, YT, HOME_SHORTS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today().isoformat()
BY_SLUG = {c['slug']: c for c in CASES}
SITE_NAME = '안전, 그리고 우리 가족'

NAV = [
    ('', '홈', 'home'),
    ('cases/', '사고에서 배우기', 'cases'),
    ('season/', '이달의 안전', 'season'),
    ('checklist/', '부모님 댁 점검표', 'checklist'),
    ('#call', '긴급 연락처', 'call'),
]

SHIELD = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true">'
          '<symbol id="shield-logo" viewBox="0 0 100 100"><path d="M50 4 L88 18 V48 C88 72 71 88 50 96 C29 88 12 72 12 48 V18 Z" fill="#ffd43b"/>'
          '<path d="M50 26 L74 46 H67 V70 H33 V46 H26 Z" fill="#3b7dd8"/>'
          '<path d="M50 66 C42 60 38 56 38 51.5 C38 48 40.5 46 43.5 46 C46 46 48 47.5 50 50 C52 47.5 54 46 56.5 46 C59.5 46 62 48 62 51.5 C62 56 58 60 50 66 Z" fill="#e8590c"/>'
          '</symbol></svg>')

esc = html.escape


def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s)


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


# ───────────── 공통 조각 ─────────────

def link(p, href):
    """메뉴 주소를 페이지 위치(p)에 맞게 바꿉니다"""
    if href == '#call':
        return p + 'index.html#call' if p else '#call'
    return (p + href) or './'


def header(p, current):
    """p: 맨 위 폴더까지의 상대 경로 ('' 또는 '../')"""
    cur = ' aria-current="page"'
    items = '\n'.join(
        f'        <li><a class="menu" href="{link(p, href)}"{cur if key == current else ""}>{label}</a></li>'
        for href, label, key in NAV)
    return f'''<header class="nav">
    <div class="wrap">
      <a href="{link(p, '')}" class="logo">안전, 그리고 <span>우리 가족</span></a>
      <ul>
{items}
      </ul>
      <a class="yt-nav" href="{YT}/shorts" target="_blank" rel="noopener">▶ 유튜브</a>
    </div>
  </header>'''


def footer(p, share_text):
    links = ''.join(f'<a href="{link(p, href)}">{label}</a>' for href, label, _ in NAV)
    links += f'<a href="{YT}?sub_confirmation=1" target="_blank" rel="noopener">유튜브 구독</a>'
    return f'''<footer>
    <div class="wrap">
      <nav class="foot-links" aria-label="사이트 메뉴">{links}</nav>
      <p>안전, 그리고 우리 가족 · 37년 산업안전 강사가 정리합니다 · 오늘도 무사히 퇴근하세요.</p>
      <button type="button" class="share-btn" data-share="{esc(share_text)}">💬 이 페이지 공유하기</button>
      <p class="share-msg" aria-live="polite"></p>
      <p class="foot-fun"><a href="{p}로또번호/">🍀 쉬어가는 코너: 행운 번호 뽑기</a></p>
    </div>
  </footer>
  {SHIELD}'''


def head(title, desc, path, p, image=None, ld=None, noindex=False):
    url = SITE + path
    image = image or SITE + 'og-image.png'
    big = image.endswith('og-image.png')
    ld_html = ''
    if ld:
        ld_html = '\n  <script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'
    robots = '\n  <meta name="robots" content="noindex" />' if noindex else ''
    size = ('\n  <meta property="og:image:width" content="1200" />'
            '\n  <meta property="og:image:height" content="630" />') if big else ''
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <link rel="canonical" href="{url}" />{robots}
  <link rel="icon" href="{p}favicon.svg" type="image/svg+xml" />
  <link rel="icon" href="{p}favicon-32.png" type="image/png" sizes="32x32" />
  <link rel="apple-touch-icon" href="{p}apple-touch-icon.png" />
  <meta name="theme-color" content="#3b7dd8" />
  <meta property="og:type" content="{'article' if ld and ld.get('@type') == 'Article' else 'website'}" />
  <meta property="og:site_name" content="{SITE_NAME}" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{image}" />{size}
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{p}assets/site.css" />{ld_html}
</head>'''


def short_card(c):
    label = strip_tags(c['card'].replace('<br />', ' ')).replace('“', '').replace('”', '')
    return f'''<button type="button" class="short" data-id="{c['video']}" aria-label="{esc(label)} (쇼츠 재생)">
          <span class="s-tag">사고에서 배우기</span>
          <strong class="s-title">{c['card']}</strong>
          <span class="s-brand"><svg viewBox="0 0 100 100" aria-hidden="true"><use href="#shield-logo" /></svg>안전, 그리고 <span>우리 가족</span></span>
          <span class="s-play" aria-hidden="true">▶</span>
        </button>'''


def case_card(c, p):
    lesson = c['lessons'][0][0]
    return f'''<a class="case" href="{p}cases/{c['slug']}.html">
          <span class="c-thumb" style="background-image:url(https://i.ytimg.com/vi/{c['video']}/hqdefault.jpg)" aria-hidden="true"></span>
          <span class="c-body">
            <span class="c-tag">{c['tag']} · {c['year']}</span>
            <h3>{esc(c['short'])}</h3>
            <p>교훈 — {esc(lesson)}</p>
          </span>
        </a>'''


def breadcrumb_ld(items):
    return {
        '@context': 'https://schema.org', '@type': 'BreadcrumbList',
        'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + u}
                            for i, (n, u) in enumerate(items)],
    }


def page(p, head_html, header_html, body, footer_html, scripts=''):
    return f'''{head_html}
<body>

  {header_html}

{body}

  {footer_html}

  <script src="{p}assets/site.js"></script>{scripts}
</body>
</html>
'''


# ───────────── 사고 사례 ─────────────

def build_case(c):
    p = '../'
    path = f"cases/{c['slug']}.html"
    title = f"{c['title']} | {SITE_NAME}"
    image = f"https://i.ytimg.com/vi/{c['video']}/hqdefault.jpg"
    ld = {
        '@context': 'https://schema.org', '@type': 'Article',
        'headline': c['title'], 'description': c['desc'], 'image': image,
        'datePublished': TODAY, 'dateModified': TODAY, 'inLanguage': 'ko',
        'author': {'@type': 'Organization', 'name': SITE_NAME, 'url': SITE},
        'publisher': {'@type': 'Organization', 'name': SITE_NAME, 'url': SITE},
        'mainEntityOfPage': SITE + path,
    }
    crumbs = breadcrumb_ld([('홈', ''), ('사고에서 배우기', 'cases/'), (c['short'], path)])
    what = '\n'.join(f'      <p>{t}</p>' for t in c['what'])
    why = '\n'.join(f'      <p>{t}</p>' for t in c['why'])
    facts = '\n'.join(f'        <div class="fact"><strong>{esc(n)}</strong><span>{esc(l)}</span></div>' for n, l in c['facts'])
    lessons = '\n'.join(f'          <li><b>{esc(h)}</b>{esc(t)}</li>' for h, t in c['lessons'])
    related = '\n        '.join(case_card(BY_SLUG[s], p) for s in c['related'] if s in BY_SLUG)
    sources = '\n'.join(f'        <li><a href="{u}" target="_blank" rel="noopener">{esc(n)}</a></li>' for n, u in c['sources'])
    share = f"{c['short']} 사고에서 배우는 안전 교훈 — {strip_tags(c['lead'])}\n가족·동료와 같이 보세요 👇"
    body = f'''  <section class="page-hero">
    <div class="wrap">
      <p class="crumbs"><a href="../">홈</a> › <a href="./">사고에서 배우기</a> › {esc(c['short'])}</p>
      <h1>{esc(c['title'])}</h1>
      <p>{esc(c['lead'])}</p>
      <p class="meta"><span>{c['year']}년</span><span>{esc(c['place'])}</span><span>{c['tag']}</span><span>읽는 데 약 3분</span></p>
    </div>
  </section>

  <section class="block">
    <div class="wrap article">
      <h2>무슨 일이 있었나</h2>
{what}
      <div class="facts">
{facts}
      </div>

      <h2>1분 영상으로 보기</h2>
      <div class="video-one">
        {short_card(c)}
      </div>

      <h2>왜 일어났나</h2>
{why}

      <h2>우리 집·일터에 주는 교훈</h2>
      <div class="lesson">
        <ol>
{lessons}
        </ol>
      </div>

      <h2>현장에서 드리는 한마디</h2>
      <p class="voice">{esc(c['voice'])}<small>— 37년 산업안전 강사, 안전, 그리고 우리 가족</small></p>

      <div class="cta-row">
        <button type="button" class="share-btn" data-share="{esc(share)}">💬 가족·동료에게 보내기</button>
        <p class="share-msg" aria-live="polite"></p>
      </div>
      <p class="cta-row"><a class="btn line" href="../checklist/">부모님 댁 안전 점검표 보기</a></p>

      <h2>함께 보면 좋은 사고</h2>
      <div class="cases">
        {related}
      </div>
      <a class="more-link" href="./">사고에서 배우기 전체 보기 →</a>

      <h2>참고 자료</h2>
      <ul class="sources">
{sources}
      </ul>
    </div>
  </section>'''
    out = page(p, head(title, c['desc'], path, p, image, ld), header(p, 'cases'), body,
               footer(p, share))
    out = out.replace('</head>', '  <script type="application/ld+json">' + json.dumps(crumbs, ensure_ascii=False) + '</script>\n</head>', 1)
    write(path, out)
    return path


def build_cases_index():
    p = '../'
    path = 'cases/'
    title = f'사고에서 배우기 — 세계 대형 사고의 원인과 교훈 | {SITE_NAME}'
    desc = ('챌린저호·컬럼비아호·체르노빌·테크노마트·실버브리지 등 국내외 대형 사고가 왜 일어났는지, '
            '우리 집과 일터에서 무엇을 배워야 하는지 37년 산업안전 강사가 쉽게 정리했습니다.')
    cards = '\n        '.join(case_card(c, p) for c in CASES)
    body = f'''  <section class="page-hero">
    <div class="wrap">
      <p class="crumbs"><a href="../">홈</a> › 사고에서 배우기</p>
      <h1>사고에서 <em>배우기</em></h1>
      <p>안전 수칙은 누군가의 사고 위에서 만들어졌습니다. 큰 사고가 왜 일어났는지 알면, 우리 집과 일터의 작은 위험이 보입니다.</p>
    </div>
  </section>

  <section class="block">
    <div class="wrap">
      <div class="cases">
        {cards}
      </div>
    </div>
  </section>'''
    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': '사고에서 배우기', 'url': SITE + path,
          'hasPart': [{'@type': 'Article', 'headline': c['title'], 'url': SITE + f"cases/{c['slug']}.html"} for c in CASES]}
    write('cases/index.html', page(p, head(title, desc, path, p, ld=ld), header(p, 'cases'), body,
                                   footer(p, '큰 사고에서 배우는 우리 집·일터 안전 교훈 모음이에요 👇')))
    return path


# ───────────── 이달의 안전 ─────────────

def months_nav(p, now=None):
    cur = ' class="now" aria-current="page"'
    return '<nav class="months" aria-label="월별 안전 수칙">' + ''.join(
        f'<a href="{p}season/{m}.html"{cur if m == now else ""}>{m}월</a>' for m in range(1, 13)) + '</nav>'


def build_season(m):
    p = '../'
    t, lead, items, rel = SEASONS[m]
    path = f'season/{m}.html'
    title = f'{m}월 안전 수칙 — {t} | {SITE_NAME}'
    desc = f'{m}월에 꼭 챙길 안전 수칙: ' + ', '.join(i for i, _ in items) + '. 왜 그래야 하는지까지 쉽게 정리했습니다.'
    rows = '\n'.join(f'''        <div class="item"><h3>{esc(i)}</h3><p>{esc(w)}</p></div>''' for i, w in items)
    share = f'{m}월 안전 수칙 — {t}\n· ' + '\n· '.join(i for i, _ in items) + '\n\n더 자세한 건 여기서 보세요 👇'
    prev_m, next_m = (m - 2) % 12 + 1, m % 12 + 1
    rel_html = ''
    if rel and rel in BY_SLUG:
        rel_html = f'''
      <h2 style="margin-top:48px">이 달에 함께 보면 좋은 사고</h2>
      <div class="cases">
        {case_card(BY_SLUG[rel], p)}
      </div>'''
    body = f'''  <section class="page-hero">
    <div class="wrap">
      <p class="crumbs"><a href="../">홈</a> › <a href="./">이달의 안전</a> › {m}월</p>
      <h1>{m}월 안전 수칙 — <em>{esc(t)}</em></h1>
      <p>{esc(lead)} 이번 달에 꼭 챙길 네 가지를 이유와 함께 정리했습니다.</p>
    </div>
  </section>

  <section class="block">
    <div class="wrap article">
      <div class="season-detail">
{rows}
      </div>
      <div class="cta-row" style="margin-top:20px">
        <button type="button" class="share-btn" data-share="{esc(share)}">💬 부모님께 보내드리기</button>
        <p class="share-msg" aria-live="polite"></p>
      </div>{rel_html}

      <h2 style="margin-top:48px">다른 달 안전 수칙</h2>
      {months_nav(p, m)}
      <p class="pager"><a href="{prev_m}.html">← {prev_m}월 · {esc(SEASONS[prev_m][0])}</a><a href="{next_m}.html">{next_m}월 · {esc(SEASONS[next_m][0])} →</a></p>
    </div>
  </section>'''
    crumbs = breadcrumb_ld([('홈', ''), ('이달의 안전', 'season/'), (f'{m}월', path)])
    write(path, page(p, head(title, desc, path, p, ld=crumbs), header(p, 'season'), body, footer(p, share)))
    return path


def build_season_index():
    p = '../'
    path = 'season/'
    title = f'월별 생활 안전 수칙 1월~12월 | {SITE_NAME}'
    desc = '빙판길·해빙기·산불·장마·폭염·태풍·명절·난방·김장까지, 1월부터 12월까지 달마다 꼭 챙겨야 할 생활 안전 수칙을 정리했습니다.'
    cards = '\n'.join(
        f'''        <a class="case" href="{m}.html" data-month="{m}">
          <span class="c-body">
            <span class="c-tag">{m}월</span>
            <h3>{esc(SEASONS[m][0])}</h3>
            <p>{esc(SEASONS[m][1])} {esc(SEASONS[m][2][0][0])} 외 3가지</p>
          </span>
        </a>''' for m in range(1, 13))
    body = f'''  <section class="page-hero">
    <div class="wrap">
      <p class="crumbs"><a href="../">홈</a> › 이달의 안전</p>
      <h1>달마다 다른 <em>위험</em>, 달마다 챙길 수칙</h1>
      <p>사고는 계절을 탑니다. 이번 달에 많이 나는 사고와 미리 챙길 것을 한 장씩 정리했습니다.</p>
    </div>
  </section>

  <section class="block">
    <div class="wrap">
      <div class="cases">
{cards}
      </div>
    </div>
  </section>'''
    script = '''
  <script>
    // 이번 달 카드를 맨 앞으로 옮기고 표시합니다 (한국 시간 기준)
    (function () {
      const m = new Date(Date.now() + 9 * 3600000).getUTCMonth() + 1;
      const card = document.querySelector('[data-month="' + m + '"]');
      if (!card) return;
      card.querySelector('.c-tag').textContent = m + '월 · 이번 달';
      card.style.borderColor = 'var(--accent)';
      card.parentNode.prepend(card);
    })();
  </script>'''
    write('season/index.html', page(p, head(title, desc, path, p), header(p, 'season'), body,
                                    footer(p, '1월부터 12월까지 달마다 챙길 생활 안전 수칙이에요 👇'), script))
    return path


# ───────────── 부모님 댁 점검표 ─────────────

def build_checklist():
    p = '../'
    path = 'checklist/'
    total = sum(len(r[3]) for r in ROOMS)
    title = f'부모님 댁 안전 점검표 — 방마다 체크하는 {total}가지 | {SITE_NAME}'
    desc = (f'현관·거실·주방·욕실·보일러실·비상 대비까지, 부모님 댁을 방마다 돌며 확인하는 안전 점검표 {total}가지. '
            '체크하면 점수가 나오고, 인쇄하거나 가족 단톡방에 공유할 수 있습니다.')
    rooms = []
    idx = 0
    for name, icon, why, items in ROOMS:
        rows = []
        for it in items:
            rows.append(f'          <label class="check-item"><input type="checkbox" data-i="{idx}" /><span>{esc(it)}</span></label>')
            idx += 1
        rooms.append(f'''      <div class="room">
        <h2>{icon} {esc(name)}</h2>
        <p class="why">{esc(why)}</p>
{chr(10).join(rows)}
      </div>''')
    body = f'''  <section class="page-hero">
    <div class="wrap">
      <p class="crumbs"><a href="../">홈</a> › 부모님 댁 점검표</p>
      <h1>부모님 댁 <em>안전 점검표</em></h1>
      <p>다음에 찾아뵐 때 이 페이지를 켜고 방마다 한 바퀴 돌아보세요. 20분이면 충분합니다. 체크한 내용은 이 기기에만 저장됩니다.</p>
    </div>
  </section>

  <section class="block" style="padding-top:24px">
    <div class="wrap article">
      <div class="sticky-score">
        <div class="progress-row" style="margin:0">
          <div class="bar"><div id="barFill"></div></div>
          <div id="score">0 / {total}</div>
        </div>
      </div>
{chr(10).join(rooms)}
      <div id="result"></div>
      <div class="cta-row no-print" style="margin-top:16px">
        <button type="button" class="share-btn" id="shareScore">💬 가족 단톡방에 결과 공유</button>
        <button type="button" class="print-btn" onclick="window.print()">🖨 인쇄하기</button>
      </div>
      <p class="share-msg" id="shareScoreMsg" aria-live="polite"></p>
      <button type="button" class="reset" id="resetBtn">처음부터 다시 하기</button>
      <p class="no-print" style="margin-top:28px">달마다 챙길 것도 있습니다 → <a href="../season/">이달의 안전 수칙 보기</a></p>
    </div>
  </section>'''
    script = f'''
  <script>
    const KEY = 'parents-check-v1';
    const TOTAL = {total};
    let state = [];
    try {{ state = JSON.parse(localStorage.getItem(KEY)) || []; }} catch (e) {{}}
    const boxes = document.querySelectorAll('.room input[type="checkbox"]');
    function render() {{
      let count = 0;
      boxes.forEach(b => {{
        const on = !!state[b.dataset.i];
        b.checked = on;
        b.closest('.check-item').classList.toggle('done', on);
        if (on) count++;
      }});
      document.getElementById('score').textContent = count + ' / ' + TOTAL;
      document.getElementById('barFill').style.width = Math.round(count / TOTAL * 100) + '%';
      const left = TOTAL - count;
      document.getElementById('result').textContent = left === 0
        ? '🎉 모든 항목을 확인했습니다. 1년에 한 번, 이맘때 다시 점검해 주세요.'
        : count === 0 ? '현관부터 시작해 보세요. 해당하는 항목에 체크하면 됩니다.'
        : '👍 ' + count + '개 확인 완료. 체크 안 된 ' + left + '개는 이번 방문 때 같이 챙겨드리면 좋습니다.';
    }}
    boxes.forEach(b => b.addEventListener('change', () => {{
      state[b.dataset.i] = b.checked;
      try {{ localStorage.setItem(KEY, JSON.stringify(state)); }} catch (e) {{}}
      render();
    }}));
    document.getElementById('resetBtn').addEventListener('click', () => {{
      state = [];
      try {{ localStorage.setItem(KEY, '[]'); }} catch (e) {{}}
      render();
    }});
    document.getElementById('shareScore').addEventListener('click', () => {{
      const missed = [];
      boxes.forEach(b => {{ if (!state[b.dataset.i]) missed.push(b.nextElementSibling.textContent); }});
      let text = '부모님 댁 안전 점검 결과: ' + document.getElementById('score').textContent;
      if (missed.length) text += '\\n\\n챙겨야 할 것:\\n· ' + missed.slice(0, 8).join('\\n· ') + (missed.length > 8 ? '\\n· 외 ' + (missed.length - 8) + '개' : '');
      sharePage(text + '\\n\\n점검표는 여기 👇', document.getElementById('shareScoreMsg'));
    }});
    render();
  </script>'''
    crumbs = breadcrumb_ld([('홈', ''), ('부모님 댁 점검표', path)])
    write('checklist/index.html', page(p, head(title, desc, path, p, ld=crumbs), header(p, 'checklist'), body,
                                       footer(p, '부모님 댁 안전 점검표예요. 다음에 찾아뵐 때 같이 한 바퀴 돌아봐요 👇'), script))
    return path


# ───────────── 직접 고치는 페이지에 공통 메뉴·꼬리말 넣기 ─────────────

def inject(rel, p, current, share_text):
    path = os.path.join(ROOT, rel)
    with open(path, encoding='utf-8') as f:
        src = f.read()
    def rep(name, content):
        nonlocal src
        pat = re.compile(r'<!-- @%s -->.*?<!-- /@%s -->' % (name, name), re.S)
        if not pat.search(src):
            raise SystemExit(f'{rel}: <!-- @{name} --> 표시를 찾지 못했습니다')
        src = pat.sub(lambda _: f'<!-- @{name} -->\n  {content}\n  <!-- /@{name} -->', src)
    rep('header', header(p, current))
    rep('footer', footer(p, share_text))
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(src)


def inject_home_cases():
    """첫 화면의 '사고에서 배우기' 카드와 쇼츠 카드를 content.py 기준으로 채웁니다."""
    path = os.path.join(ROOT, 'index.html')
    with open(path, encoding='utf-8') as f:
        src = f.read()
    cards = '\n        '.join(case_card(c, '') for c in CASES[:6])
    shorts = '\n        '.join(short_card(BY_SLUG[s]) for s in HOME_SHORTS)
    for name, content in (('cases', cards), ('shorts', shorts)):
        pat = re.compile(r'<!-- @%s -->.*?<!-- /@%s -->' % (name, name), re.S)
        if not pat.search(src):
            raise SystemExit(f'index.html: <!-- @{name} --> 표시를 찾지 못했습니다')
        src = pat.sub(lambda _: f'<!-- @{name} -->\n        {content}\n        <!-- /@{name} -->', src)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(src)


def build_seasons_js():
    """첫 화면 '이달의 안전'이 쓰는 데이터 (content.py 의 SEASONS 에서 자동 생성)"""
    data = {m: [t, lead, [i for i, _ in items]] for m, (t, lead, items, _) in SEASONS.items()}
    write('assets/seasons.js', '// 자동 생성 파일입니다. 내용은 tools/content.py 의 SEASONS 에서 고치세요.\n'
          'const SEASONS = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n')


def build_sitemap(paths):
    urls = ['', *paths]
    body = '\n'.join(f'''  <url>
    <loc>{SITE}{u}</loc>
    <lastmod>{TODAY}</lastmod>
  </url>''' for u in urls)
    write('sitemap.xml', f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{body}
</urlset>
''')


def main():
    paths = [build_cases_index()]
    paths += [build_case(c) for c in CASES]
    paths.append(build_season_index())
    paths += [build_season(m) for m in range(1, 13)]
    paths.append(build_checklist())
    inject('index.html', '', 'home', '생활 안전 수칙이랑 긴급 연락처를 한 페이지에 정리해 놓은 곳이에요. 가족들도 한 번씩 보세요 👇')
    inject_home_cases()
    inject('로또번호/index.html', '../', None, '재미로 뽑아보는 오늘의 행운 번호 🍀')
    build_seasons_js()
    build_sitemap(paths)
    print(f'완료: 페이지 {len(paths)}개 + 첫 화면 + 사이트맵')


if __name__ == '__main__':
    main()
