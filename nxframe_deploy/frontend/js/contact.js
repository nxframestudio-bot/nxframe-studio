/* NXFRAME STUDIO — Contact Form JS */
'use strict';
document.addEventListener('DOMContentLoaded', () => {
  const form   = document.getElementById('contact-form');
  const btn    = document.getElementById('form-submit-btn');

  form?.addEventListener('submit', async e => {
    e.preventDefault();
    const name  = document.getElementById('f-name').value.trim();
    const email = document.getElementById('f-email').value.trim();
    const type  = document.getElementById('f-type').value.trim();
    const msg   = document.getElementById('f-msg').value.trim();
    if (!name || !email || !msg) { toast('✗ Please fill in all required fields', true); return; }
    btn.disabled = true; btn.textContent = 'Sending...';
    try {
      await NX.api('/api/contact', {
        method: 'POST',
        body: JSON.stringify({ name, email, project_type: type, message: msg }),
      });
      btn.textContent = 'Sent ✓';
      btn.style.background = '#00cc6a';
      form.reset();
      setTimeout(() => { btn.textContent = 'Send Message →'; btn.style.background = ''; btn.disabled = false; }, 3000);
    } catch (err) {
      toast('✗ Failed to send. Try again.', true);
      btn.textContent = 'Send Message →'; btn.disabled = false;
    }
  });
});
