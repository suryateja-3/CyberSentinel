/* ==========================================================================
   CYBER SENTINEL - ABOUT PAGE
   Project overview, tech stack, API endpoint reference, team cards
   ========================================================================== */

export function renderAboutPage() {
  const page = document.createElement('div');
  page.className = 'view-page';

  /* Header card */
  const headerCard = document.createElement('div');
  headerCard.className = 'about-header-card';
  headerCard.innerHTML = `
    <div style="font-size:3rem;margin-bottom:1rem" aria-hidden="true">🛡️</div>
    <h1 class="about-title">About <span class="gradient-text" style="background:linear-gradient(135deg,var(--cyan-300),var(--blue-400));-webkit-background-clip:text;-webkit-text-fill-color:transparent">CyberSentinel</span></h1>
    <p class="about-description">
      CyberSentinel is an open-source AI-powered cybersecurity platform that unifies three threat-detection models —
      fake news classification, transaction fraud scoring, and URL phishing detection — into a single, clean interface
      designed to connect to a Flask ML REST API.
    </p>
    <div style="display:flex;gap:0.85rem;justify-content:center;flex-wrap:wrap;margin-top:1.75rem">
      <a href="https://github.com" target="_blank" rel="noopener noreferrer" class="btn btn-outline-cyan btn-sm" aria-label="View source on GitHub (opens in new tab)">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>
        View on GitHub
      </a>
      <span class="badge badge-info" style="padding:0.45rem 0.9rem;font-size:0.825rem">v1.0.0 — Demo Build</span>
    </div>
  `;
  page.appendChild(headerCard);

  /* Two-column layout */
  const twoCol = document.createElement('div');
  twoCol.style.cssText = 'display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-bottom:1.5rem';

  /* Tech Stack Card */
  const techCard = document.createElement('div');
  techCard.className = 'cyber-card';
  techCard.setAttribute('aria-label', 'Technology stack');
  techCard.innerHTML = `
    <div class="card-header">
      <h2 class="card-title"><span aria-hidden="true">⚙️</span> Tech Stack</h2>
    </div>
  `;

  const stacks = [
    { group: 'Frontend', items: ['Vanilla JavaScript (ES2022)', 'Vite (Build Tool)', 'CSS Custom Properties', 'JetBrains Mono / Outfit / Inter'] },
    { group: 'Backend (Flask)', items: ['Python 3.10+', 'Flask + Flask-CORS', 'scikit-learn / XGBoost', 'transformers (HuggingFace)', 'pandas / numpy'] },
    { group: 'ML Datasets', items: ['LIAR Dataset (Fake News)', 'Kaggle Credit Card Fraud', 'PhishTank + OpenPhish'] },
  ];

  stacks.forEach(s => {
    const groupEl = document.createElement('div');
    groupEl.style.marginBottom = '1.25rem';
    groupEl.innerHTML = `<div style="font-size:0.775rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.4px;margin-bottom:0.5rem">${s.group}</div>`;
    const pills = document.createElement('div');
    pills.className = 'tech-stack';
    s.items.forEach(item => {
      const pill = document.createElement('span');
      pill.className = 'tech-pill';
      pill.textContent = item;
      pills.appendChild(pill);
    });
    groupEl.appendChild(pills);
    techCard.appendChild(groupEl);
  });

  /* Architecture Card */
  const archCard = document.createElement('div');
  archCard.className = 'cyber-card';
  archCard.setAttribute('aria-label', 'System architecture overview');
  archCard.innerHTML = `
    <div class="card-header">
      <h2 class="card-title"><span aria-hidden="true">🏗️</span> Architecture</h2>
    </div>
    <div style="display:flex;flex-direction:column;gap:0.85rem">
      <div style="padding:1rem;border:1px solid var(--border-cyan);border-radius:var(--radius-md);background:var(--cyan-subtle);text-align:center">
        <div style="font-size:0.75rem;color:var(--text-muted);text-transform:uppercase;margin-bottom:0.35rem">Frontend</div>
        <div style="font-weight:700;color:var(--text-primary)">CyberSentinel UI</div>
        <div style="font-size:0.8rem;color:var(--cyan-300)">Vite + Vanilla JS</div>
      </div>
      <div style="text-align:center;color:var(--text-muted);font-size:0.85rem" aria-hidden="true">↕ REST API (JSON)</div>
      <div style="padding:1rem;border:1px solid var(--border-color);border-radius:var(--radius-md);background:rgba(15,23,42,0.5);text-align:center">
        <div style="font-size:0.75rem;color:var(--text-muted);text-transform:uppercase;margin-bottom:0.35rem">Backend</div>
        <div style="font-weight:700;color:var(--text-primary)">Flask REST API</div>
        <div style="font-size:0.8rem;color:var(--text-secondary)">Python • ML Models • JSON Responses</div>
      </div>
      <div style="text-align:center;color:var(--text-muted);font-size:0.85rem" aria-hidden="true">↕ Inference</div>
      <div style="padding:1rem;border:1px solid var(--border-color);border-radius:var(--radius-md);background:rgba(15,23,42,0.5);display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.5rem">
        ${['📰 NLP Model', '💳 XGBoost', '🔗 RF Classifier'].map(m => `<div style="text-align:center;font-size:0.8rem;color:var(--text-secondary);padding:0.5rem;background:var(--bg-surface-elevated);border-radius:var(--radius-sm)">${m}</div>`).join('')}
      </div>
    </div>
  `;

  twoCol.appendChild(techCard);
  twoCol.appendChild(archCard);
  page.appendChild(twoCol);

  /* API Endpoint Reference */
  const apiCard = document.createElement('div');
  apiCard.className = 'cyber-card accent-glow';
  apiCard.style.marginBottom = '1.5rem';
  apiCard.setAttribute('aria-label', 'Flask API endpoint reference');

  const endpoints = [
    { method: 'GET',  path: '/api/health',              desc: 'Health check — returns API status' },
    { method: 'POST', path: '/api/detect/fake-news',    desc: 'Fake news classification (text, title)' },
    { method: 'POST', path: '/api/detect/fraud',        desc: 'Fraud risk scoring (amount, merchant, location, device_id, hour)' },
    { method: 'POST', path: '/api/detect/url',          desc: 'URL phishing detection (url)' },
    { method: 'GET',  path: '/api/models/performance',  desc: 'Fetch live model metrics for all detectors' },
    { method: 'GET',  path: '/api/dashboard/stats',     desc: 'Dashboard aggregate statistics' },
  ];

  apiCard.innerHTML = `
    <div class="card-header">
      <h2 class="card-title"><span aria-hidden="true">🔌</span> Flask API Endpoints</h2>
      <span class="badge badge-info">Connect Your Backend</span>
    </div>
    <p style="font-size:0.875rem;color:var(--text-secondary);margin-bottom:1.25rem">
      Set <code style="background:rgba(6,182,212,0.15);color:var(--cyan-300);padding:0.15rem 0.4rem;border-radius:4px">VITE_API_BASE_URL=http://localhost:5000</code> in your <code style="background:rgba(6,182,212,0.15);color:var(--cyan-300);padding:0.15rem 0.4rem;border-radius:4px">.env</code> file.
    </p>
    <div class="endpoint-list" aria-label="API endpoint list"></div>
  `;

  const endpointList = apiCard.querySelector('.endpoint-list');
  endpoints.forEach(ep => {
    const div = document.createElement('div');
    div.className = 'endpoint-item';
    div.setAttribute('aria-label', `${ep.method} ${ep.path} — ${ep.desc}`);
    div.innerHTML = `
      <span class="method-badge method-${ep.method.toLowerCase()}">${ep.method}</span>
      <span class="endpoint-path">${ep.path}</span>
      <span class="endpoint-desc">${ep.desc}</span>
    `;
    endpointList.appendChild(div);
  });
  page.appendChild(apiCard);

  /* Expected Response Formats */
  const responseCard = document.createElement('div');
  responseCard.className = 'cyber-card';
  responseCard.style.marginBottom = '1.5rem';
  responseCard.setAttribute('aria-label', 'Expected API response formats');
  responseCard.innerHTML = `
    <div class="card-header">
      <h2 class="card-title"><span aria-hidden="true">📋</span> Expected API Response Format</h2>
    </div>
    <p style="font-size:0.875rem;color:var(--text-secondary);margin-bottom:1rem">
      Each detection endpoint should return a JSON object matching this structure:
    </p>
    <pre class="json-code-box" aria-label="Expected API response JSON structure">{
  "verdict": "SAFE" | "WARNING" | "DANGER",
  "confidence": 0.94,
  "description": "Human-readable explanation of the verdict",
  "features": [
    { "icon": "✅", "text": "Feature description", "type": "check" },
    { "icon": "⚠️", "text": "Risk signal found",   "type": "warn"  },
    { "icon": "🚨", "text": "Critical indicator",  "type": "bad"   }
  ],
  "raw": { /* optional: any additional model output */ }
}</pre>
  `;
  page.appendChild(responseCard);

  /* Team / Contributors */
  const teamCard = document.createElement('div');
  teamCard.className = 'cyber-card';
  teamCard.setAttribute('aria-label', 'Project contributors');
  teamCard.innerHTML = `
    <div class="card-header">
      <h2 class="card-title"><span aria-hidden="true">👥</span> Contributors</h2>
      <span class="badge badge-demo">Demo Placeholders</span>
    </div>
    <div class="team-grid"></div>
  `;

  const teamMembers = [
    { emoji: '👩‍💻', name: 'ML Engineer', role: 'Model Training & Evaluation' },
    { emoji: '🧑‍🔬', name: 'Data Scientist', role: 'Feature Engineering' },
    { emoji: '👨‍💻', name: 'Backend Dev', role: 'Flask API & Serving' },
    { emoji: '🎨', name: 'Frontend Dev', role: 'UI / UX Design' },
  ];

  const teamGrid = teamCard.querySelector('.team-grid');
  teamMembers.forEach(m => {
    const card = document.createElement('div');
    card.className = 'team-card';
    card.setAttribute('aria-label', `${m.name} — ${m.role}`);
    card.innerHTML = `
      <div class="team-avatar" aria-hidden="true">${m.emoji}</div>
      <div class="team-name">${m.name}</div>
      <div class="team-role">${m.role}</div>
    `;
    teamGrid.appendChild(card);
  });
  page.appendChild(teamCard);

  return page;
}
