/* ==========================================================================
   CYBER SENTINEL - LANDING PAGE
   Hero Section, Feature Cards, Statistics Banner
   ========================================================================== */

export function renderLandingPage(router) {
  const page = document.createElement('div');
  page.className = 'landing-page';

  /* ── Hero ─────────────────────────────────────────────────────────── */
  const hero = document.createElement('section');
  hero.className = 'hero-section';
  hero.setAttribute('aria-label', 'Hero section');

  hero.innerHTML = `
    <div class="hero-tagline-badge" aria-label="AI-powered cybersecurity platform">
      <span aria-hidden="true">🛡️</span>
      <span>AI-Powered Cybersecurity Platform</span>
    </div>

    <h1 class="hero-title">
      Detect Threats.<br>
      <span class="gradient-text">Stay Protected.</span>
    </h1>

    <p class="hero-subtitle">
      CyberSentinel combines machine learning and real-time analysis to detect
      fake news, online fraud, and malicious URLs — before they cause harm.
    </p>

    <div class="hero-cta-group">
      <button class="btn btn-cyan" id="hero-launch-btn" aria-label="Launch dashboard">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><polyline points="13 2 13 9 20 9"/><path d="M6 21h12a2 2 0 0 0 2-2V7.6L14.4 2H6a2 2 0 0 0-2 2v15a2 2 0 0 0 2 2z"/></svg>
        Launch Dashboard
      </button>
      <button class="btn btn-outline-cyan" id="hero-about-btn" aria-label="Learn more about CyberSentinel">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        Learn More
      </button>
    </div>

    <div class="hero-mini-cards" aria-label="Platform capabilities">
      <div class="hero-mini-card" aria-label="Fake news detection feature">
        <span class="hero-mini-card-icon" aria-hidden="true">📰</span>
        <span>Fake News Detection</span>
      </div>
      <div class="hero-mini-card" aria-label="Fraud detection feature">
        <span class="hero-mini-card-icon" aria-hidden="true">💳</span>
        <span>Fraud Detection</span>
      </div>
      <div class="hero-mini-card" aria-label="URL phishing detection feature">
        <span class="hero-mini-card-icon" aria-hidden="true">🔗</span>
        <span>URL / Phishing Detection</span>
      </div>
      <div class="hero-mini-card" aria-label="Real-time threat scoring feature">
        <span class="hero-mini-card-icon" aria-hidden="true">⚡</span>
        <span>Real-Time Scoring</span>
      </div>
    </div>
  `;

  hero.querySelector('#hero-launch-btn').addEventListener('click', () => router.navigate('dashboard'));
  hero.querySelector('#hero-about-btn').addEventListener('click', () => router.navigate('about'));

  /* ── Stats Banner ─────────────────────────────────────────────────── */
  const statsBanner = document.createElement('section');
  statsBanner.className = 'stats-section';
  statsBanner.setAttribute('aria-label', 'Platform statistics');
  statsBanner.innerHTML = `
    <div class="stats-grid">
      <div class="stat-item">
        <div class="stat-value" aria-label="97.3 percent accuracy">97.3%</div>
        <div class="stat-label">Avg. Model Accuracy</div>
      </div>
      <div class="stat-item">
        <div class="stat-value" aria-label="3 detection models">3</div>
        <div class="stat-label">AI Detection Models</div>
      </div>
      <div class="stat-item">
        <div class="stat-value" aria-label="less than 200 milliseconds latency">&lt;200ms</div>
        <div class="stat-label">Inference Latency</div>
      </div>
      <div class="stat-item">
        <div class="stat-value" aria-label="open source">Open</div>
        <div class="stat-label">Source &amp; Extensible</div>
      </div>
    </div>
  `;

  /* ── Feature Cards ────────────────────────────────────────────────── */
  const featureSection = document.createElement('section');
  featureSection.className = 'feature-section';
  featureSection.setAttribute('aria-label', 'Platform features');

  const features = [
    {
      id: 'fake-news',
      icon: '📰',
      title: 'Fake News Detection',
      desc: 'Paste any article or headline. Our NLP classifier analyses linguistic patterns, sentiment anomalies, and source credibility signals to score credibility.',
      link: 'Try Detection →',
    },
    {
      id: 'fraud',
      icon: '💳',
      title: 'Online Fraud Detection',
      desc: 'Submit transaction metadata — amount, merchant, device, and location — and get an instant risk score powered by anomaly detection models.',
      link: 'Analyse Transaction →',
    },
    {
      id: 'url',
      icon: '🔗',
      title: 'URL / Phishing Detection',
      desc: 'Enter any URL and our classifier checks domain age, SSL certificates, redirect chains, and lexical patterns to flag phishing attempts.',
      link: 'Scan URL →',
    },
    {
      id: 'performance',
      icon: '📈',
      title: 'Model Performance',
      desc: 'View detailed accuracy, precision, recall, F1 scores, and confusion matrices for each deployed model — full transparency into ML performance.',
      link: 'View Metrics →',
    },
  ];

  featureSection.innerHTML = `
    <div class="section-heading">
      <h2>What CyberSentinel Can Do</h2>
    </div>
    <p class="section-subtext">Three specialised AI detection modules, unified in a single platform. Built to connect to a Flask ML backend.</p>
    <div class="features-grid" role="list" aria-label="Feature list"></div>
  `;

  const grid = featureSection.querySelector('.features-grid');
  features.forEach(f => {
    const card = document.createElement('div');
    card.className = 'feature-card';
    card.setAttribute('role', 'listitem');
    card.setAttribute('tabindex', '0');
    card.setAttribute('aria-label', `${f.title} — click to navigate`);
    card.innerHTML = `
      <div class="feature-icon" aria-hidden="true">${f.icon}</div>
      <h3 class="feature-title">${f.title}</h3>
      <p class="feature-desc">${f.desc}</p>
      <span class="feature-link-label">
        ${f.link}
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
      </span>
    `;
    const navigate = () => router.navigate(f.id);
    card.addEventListener('click', navigate);
    card.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); navigate(); } });
    grid.appendChild(card);
  });

  page.appendChild(hero);
  page.appendChild(statsBanner);
  page.appendChild(featureSection);

  return page;
}
