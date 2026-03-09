/* NXFRAME STUDIO — Core JS (cursor, toast, auth, admin bar) */
'use strict';

// ── Cursor ────────────────────────────────────────────────────
const cur = document.getElementById('cursor');
const ring = document.getElementById('cursor-ring');
let cx = 0, cy = 0, rx = 0, ry = 0;

document.addEventListener('mousemove', e => {
  cx = e.clientX; cy = e.clientY;
  if (cur) cur.style.transform = `translate(${cx-5}px,${cy-5}px)`;
});
(function trackRing() {
  rx += (cx - rx) * .12; ry += (cy - ry) * .12;
  if (ring) ring.style.transform = `translate(${rx-19}px,${ry-19}px)`;
  requestAnimationFrame(trackRing);
})();
document.addEventListener('mouseover', e => {
  const over = e.target.closest('a,button,.p-item,.service-card,.card-item,.update-card');
  document.body.classList.toggle('hov', !!over);
});

// ── Toast ─────────────────────────────────────────────────────
const toastEl = document.getElementById('toast');
function toast(msg, isErr = false) {
  if (!toastEl) return;
  toastEl.textContent = msg;
  toastEl.className = 'toast' + (isErr ? ' err' : '');
  toastEl.classList.add('show');
  clearTimeout(toastEl._t);
  toastEl._t = setTimeout(() => toastEl.classList.remove('show'), 3000);
}
window.toast = toast;

// ── Scroll Reveal ─────────────────────────────────────────────
const ro = new IntersectionObserver(es => es.forEach(e => {
  if (e.isIntersecting) e.target.classList.add('in');
}), { threshold: .07 });
document.querySelectorAll('.reveal').forEach(el => ro.observe(el));

// ── Auth / Admin State ────────────────────────────────────────
let isAdmin = false;
window.getAdmin = () => isAdmin;

const loginOverlay = document.getElementById('login-overlay');
const adminBar     = document.getElementById('admin-bar');
const adminNavBtn  = document.getElementById('admin-nav-btn');
const badge        = document.getElementById('unread-badge');

function openLogin() {
  if (!loginOverlay) return;
  loginOverlay.classList.add('on');
  setTimeout(() => document.getElementById('pw-input')?.focus(), 350);
}
function closeLogin() {
  if (!loginOverlay) return;
  loginOverlay.classList.remove('on');
  const inp = document.getElementById('pw-input');
  if (inp) { inp.value = ''; inp.classList.remove('err'); }
  const err = document.getElementById('login-err');
  if (err) err.textContent = '';
}
window.openLogin = openLogin;
window.closeLogin = closeLogin;

async function attemptLogin() {
  const inp = document.getElementById('pw-input');
  const err = document.getElementById('login-err');
  if (!inp) return;
  try {
    await NX.api('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username: 'hcsavin', password: inp.value }),
    });
    isAdmin = true;
    closeLogin();
    enableAdmin();
    toast('🔓 Admin mode unlocked');
  } catch (e) {
    inp.classList.add('err');
    if (err) err.textContent = 'Incorrect password.';
    inp.value = '';
    setTimeout(() => { inp.classList.remove('err'); if(err) err.textContent=''; }, 2000);
  }
}

async function doLogout() {
  await NX.api('/api/auth/logout', { method: 'POST' }).catch(() => {});
  isAdmin = false;
  disableAdmin();
  toast('🔒 Logged out');
}

function enableAdmin() {
  isAdmin = true;
  adminBar?.classList.add('on');
  adminNavBtn?.classList.add('unlocked');
  if (adminNavBtn) adminNavBtn.textContent = '🔓 Admin';
  document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'flex');
  document.querySelectorAll('.p-actions').forEach(el => el.classList.add('show'));
  fetchUnread();
}
function disableAdmin() {
  isAdmin = false;
  adminBar?.classList.remove('on');
  adminNavBtn?.classList.remove('unlocked');
  if (adminNavBtn) adminNavBtn.textContent = '🔒 Admin';
  document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'none');
  document.querySelectorAll('.p-actions').forEach(el => el.classList.remove('show'));
  if (badge) { badge.textContent = ''; badge.classList.remove('show'); }
}

async function fetchUnread() {
  if (!isAdmin || !badge) return;
  try {
    const { count } = await NX.api('/api/contact/unread-count');
    badge.textContent = count;
    badge.classList.toggle('show', count > 0);
  } catch (e) {}
}
window.fetchUnread = fetchUnread;

async function checkSession() {
  try {
    const { authenticated } = await NX.api('/api/auth/status');
    if (authenticated) enableAdmin();
  } catch (e) {}
}

// ── Wire login UI ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('admin-nav-btn')?.addEventListener('click', () => {
    if (isAdmin) { toast('Already in admin mode'); return; }
    openLogin();
  });
  document.getElementById('login-close-btn')?.addEventListener('click', closeLogin);
  loginOverlay?.addEventListener('click', e => { if (e.target === loginOverlay) closeLogin(); });
  document.getElementById('login-submit')?.addEventListener('click', attemptLogin);
  document.getElementById('pw-input')?.addEventListener('keydown', e => { if (e.key === 'Enter') attemptLogin(); });
  document.getElementById('logout-btn')?.addEventListener('click', doLogout);
  document.getElementById('dash-btn')?.addEventListener('click', () => window.location.href = 'pages/dashboard.html');
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeLogin(); });
  checkSession();
  setInterval(fetchUnread, 30000);
});
