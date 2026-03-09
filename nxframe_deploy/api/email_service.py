"""NXFRAME STUDIO — Email Service"""
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from api.config import settings

async def _send(msg):
    if not settings.SMTP_PASSWORD:
        print("⚠️  Email skipped — SMTP_PASSWORD not configured")
        return False
    try:
        await aiosmtplib.send(
            msg, hostname=settings.SMTP_HOST, port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME, password=settings.SMTP_PASSWORD, start_tls=True,
        )
        return True
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

async def notify_new_contact(name, email, project_type, message):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📬 New Enquiry from {name} — NXFRAME STUDIO"
    msg["From"]    = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"]      = settings.CONTACT_RECEIVER_EMAIL
    msg["Reply-To"] = email
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>body{{font-family:Arial,sans-serif;background:#030a05;color:#e8fff2;margin:0;padding:0}}
.w{{max-width:600px;margin:0 auto;padding:32px 16px}}
.hdr{{background:#0a1a0e;border:1px solid rgba(0,255,136,.25);padding:32px;text-align:center;margin-bottom:16px}}
.logo{{font-size:28px;letter-spacing:8px;color:#00ff88;font-weight:900}}
.sub{{font-size:10px;letter-spacing:3px;color:#4a6b55;text-transform:uppercase;margin-top:6px}}
.card{{background:#0a1a0e;border:1px solid rgba(0,255,136,.12);padding:24px;margin-bottom:12px}}
.lbl{{font-size:10px;letter-spacing:3px;text-transform:uppercase;color:#00ff88;margin-bottom:6px}}
.val{{font-size:16px;color:#e8fff2;font-weight:600}}
.msg{{background:#080f0a;border-left:3px solid #00ff88;padding:18px;margin-top:8px;font-size:15px;line-height:1.75;color:rgba(232,255,242,.8);white-space:pre-wrap}}
a{{color:#00ff88}}</style></head><body><div class="w">
<div class="hdr"><div class="logo">NXFRAME</div><div class="sub">New Portfolio Enquiry</div></div>
<div class="card"><div class="lbl">From</div><div class="val">{name}</div></div>
<div class="card"><div class="lbl">Email</div><div class="val"><a href="mailto:{email}">{email}</a></div></div>
<div class="card"><div class="lbl">Project Type</div><div class="val">{project_type or 'Not specified'}</div></div>
<div class="card"><div class="lbl">Received</div><div class="val">{datetime.now().strftime('%d %B %Y — %H:%M')}</div></div>
<div class="card"><div class="lbl">Message</div><div class="msg">{message}</div></div>
</div></body></html>"""
    msg.attach(MIMEText(html, "html"))
    await _send(msg)

async def send_autoreply(name, email):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Thanks for reaching out — NXFRAME STUDIO"
    msg["From"]    = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"]      = email
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>body{{font-family:Arial,sans-serif;background:#030a05;color:#e8fff2;margin:0;padding:0}}
.w{{max-width:600px;margin:0 auto;padding:32px 16px}}
.hdr{{background:#0a1a0e;border:1px solid rgba(0,255,136,.25);padding:40px;text-align:center}}
.logo{{font-size:32px;letter-spacing:8px;color:#00ff88;font-weight:900}}
.body{{background:#0a1a0e;border:1px solid rgba(0,255,136,.1);padding:32px;margin-top:16px;line-height:1.8}}
.hl{{color:#00ff88;font-weight:700}} a{{color:#00ff88}}</style></head><body><div class="w">
<div class="hdr"><div class="logo">NXFRAME</div></div>
<div class="body">
<p>Hey <span class="hl">{name}</span>,</p>
<p>Your message has been received! I'll get back to you within <strong>24–48 hours</strong>.</p>
<p>Check out my latest work:<br>
📸 <a href="https://www.instagram.com/nxframe_studio?igsh=MXExc3RxaG8weXhkZg==">@nxframe_studio</a><br>
🎨 <a href="https://www.instagram.com/dude_visuals_7?igsh=MWpiajR3ZzJwaTl3dg==">@dude_visuals_7</a></p>
<p>Talk soon,<br><span class="hl">HC Savin</span><br>Creative Director, NXFRAME STUDIO</p>
</div></div></body></html>"""
    msg.attach(MIMEText(html, "html"))
    await _send(msg)
