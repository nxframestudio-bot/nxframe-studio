/* NXFRAME STUDIO — Creative Updates JS */
'use strict';
let allUpdates = [];
let updFilter = 'all';

const CAT_CLASS = { trend:'cat-trend', tool:'cat-tool', technique:'cat-technique', inspiration:'cat-inspiration' };
const CAT_LABEL = { trend:'Trend', tool:'Tool / Software', technique:'Technique', inspiration:'Inspiration' };

async function loadUpdates() {
  try {
    allUpdates = await NX.api('/api/updates');
    renderUpdates();
  } catch (e) {
    document.getElementById('upd-grid').innerHTML =
      '<div class="p-empty"><div class="p-empty-icon">⚠️</div><div class="p-empty-text">Could not load updates</div></div>';
  }
}

function renderUpdates() {
  const grid = document.getElementById('upd-grid');
  const filtered = updFilter === 'all' ? allUpdates : allUpdates.filter(u => u.category === updFilter);
  if (!filtered.length) {
    grid.innerHTML = '<div class="p-empty"><div class="p-empty-icon">📰</div><div class="p-empty-text">No updates yet</div></div>';
    return;
  }
  grid.innerHTML = '';
  filtered.forEach(u => grid.appendChild(buildUpdateCard(u)));
}

function buildUpdateCard(u) {
  const div = document.createElement('div');
  div.className = 'update-card' + (u.is_pinned ? ' pinned' : '');
  const date = u.created_at ? new Date(u.created_at).toLocaleDateString('en-GB', { day:'numeric', month:'short', year:'numeric' }) : '';
  const tagsHtml = (u.tags || []).map(t => `<span class="upd-tag">${t.trim()}</span>`).join('');
  const linkHtml = u.source_url ? `<a href="${u.source_url}" target="_blank" class="upd-link">Read More →</a>` : '<span></span>';
  const isAdmin = window.getAdmin();

  div.innerHTML = `
    ${u.is_pinned ? '<div class="upd-pin">📌</div>' : ''}
    <span class="upd-cat ${CAT_CLASS[u.category] || ''}">${CAT_LABEL[u.category] || u.category}</span>
    <div class="upd-title">${u.title}</div>
    <div class="upd-summary">${u.summary}</div>
    ${tagsHtml ? `<div class="upd-tags">${tagsHtml}</div>` : ''}
    <div class="upd-footer">
      ${linkHtml}
      <div style="display:flex;align-items:center;gap:.8rem;">
        <span class="upd-date">${date}</span>
        <div class="upd-admin-btns${isAdmin ? ' show' : ''}">
          <button class="upd-adm-btn del" title="Delete">🗑</button>
        </div>
      </div>
    </div>`;

  div.querySelector('.del')?.addEventListener('click', async () => {
    if (!window.getAdmin()) return;
    try {
      await NX.api(`/api/updates/${u.id}`, { method: 'DELETE', raw: true });
      allUpdates = allUpdates.filter(x => x.id !== u.id);
      div.style.opacity = '0'; div.style.transform = 'scale(.9)';
      setTimeout(() => { div.remove(); }, 350);
      toast('Update removed');
    } catch (err) { toast('✗ ' + err.message, true); }
  });
  return div;
}

// ── Filter ────────────────────────────────────────────────────
document.querySelectorAll('[data-upd-filter]').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('[data-upd-filter]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    updFilter = btn.dataset.updFilter;
    renderUpdates();
  });
});

// ── Add Update Modal ──────────────────────────────────────────
const updModal = document.getElementById('upd-modal');
document.getElementById('add-update-btn')?.addEventListener('click', () => {
  if (!window.getAdmin()) return;
  updModal.classList.add('on'); document.body.style.overflow = 'hidden';
});
function closeUpdModal() { updModal.classList.remove('on'); document.body.style.overflow = ''; resetUpdForm(); }
document.getElementById('upd-modal-close')?.addEventListener('click', closeUpdModal);
updModal?.addEventListener('click', e => { if (e.target === updModal) closeUpdModal(); });
function resetUpdForm() {
  ['u-title','u-summary','u-url','u-tags'].forEach(id => { const el = document.getElementById(id); if(el) el.value = ''; });
  document.getElementById('u-cat').value = 'trend';
  document.getElementById('u-pinned').checked = false;
}

document.getElementById('upd-submit-btn')?.addEventListener('click', async () => {
  if (!window.getAdmin()) return;
  const title   = document.getElementById('u-title').value.trim();
  const summary = document.getElementById('u-summary').value.trim();
  if (!title || !summary) { toast('✗ Title and summary required', true); return; }
  try {
    const u = await NX.api('/api/updates', {
      method: 'POST',
      body: JSON.stringify({
        title, category: document.getElementById('u-cat').value,
        summary, source_url: document.getElementById('u-url').value.trim() || null,
        tags: document.getElementById('u-tags').value.trim() || null,
        is_pinned: document.getElementById('u-pinned').checked,
      }),
    });
    allUpdates.unshift(u);
    closeUpdModal();
    renderUpdates();
    toast(`✓ "${title}" posted`);
  } catch (err) { toast('✗ ' + err.message, true); }
});

// ── Init ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadUpdates();
  const addBtn = document.getElementById('add-update-btn');
  if (addBtn && window.getAdmin()) addBtn.style.display = 'inline-block';
});
