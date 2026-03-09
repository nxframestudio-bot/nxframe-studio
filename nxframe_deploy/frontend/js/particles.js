/* NXFRAME STUDIO — Particle Canvas */
(function() {
  const canvas = document.getElementById('particles-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, mX = 0, mY = 0;

  function resize() { W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }
  resize();
  window.addEventListener('resize', resize);
  document.addEventListener('mousemove', e => { mX = e.clientX; mY = e.clientY; });

  const pts = Array.from({ length: 100 }, () => ({
    x: Math.random() * window.innerWidth, y: Math.random() * window.innerHeight,
    vx: (Math.random() - .5) * .35, vy: (Math.random() - .5) * .35,
    r: Math.random() * 1.2 + .3, ph: Math.random() * Math.PI * 2,
  }));

  (function draw() {
    ctx.clearRect(0, 0, W, H);
    pts.forEach(p => {
      p.x += p.vx; p.y += p.vy; p.ph += .016;
      const alpha = .1 + Math.abs(Math.sin(p.ph)) * .38;
      const dx = p.x - mX, dy = p.y - mY, d = Math.hypot(dx, dy);
      if (d < 110) { p.x += dx / d * 1.8 * (110 - d) / 110; p.y += dy / d * 1.8 * (110 - d) / 110; }
      if (p.x < 0 || p.x > W) p.vx *= -1;
      if (p.y < 0 || p.y > H) p.vy *= -1;
      ctx.save(); ctx.globalAlpha = alpha; ctx.fillStyle = '#00ff88';
      ctx.shadowBlur = 5; ctx.shadowColor = '#00ff88';
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill(); ctx.restore();
    });
    for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++) {
      const dx = pts[i].x - pts[j].x, dy = pts[i].y - pts[j].y, d = Math.hypot(dx, dy);
      if (d < 75) {
        ctx.save(); ctx.globalAlpha = (1 - d / 75) * .07;
        ctx.strokeStyle = '#00ff88'; ctx.lineWidth = .5;
        ctx.beginPath(); ctx.moveTo(pts[i].x, pts[i].y); ctx.lineTo(pts[j].x, pts[j].y); ctx.stroke(); ctx.restore();
      }
    }
    requestAnimationFrame(draw);
  })();
})();
