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
