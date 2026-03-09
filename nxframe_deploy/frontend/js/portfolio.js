/* NXFRAME STUDIO — Portfolio JS */
'use strict';
const BG = ['pc1','pc2','pc3','pc4','pc5','pc6'];
let allProjects = [];
let currentFilter = 'all';
let dragSrcId = null;

// ── Load Projects ─────────────────────────────────────────────
async function loadProjects() {
  try {
    allProjects = await NX.api('/api/projects');
    renderProjects();
  } catch (e) {
    document.getElementById('p-grid').innerHTML =
      '<div class="p-empty"><div class="p-empty-icon">⚠️</div><div class="p-empty-text">Could not load projects</div></div>';
  }
}

function renderProjects() {
  const grid = document.getElementById('p-grid');
  const filtered = currentFilter === 'all' ? allProjects : allProjects.filter(p => p.category === currentFilter);
  if (!filtered.length) {
    grid.innerHTML = '<div class="p-empty"><div class="p-empty-icon">🗂️</div><div class="p-empty-text">No projects yet</div></div>';
    return;
  }
  grid.innerHTML = '';
  filtered.forEach((p, i) => {
    const bg = BG[i % 6];
    const card = buildCard(p, bg);
    grid.appendChild(card);
  });
}

function buildCard(p, bg) {
  const div = document.createElement('div');
  div.className = 'p-item';
  div.dataset.id  = p.id;
  div.dataset.cat = p.category;
  div.draggable = true;

  const imgHtml = p.image_url
    ? `<img class="p-img" src="${NX.API_BASE}${p.image_url}" alt="${p.title}">`
    : '';
  const phStyle = p.image_url ? 'style="display:none"' : '';

  div.innerHTML = `
    <div class="p-visual ${bg}">
      ${imgHtml}
      <div class="p-ph" ${phStyle}><div class="p-ph-icon">${p.icon}</div><div class="p-ph-text">${p.label}</div></div>
      <div class="p-overlay"><div class="p-ov-cat">${p.label}</div><div class="p-ov-title">${p.title}</div></div>
      <div class="p-actions${window.getAdmin() ? ' show' : ''}">
        <button class="p-act-btn upload-btn" title="Upload image">🖼</button>
        <button class="p-act-btn del" title="Delete">🗑</button>
      </div>
      <input type="file" accept="image/*" class="file-hidden">
    </div>
    <div class="p-info">
      <div><div class="p-info-title">${p.title}</div><div class="p-info-cat">${p.label}</div></div>
      <div class="p-arrow">→</div>
    </div>`;

  bindCard(div, p);
  return div;
}

function bindCard(card, p) {
  // Click → lightbox
  card.addEventListener('click', e => {
    if (e.target.closest('.p-act-btn,.file-hidden')) return;
    openLightbox(p);
  });

  // Upload image
  const uploadBtn = card.querySelector('.upload-btn');
  const fileInput = card.querySelector('.file-hidden');
  const visual    = card.querySelector('.p-visual');
  const ph        = card.querySelector('.p-ph');

  uploadBtn?.addEventListener('click', e => {
    e.stopPropagation();
    if (!window.getAdmin()) return;
    fileInput.click();
  });

  fileInput?.addEventListener('change', async () => {
    const file = fileInput.files[0]; if (!file) return;
    try {
      const fd = new FormData(); fd.append('file', file);
      const res = await fetch(`${NX.API_BASE}/api/projects/${p.id}/image`, {
        method: 'POST', credentials: 'include', body: fd,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      let img = visual.querySelector('.p-img');
      if (!img) { img = document.createElement('img'); img.className = 'p-img'; visual.insertBefore(img, visual.querySelector('.p-overlay')); }
      img.src = NX.API_BASE + data.image_url;
      ph.style.display = 'none';
      p.image_url = data.image_url;
      toast('✓ Image uploaded');
    } catch (err) { toast('✗ Upload failed: ' + err.message, true); }
  });

  // Delete
  card.querySelector('.del')?.addEventListener('click', async e => {
    e.stopPropagation();
    if (!window.getAdmin()) return;
    if (!confirm(`Delete "${p.title}"?`)) return;
    try {
      await NX.api(`/api/projects/${p.id}`, { method: 'DELETE', raw: true });
      card.style.opacity = '0'; card.style.transform = 'scale(.85)';
      setTimeout(() => { card.remove(); allProjects = allProjects.filter(x => x.id !== p.id); toast('Project deleted'); }, 380);
    } catch (err) { toast('✗ ' + err.message, true); }
  });

  // Drag to reorder
  card.addEventListener('dragstart', () => { dragSrcId = p.id; card.style.opacity = '.4'; });
  card.addEventListener('dragend',   () => { card.style.opacity = '1'; dragSrcId = null; });
  card.addEventListener('dragover',  e => { e.preventDefault(); card.style.borderColor = 'rgba(0,255,136,.5)'; });
  card.addEventListener('dragleave', () => { card.style.borderColor = ''; });
  card.addEventListener('drop', async e => {
    e.preventDefault(); card.style.borderColor = '';
    if (!window.getAdmin() || dragSrcId === p.id) return;
    // Swap orders
    const srcProject = allProjects.find(x => x.id === dragSrcId);
    const dstProject = p;
    const tmpOrder = srcProject.order;
    srcProject.order = dstProject.order;
    dstProject.order = tmpOrder;
    allProjects.sort((a, b) => a.order - b.order);
    renderProjects();
    try {
      await NX.api('/api/projects/reorder', {
        method: 'POST',
        body: JSON.stringify(allProjects.map(x => ({ id: x.id, order: x.order }))),
      });
      toast('✓ Order saved');
    } catch (err) { toast('✗ Reorder failed', true); }
  });
}

// ── Lightbox ──────────────────────────────────────────────────
const lb = document.getElementById('lightbox');
function openLightbox(p) {
  document.getElementById('lb-cat').textContent   = p.label;
  document.getElementById('lb-title').textContent = p.title;
  document.getElementById('lb-desc').textContent  = p.description || '';
  const vis = document.getElementById('lb-visual');
  vis.querySelectorAll('img').forEach(i => i.remove());
  const ph = document.getElementById('lb-ph');
  if (p.image_url) {
    const img = document.createElement('img'); img.src = NX.API_BASE + p.image_url; img.alt = p.title;
    vis.appendChild(img); ph.style.display = 'none';
  } else { ph.textContent = p.icon; ph.style.display = 'flex'; }
  lb.classList.add('on'); document.body.style.overflow = 'hidden';
}
document.getElementById('lb-close')?.addEventListener('click', () => { lb.classList.remove('on'); document.body.style.overflow = ''; });
lb?.addEventListener('click', e => { if (e.target === lb) { lb.classList.remove('on'); document.body.style.overflow = ''; } });
document.addEventListener('keydown', e => { if (e.key === 'Escape') { lb?.classList.remove('on'); document.body.style.overflow = ''; } });

// ── Filter ────────────────────────────────────────────────────
document.querySelectorAll('[data-filter]').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('[data-filter]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter = btn.dataset.filter;
    renderProjects();
  });
});

// ── Add Project Modal ─────────────────────────────────────────
const addModal = document.getElementById('add-modal');
let modalImgFile = null;

document.getElementById('add-project-btn')?.addEventListener('click', () => {
  if (!window.getAdmin()) return;
  addModal.classList.add('on'); document.body.style.overflow = 'hidden';
});
function closeAddModal() { addModal.classList.remove('on'); document.body.style.overflow = ''; resetModal(); }
document.getElementById('modal-close-btn')?.addEventListener('click', closeAddModal);
addModal?.addEventListener('click', e => { if (e.target === addModal) closeAddModal(); });

function resetModal() {
  ['m-title','m-desc'].forEach(id => { const el = document.getElementById(id); if(el) el.value = ''; });
  document.getElementById('m-cat').value = 'graphic';
  document.getElementById('drop-preview').style.display = 'none';
  modalImgFile = null;
}

const dropZone = document.getElementById('drop-zone');
const modalFile = document.getElementById('modal-file');
const dropPreview = document.getElementById('drop-preview');

function handleImgFile(file) {
  if (!file || !file.type.startsWith('image/')) return;
  modalImgFile = file;
  const r = new FileReader();
  r.onload = ev => { dropPreview.src = ev.target.result; dropPreview.style.display = 'block'; };
  r.readAsDataURL(file);
}
modalFile?.addEventListener('change', () => handleImgFile(modalFile.files[0]));
dropZone?.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag'); });
dropZone?.addEventListener('dragleave', () => dropZone.classList.remove('drag'));
dropZone?.addEventListener('drop', e => { e.preventDefault(); dropZone.classList.remove('drag'); handleImgFile(e.dataTransfer.files[0]); });

document.getElementById('modal-submit-btn')?.addEventListener('click', async () => {
  if (!window.getAdmin()) return;
  const title = document.getElementById('m-title').value.trim();
  const cat   = document.getElementById('m-cat').value;
  const desc  = document.getElementById('m-desc').value.trim();
  if (!title) { toast('✗ Title required', true); return; }
  try {
    const project = await NX.api('/api/projects', { method: 'POST', body: JSON.stringify({ title, category: cat, description: desc }) });
    if (modalImgFile) {
      const fd = new FormData(); fd.append('file', modalImgFile);
      const r = await fetch(`${NX.API_BASE}/api/projects/${project.id}/image`, { method: 'POST', credentials: 'include', body: fd });
      const d = await r.json(); if (r.ok) project.image_url = d.image_url;
    }
    allProjects.push(project);
    closeAddModal();
    renderProjects();
    toast(`✓ "${title}" added`);
  } catch (err) { toast('✗ ' + err.message, true); }
});

// ── Counters ──────────────────────────────────────────────────
function runCounter(el) {
  if (el.dataset.done) return; el.dataset.done = '1';
  const t = +el.dataset.target, s = el.dataset.suffix || '';
  const start = performance.now();
  (function tick(now) {
    const p = Math.min((now - start) / 1800, 1), e = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.floor(e * t) + s;
    if (p < 1) requestAnimationFrame(tick); else el.textContent = t + s;
  })(start);
}
function runInf(el) {
  if (el.dataset.done) return; el.dataset.done = '1';
  let n = 0; const iv = setInterval(() => {
    n += Math.floor(Math.random() * 50 + 20); el.textContent = n;
    if (n > 900) { clearInterval(iv); el.textContent = '∞'; }
  }, 60);
}
const statsObs = new IntersectionObserver(es => es.forEach(e => {
  if (e.isIntersecting) {
    e.target.querySelectorAll('[data-target]').forEach(runCounter);
    const inf = e.target.querySelector('#inf-stat'); if (inf) runInf(inf);
  }
}), { threshold: .3 });
const statsEl = document.querySelector('.about-stats');
if (statsEl) statsObs.observe(statsEl);

// ── Init ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadProjects();
  // Show admin-only elements when already admin
  document.getElementById('add-project-btn').style.display = window.getAdmin() ? 'flex' : 'none';
});
