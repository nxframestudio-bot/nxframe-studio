/* NXFRAME STUDIO — API Client
   After deploying backend to Railway, replace the URL below with your Railway URL
   e.g. https://nxframe-api.up.railway.app
*/
const API_BASE = 'REPLACE_WITH_RAILWAY_URL';

async function api(path, opts = {}) {
  const res = await fetch(API_BASE + path, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(opts.headers || {}) },
    ...opts,
  });
  if (opts.raw) return res;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
  return data;
}

async function apiForm(path, formData) {
  const res = await fetch(API_BASE + path, {
    method: 'POST', credentials: 'include', body: formData,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
  return data;
}

window.NX = { api, apiForm, API_BASE };
