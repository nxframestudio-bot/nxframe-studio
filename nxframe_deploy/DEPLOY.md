# 🚀 NXFRAME STUDIO — Deploy Guide
### HC Savin · Vercel (Frontend) + Railway (Backend)

---

## What You Need
- GitHub account (free) — github.com
- Vercel account (free) — vercel.com
- Railway account (free) — railway.app
- Gmail App Password (for contact form emails)

Total time: **~15 minutes**

---

## STEP 1 — Push to GitHub

1. Go to **github.com** → click **New repository**
2. Name it `nxframe-studio` → Create repository
3. Open a terminal in this folder and run:

```bash
git init
git add .
git commit -m "NXFRAME STUDIO — Initial deploy"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/nxframe-studio.git
git push -u origin main
```

---

## STEP 2 — Deploy Backend to Railway

1. Go to **railway.app** → Login with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your `nxframe-studio` repo
4. Railway auto-detects the `Procfile` and starts building

### Add Environment Variables on Railway:
Click your service → **Variables** tab → Add these one by one:

| Variable | Value |
|----------|-------|
| `ADMIN_USERNAME` | `hcsavin` |
| `ADMIN_PASSWORD` | `NXFRAME.savin@adminLogin#200507` |
| `SECRET_KEY` | any long random string |
| `SMTP_USERNAME` | `nxframestudio@gmail.com` |
| `SMTP_PASSWORD` | your Gmail App Password |
| `SMTP_FROM_EMAIL` | `nxframestudio@gmail.com` |
| `CONTACT_RECEIVER_EMAIL` | `nxframestudio@gmail.com` |
| `DEBUG` | `False` |

5. Go to **Settings** → **Networking** → **Generate Domain**
6. Copy your Railway URL — looks like: `https://nxframe-studio-production.up.railway.app`

---

## STEP 3 — Update Frontend with Your Railway URL

Open `frontend/js/api.js` and replace:
```javascript
const API_BASE = 'REPLACE_WITH_RAILWAY_URL';
```
with your actual Railway URL:
```javascript
const API_BASE = 'https://nxframe-studio-production.up.railway.app';
```

Also update `api/config.py` — set `FRONTEND_URL` to your Vercel URL (you'll get this after Step 4, come back and update):
```python
FRONTEND_URL: str = "https://nxframe-studio.vercel.app"
```

Commit and push:
```bash
git add .
git commit -m "Add Railway backend URL"
git push
```

---

## STEP 4 — Deploy Frontend to Vercel

1. Go to **vercel.com** → Login with GitHub
2. Click **Add New Project** → Import `nxframe-studio`
3. Vercel auto-detects `vercel.json` settings
4. Set **Root Directory** to `frontend`
5. Click **Deploy** — done in ~30 seconds!
6. Copy your Vercel URL: `https://nxframe-studio.vercel.app`

### Add Environment Variable on Vercel (optional):
Go to Project Settings → Environment Variables:
| Name | Value |
|------|-------|
| `NEXT_PUBLIC_API_URL` | your Railway URL |

---

## STEP 5 — Update CORS on Railway

Go back to Railway → Variables → add:
```
FRONTEND_URL = https://nxframe-studio.vercel.app
```
(Use your actual Vercel URL)

Railway auto-redeploys. Done! ✅

---

## STEP 6 — Set Up Gmail App Password

1. Sign in to **myaccount.google.com**
2. Go to **Security** → turn on **2-Step Verification** (if not already on)
3. Search **App Passwords** in the search bar
4. Select app: **Mail** → Generate
5. Copy the 16-character password
6. Paste it into Railway as `SMTP_PASSWORD`

---

## ✅ Final Checklist

- [ ] Code pushed to GitHub
- [ ] Railway backend deployed + domain generated
- [ ] `frontend/js/api.js` updated with Railway URL
- [ ] Vercel frontend deployed
- [ ] `FRONTEND_URL` set on Railway (your Vercel URL)
- [ ] Gmail App Password added to Railway
- [ ] Visit your Vercel URL — portfolio loads
- [ ] Click 🔒 Admin → enter password → admin mode works
- [ ] Submit a test contact form → receive email

---

## 🔐 Admin Login

```
Password: NXFRAME.savin@adminLogin#200507
```

Click **🔒 Admin** in the nav → enter password → admin mode unlocks.
Click **📊 Dashboard** to manage everything.

---

## 📂 File Structure

```
nxframe-studio/               ← your GitHub repo root
├── Procfile                  ← tells Railway how to start backend
├── requirements.txt          ← Python dependencies
├── vercel.json               ← tells Vercel how to serve frontend
├── .gitignore
├── DEPLOY.md                 ← this file
│
├── api/                      ← FastAPI backend
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── auth.py
│   ├── email_service.py
│   ├── seed.py
│   ├── models/
│   ├── routers/
│   └── static/uploads/
│
└── frontend/                 ← Static website (Vercel)
    ├── index.html
    ├── css/main.css
    ├── js/
    │   ├── api.js  ← UPDATE with Railway URL
    │   ├── core.js
    │   ├── portfolio.js
    │   ├── updates.js
    │   ├── contact.js
    │   └── particles.js
    └── pages/
        └── dashboard.html
```

---

## 🆘 Troubleshooting

**Password says "incorrect" on deployed site**
→ Make sure `ADMIN_PASSWORD` is set correctly in Railway Variables (no extra spaces)

**CORS error in browser console**
→ Set `FRONTEND_URL` in Railway to your exact Vercel URL (including https://, no trailing slash)

**Contact form not sending email**
→ Check `SMTP_PASSWORD` in Railway — must be Gmail App Password (not your login password)
→ Make sure `SMTP_USERNAME` matches the Gmail account that generated the App Password

**Images not loading after upload**
→ Railway's free tier uses ephemeral storage (files reset on redeploy). For permanent images, upgrade to Railway Pro or use Cloudflare R2 / AWS S3.

---

*NXFRAME STUDIO © 2025 — HC Savin*
