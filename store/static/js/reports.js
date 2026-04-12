document.addEventListener('DOMContentLoaded', function () {
  const el      = document.getElementById('chartData');
  if (!el) return;

  const labels  = el.dataset.labels.split(',');
  const totals  = el.dataset.totals.split(',').map(Number);
  const maxTotal = Math.max(...totals, 1);
  const chart    = document.getElementById('barChart');
  if (!chart) return;

  chart.innerHTML = '';

  labels.forEach(function (label, i) {
    const total     = totals[i];
    const heightPct = Math.round((total / maxTotal) * 100);
    const isToday   = i === labels.length - 1;

    const col       = document.createElement('div');
    col.className   = 'bar-col';
    col.innerHTML   = `
      <div style="font-size:10px; color:var(--haruki-muted); margin-bottom:2px;">
        ${total > 0 ? '¥' + total.toLocaleString() : ''}
      </div>
      <div class="bar-fill ${isToday ? 'today' : ''}"
           style="height:${heightPct}%"></div>
      <div class="bar-label">${label}</div>
    `;
    chart.appendChild(col);
  });
});

// ── Top product bars ──
document.querySelectorAll('.top-product-bar').forEach(function (bar) {
  const qty = parseInt(bar.dataset.qty) || 0;
  const max = parseInt(bar.dataset.max) || 1;
  const pct = Math.round((qty / max) * 100);
  bar.style.width = pct + '%';
});