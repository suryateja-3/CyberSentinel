/* ==========================================================================
   CYBER SENTINEL - DASHBOARD PAGE
   Overview stats, recent activity table, quick action links
   All values are clearly labelled as DEMO DATA
   ========================================================================== */

import { createDemoBanner } from '../components/ui.js';

/* ── DEMO DATA (clearly labelled) ────────────────────────────────── */
const DEMO_STATS = [
  { icon: '🔍', value: '1,248', label: 'Total Scans', trend: '+12 today', trendType: 'up' },
  { icon: '📰', value: '312',   label: 'Articles Analysed', trend: '+3 this hour', trendType: 'up' },
  { icon: '💳', value: '567',   label: 'Transactions Checked', trend: '+8 today', trendType: 'up' },
  { icon: '🔗', value: '369',   label: 'URLs Scanned', trend: '−1 from yesterday', trendType: 'down' },
];

const DEMO_RECENT = [
  { time: '09:31:04', type: '📰 Fake News', input: '"Scientists discover water on Mars surface near polar caps..."', verdict: 'SAFE',    score: '92%' },
  { time: '09:28:51', type: '🔗 URL Scan',  input: 'http://paypa1-verify.ru/account/login',                          verdict: 'DANGER',  score: '99%' },
  { time: '09:25:17', type: '💳 Fraud',      input: '$4,500 — Night-time ATM | New Device',                           verdict: 'WARNING', score: '61%' },
  { time: '09:21:44', type: '📰 Fake News', input: '"Government to ban all social media platforms by 2025..."',      verdict: 'DANGER',  score: '88%' },
  { time: '09:19:02', type: '🔗 URL Scan',  input: 'https://github.com/tensorflow/tensorflow',                       verdict: 'SAFE',    score: '97%' },
  { time: '09:14:33', type: '💳 Fraud',      input: '$12 — Starbucks | Known Device',                                verdict: 'SAFE',    score: '95%' },
];

const DEMO_THREATS = [
  { label: 'Phishing URLs',      count: 142, pct: 38.6, color: '#ef4444' },
  { label: 'Fake News Articles', count: 87,  pct: 27.9, color: '#f59e0b' },
  { label: 'Fraud Transactions', count: 64,  pct: 17.4, color: '#8b5cf6' },
  { label: 'Safe (Verified)',    count: 954, pct: 76.5, color: '#10b981' },
];

function getBadgeClass(verdict) {
  if (verdict === 'SAFE')    return 'badge-safe';
  if (verdict === 'DANGER')  return 'badge-danger';
  if (verdict === 'WARNING') return 'badge-warning';
  return 'badge-info';
}

export function renderDashboardPage(router) {
  const page = document.createElement('div');
  page.className = 'view-page';
  page.setAttribute('aria-label', 'Dashboard overview');

  /* Title */
  const titleEl = document.createElement('div');
  titleEl.innerHTML = `
    <h1 class="page-title">
      <span aria-hidden="true">📊</span> Dashboard
    </h1>
    <p class="page-subtitle">Platform overview and real-time scan activity</p>
  `;
  page.appendChild(titleEl);

  /* Demo Banner */
  page.appendChild(createDemoBanner());

  /* Stat Cards */
  const statsGrid = document.createElement('div');
  statsGrid.className = 'dashboard-stats-grid';
  statsGrid.setAttribute('role', 'list');
  statsGrid.setAttribute('aria-label', 'Summary statistics (demo data)');

  DEMO_STATS.forEach(stat => {
    const card = document.createElement('div');
    card.className = 'stat-card';
    card.setAttribute('role', 'listitem');
    card.innerHTML = `
      <div class="stat-card-icon" aria-hidden="true">${stat.icon}</div>
      <div class="stat-card-value" aria-label="${stat.value} ${stat.label}">${stat.value}</div>
      <div class="stat-card-label">${stat.label}</div>
      <div class="stat-card-trend trend-${stat.trendType}" aria-label="Trend: ${stat.trend}">
        ${stat.trendType === 'up' ? '↑' : '↓'} ${stat.trend}
      </div>
    `;
    statsGrid.appendChild(card);
  });
  page.appendChild(statsGrid);

  /* Main 2-column grid */
  const mainGrid = document.createElement('div');
  mainGrid.className = 'dashboard-grid';

  /* Recent Activity Table */
  const activityCard = document.createElement('div');
  activityCard.className = 'cyber-card accent-glow';
  activityCard.setAttribute('aria-label', 'Recent scan activity (demo data)');

  const tableRows = DEMO_RECENT.map(r => `
    <tr>
      <td class="mono-font" style="color:var(--text-muted)">${r.time}</td>
      <td>${r.type}</td>
      <td style="max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.8rem;color:var(--text-secondary)">${r.input}</td>
      <td><span class="badge ${getBadgeClass(r.verdict)}">${r.verdict}</span></td>
      <td class="mono-font" style="color:var(--cyan-300)">${r.score}</td>
    </tr>
  `).join('');

  activityCard.innerHTML = `
    <div class="card-header">
      <h2 class="card-title"><span aria-hidden="true">🕒</span> Recent Activity</h2>
      <span class="badge badge-demo">Demo Data</span>
    </div>
    <div style="overflow-x:auto">
      <table class="recent-activity-table" aria-label="Recent scan activity">
        <thead>
          <tr>
            <th scope="col">Time</th>
            <th scope="col">Type</th>
            <th scope="col">Input</th>
            <th scope="col">Verdict</th>
            <th scope="col">Confidence</th>
          </tr>
        </thead>
        <tbody>${tableRows}</tbody>
      </table>
    </div>
  `;

  /* Threat Breakdown */
  const threatCard = document.createElement('div');
  threatCard.className = 'cyber-card accent-glow';
  threatCard.setAttribute('aria-label', 'Threat type breakdown (demo data)');

  const barRows = DEMO_THREATS.map(t => `
    <div class="bar-row">
      <span class="bar-row-label">${t.label}</span>
      <div class="bar-track" role="progressbar" aria-valuenow="${t.pct}" aria-valuemin="0" aria-valuemax="100" aria-label="${t.label}: ${t.pct}%">
        <div class="bar-fill" style="width:0%;background:linear-gradient(90deg,${t.color}99,${t.color})" data-width="${t.pct}"></div>
      </div>
      <span class="bar-row-val">${t.count}</span>
    </div>
  `).join('');

  threatCard.innerHTML = `
    <div class="card-header">
      <h2 class="card-title"><span aria-hidden="true">⚠️</span> Threat Breakdown</h2>
      <span class="badge badge-demo">Demo Data</span>
    </div>
    <div class="bar-chart" aria-label="Threat type breakdown">${barRows}</div>
    <p style="font-size:0.75rem;color:var(--text-muted);margin-top:1.25rem">* Values represent synthetic demo data for UI demonstration.</p>
  `;

  mainGrid.appendChild(activityCard);
  mainGrid.appendChild(threatCard);
  page.appendChild(mainGrid);

  /* Quick Actions */
  const quickCard = document.createElement('div');
  quickCard.className = 'cyber-card';
  quickCard.innerHTML = `
    <div class="card-header">
      <h2 class="card-title"><span aria-hidden="true">⚡</span> Quick Actions</h2>
    </div>
    <div style="display:flex;gap:0.85rem;flex-wrap:wrap">
      <button class="btn btn-cyan" id="qaction-fn" aria-label="Go to Fake News Detection">📰 Fake News Detection</button>
      <button class="btn btn-outline-cyan" id="qaction-fr" aria-label="Go to Fraud Detection">💳 Fraud Detection</button>
      <button class="btn btn-outline-cyan" id="qaction-url" aria-label="Go to URL Detection">🔗 URL Detection</button>
      <button class="btn btn-secondary" id="qaction-perf" aria-label="Go to Model Performance">📈 Model Performance</button>
    </div>
  `;
  page.appendChild(quickCard);

  /* Animate bars on render */
  requestAnimationFrame(() => {
    setTimeout(() => {
      page.querySelectorAll('.bar-fill[data-width]').forEach(bar => {
        bar.style.width = bar.dataset.width + '%';
      });
    }, 100);
  });

  /* Quick action navigation */
  page.querySelector('#qaction-fn').addEventListener('click', () => router.navigate('fake-news'));
  page.querySelector('#qaction-fr').addEventListener('click', () => router.navigate('fraud'));
  page.querySelector('#qaction-url').addEventListener('click', () => router.navigate('url'));
  page.querySelector('#qaction-perf').addEventListener('click', () => router.navigate('performance'));

  return page;
}
