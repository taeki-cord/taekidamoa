// 모든 페이지가 같이 쓰는 기능: 공유 버튼, 쇼츠 카드 재생, 방문자 수 집계

// 안전 다짐 게시판·방문자 수 저장소 (Supabase REST API)
// 공개용(publishable) 키라서 페이지에 넣어도 됩니다. 읽기·쓰기 권한은 DB의 RLS 정책으로 제한돼 있습니다.
const SUPABASE_URL = 'https://fydyfkegmcazmldfhowf.supabase.co';
const SUPABASE_KEY = 'sb_publishable_KQORj--X7LpoHi7BzTyH-w_FyIm3ohQ';
const headers = { apikey: SUPABASE_KEY, 'Content-Type': 'application/json' };

// 공유하기: 휴대폰은 공유 창(카톡 등)을 띄우고, 안 되면 링크를 복사합니다.
// 공유 주소는 지금 보고 있는 페이지 주소 끝에 ?from=share 를 붙인 것입니다 (공유로 들어온 방문을 따로 집계)
function shareUrl() {
  const canon = document.querySelector('link[rel="canonical"]');
  return (canon ? canon.href : location.origin + location.pathname) + '?from=share';
}
async function sharePage(text, msgEl) {
  const url = shareUrl();
  if (navigator.share) {
    try { await navigator.share({ title: document.title, text, url }); return; }
    catch (e) { if (e.name === 'AbortError') return; }
  }
  const full = text + '\n' + url;
  try {
    await navigator.clipboard.writeText(full);
    if (msgEl) msgEl.textContent = '✅ 링크를 복사했습니다. 카톡 대화방에 붙여넣기 해주세요.';
  } catch (e) {
    window.prompt('아래 내용을 복사해서 보내주세요.', full);
  }
}
// data-share="보낼 문구" 가 붙은 버튼은 누르면 바로 공유됩니다. 바로 다음 .share-msg 에 안내가 뜹니다
document.querySelectorAll('[data-share]').forEach(btn => {
  btn.addEventListener('click', () => {
    const msg = btn.nextElementSibling && btn.nextElementSibling.classList.contains('share-msg') ? btn.nextElementSibling : null;
    sharePage(btn.dataset.share, msg);
  });
});

// 쇼츠 카드를 누르면 그 자리에 유튜브 플레이어를 띄웁니다 (처음부터 영상을 불러오지 않아 빠릅니다)
document.querySelectorAll('.short').forEach(card => {
  // 위쪽 절반에 실제 영상 장면(유튜브 썸네일)을 깔아서 영상이라는 걸 바로 알 수 있게 합니다
  const thumb = document.createElement('span');
  thumb.className = 's-thumb';
  thumb.setAttribute('aria-hidden', 'true');
  thumb.style.backgroundImage = 'url(https://i.ytimg.com/vi/' + card.dataset.id + '/hqdefault.jpg)';
  card.prepend(thumb);
  card.addEventListener('click', () => {
    const f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + card.dataset.id + '?autoplay=1&playsinline=1';
    f.title = card.getAttribute('aria-label').replace(' (쇼츠 재생)', '');
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    f.referrerPolicy = 'strict-origin-when-cross-origin';
    f.allowFullscreen = true;
    card.replaceWith(f);
  });
});

// 방문자 수: 같은 기기는 하루에 한 번만 셉니다 (새로고침이나 여러 페이지를 봐도 부풀지 않게)
function visitSource() {
  const from = new URLSearchParams(location.search).get('from');
  if (from === 'yt' || from === 'youtube') return 'youtube';
  if (from === 'share') return 'share';
  if (from === 'blog') return 'blog';
  const ref = document.referrer;
  if (!ref) return 'direct';
  if (ref.indexOf(location.origin + '/taekidamoa') === 0) return 'internal';
  if (/youtube\.com|youtu\.be/.test(ref)) return 'youtube';
  if (/blog\.naver\.com/.test(ref)) return 'blog';
  if (/google\.|naver\.com|daum\.net|bing\.com/.test(ref)) return 'search';
  return 'other';
}

const SHOW_VISITS_FROM = 100; // 누적 방문자가 이 숫자 이상일 때만 화면에 표시

// 주인 모드: 주소 끝에 ?owner=on 을 붙여 한 번 접속하면 이 기기·브라우저는 방문자 수에서 빠집니다.
// 해제는 ?owner=off. 주인 모드에서는 방문자 수가 100명 전이라도 항상 보입니다.
function isOwner() {
  const params = new URLSearchParams(location.search);
  const flag = params.get('owner');
  try {
    if (flag === 'on') localStorage.setItem('site-owner', '1');
    if (flag === 'off') localStorage.removeItem('site-owner');
  } catch (e) {}
  if (flag !== null) {
    // 주소창에서 ?owner=... 를 지워서 이 주소가 그대로 공유되지 않게 합니다
    params.delete('owner');
    const q = params.toString();
    history.replaceState(null, '', location.pathname + (q ? '?' + q : '') + location.hash);
  }
  try { return localStorage.getItem('site-owner') === '1'; } catch (e) { return flag === 'on'; }
}

async function countVisit() {
  const today = new Date().toLocaleDateString('ko-KR', { timeZone: 'Asia/Seoul' });
  const owner = isOwner();
  const src = visitSource();
  let already = false;
  try { already = localStorage.getItem('visit-day') === today; } catch (e) {}
  // 사이트 안에서 페이지를 옮겨 다닌 건 새 방문이 아닙니다
  const counted = !owner && !already && src !== 'internal';
  const record = s => fetch(SUPABASE_URL + '/rest/v1/rpc/record_visit', {
    method: 'POST',
    headers,
    body: JSON.stringify({ src: s, counted })
  });
  try {
    let res = await record(src);
    // DB가 'blog' 경로를 아직 모르면 '기타'로라도 셉니다
    if (!res.ok && src === 'blog') res = await record('other');
    if (!res.ok) throw new Error(res.status);
    const { today: t, total } = await res.json();
    if (counted) { try { localStorage.setItem('visit-day', today); } catch (e) {} }
    const el = document.getElementById('visits');
    if (!el) return; // 방문자 수는 첫 화면에만 표시합니다
    if (!owner && Number(total) < SHOW_VISITS_FROM) return; // 초반엔 숫자를 숨기고 집계만 합니다
    el.innerHTML = (owner ? '🔑 주인 모드 (내 방문은 제외)<br>' : '') +
      '👀 오늘 <strong></strong>명 · 누적 <strong></strong>명이 함께했습니다';
    const nums = el.querySelectorAll('strong');
    nums[0].textContent = Number(t).toLocaleString('ko-KR');
    nums[1].textContent = Number(total).toLocaleString('ko-KR');
  } catch (e) {
    // 집계 실패해도 페이지 이용에는 지장 없도록 조용히 넘어갑니다
  }
}
countVisit();

// 안전 다짐 게시판: class="pledge-board" 인 곳에 입력칸과 최근 다짐을 채웁니다.
// 첫 화면·사고 글·월별 페이지가 모두 같은 게시판(pledges 표)을 써서 글이 한곳에 모입니다.
//   data-limit="3"   보여줄 최근 다짐 개수
//   data-more="../#pledge"  있으면 아래에 '다짐 전체 보기' 링크
const PLEDGE_API = SUPABASE_URL + '/rest/v1/pledges';
const PLEDGE_EXAMPLES = [
  '딸 결혼식엔 두 발로 걸어 들어가겠습니다',
  '손주 안아줄 허리, 오늘부터 무릎 굽혀 듭니다',
  '“다녀올게” 약속은 “다녀왔어”로 지키겠습니다',
  '운전대 잡으면 카톡은 도착해서 봅니다',
  '한잔했으면 대리비가 제일 싼 보험입니다',
  '가스 밸브 확인 3초, 후회는 평생입니다',
  '“괜찮겠지” 한 번 참으면 가족이 평생 편합니다',
  '내가 다치면 우리 집 월급도 멈춥니다. 안전 먼저!',
  '퇴근길 “다 왔다” 싶을 때 한 번 더 천천히',
  '정년까지 다친 데 없이 웃으며 퇴직하겠습니다',
  '위험하다 싶으면 눈치 보지 않고 멈추겠습니다',
  '“전에도 괜찮았다”는 말, 이제 믿지 않겠습니다'
];

document.querySelectorAll('.pledge-board').forEach(board => {
  const limit = Number(board.dataset.limit) || 12;
  board.innerHTML = `
    <p class="pledge-count" hidden></p>
    <form class="pledge-form">
      <input name="who" maxlength="20" placeholder="이름 또는 별명" aria-label="이름 또는 별명" required />
      <input name="text" maxlength="100" placeholder="나의 안전 다짐 한 줄" aria-label="나의 안전 다짐 한 줄" required />
      <button class="btn" type="submit">내 다짐 남기기</button>
    </form>
    <div class="chips"><span>막막하시면 골라보세요 👉</span><div class="chip-list"></div></div>
    <p class="pledge-msg" aria-live="polite"></p>
    <div class="pledges"></div>` +
    (board.dataset.more ? `<a class="more-link" href="${board.dataset.more}">다른 분들의 다짐 더 보기 →</a>` : '');

  const form = board.querySelector('form');
  const msg = board.querySelector('.pledge-msg');
  const listEl = board.querySelector('.pledges');
  const countEl = board.querySelector('.pledge-count');

  // 예시 다짐: 누르면 입력칸에 자동으로 채워집니다
  PLEDGE_EXAMPLES.slice().sort(() => Math.random() - 0.5).slice(0, 3).forEach(text => {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'chip';
    chip.textContent = text;
    chip.addEventListener('click', () => { form.elements.text.value = text; form.elements.text.focus(); });
    board.querySelector('.chip-list').appendChild(chip);
  });

  function show(rows) {
    listEl.innerHTML = '';
    if (!rows.length) {
      msg.textContent = '아직 아무도 없습니다. 첫 번째 다짐의 주인공이 되어주세요!';
      return;
    }
    rows.forEach(r => {
      const card = document.createElement('div');
      card.className = 'pledge';
      const p = document.createElement('p');
      p.textContent = r.message;
      const small = document.createElement('small');
      small.textContent = r.name + ' · ' + new Date(r.created_at).toLocaleDateString('ko-KR');
      card.append(p, small);
      listEl.appendChild(card);
    });
  }

  async function load() {
    try {
      const res = await fetch(PLEDGE_API + '?select=name,message,created_at&order=created_at.desc&limit=' + limit,
        { headers: { ...headers, Prefer: 'count=exact' } });
      if (!res.ok) throw new Error(res.status);
      msg.textContent = '';
      show(await res.json());
      // 전체 개수는 Content-Range 머리글 끝 숫자 ("0-2/15" → 15)
      const total = Number((res.headers.get('Content-Range') || '').split('/')[1]);
      if (total >= 5) {
        countEl.textContent = '✍️ 지금까지 ' + total.toLocaleString('ko-KR') + '분이 안전 다짐을 남겼습니다';
        countEl.hidden = false;
      }
    } catch (e) {
      msg.textContent = '다짐 목록을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.';
    }
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = form.elements.who.value.trim();
    const message = form.elements.text.value.trim();
    if (!name || !message) return;
    const btn = form.querySelector('button');
    btn.disabled = true;
    try {
      const res = await fetch(PLEDGE_API, {
        method: 'POST',
        headers: { ...headers, Prefer: 'return=minimal' },
        body: JSON.stringify({ name, message })
      });
      if (!res.ok) throw new Error(res.status);
      form.elements.text.value = '';
      await load();
      msg.textContent = '감사합니다! 다짐이 등록됐습니다.';
    } catch (err) {
      msg.textContent = '등록에 실패했습니다. 잠시 후 다시 시도해 주세요.';
    } finally {
      btn.disabled = false;
    }
  });

  load();
});
