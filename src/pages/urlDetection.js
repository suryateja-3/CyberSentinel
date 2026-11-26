/* ==========================================================================
   CYBER SENTINEL - URL DETECTION PAGE
   Connects to POST /api/detect/url
   ========================================================================== */

import { detectURL } from '../api/client.js';
import { createDemoBanner, createScanLoader, createConfidenceBar, createFeatureList, HistoryFeed, showToast } from '../components/ui.js';
import { validateURL, setFieldValidity } from '../utils/validation.js';

const PRESET_URLS = [
  { label: 'Safe URL',    value: 'https://github.com/tensorflow/tensorflow' },
  { label: 'Phishing',   value: 'http://paypa1-secure-verify.ru/account/login?token=abc123' },
  { label: 'Suspicious', value: 'http://bit.ly/3xR9zQ2?redirect=bankofamerica.phish.net' },
];

const history = new HistoryFeed(10);

export function renderURLPage() {
  const page = document.createElement('div');
  page.className = 'view-page';

  page.innerHTML = `
    <h1 class="page-title"><span aria-hidden="true">🔗</span> URL / Phishing Detection</h1>
    <p class="page-subtitle">Paste any URL to check for phishing, malware, or malicious redirect patterns.</p>
  `;

  page.appendChild(createDemoBanner('⚠️ DEMO MODE — Submits to POST /api/detect/url on your Flask backend. No real network scanning is performed here.'));

  const layout = document.createElement('div');
  layout.className = 'detection-layout';

  /* ── Input Panel ──────────────────────────────────────────────────── */
  const inputPanel = document.createElement('div');
  inputPanel.className = 'cyber-card accent-glow';

  inputPanel.innerHTML = `
    <div class="card-header">
      <h2 class="card-title"><span aria-hidden="true">🔍</span> URL Scanner</h2>
      <span class="badge badge-info">Lexical + ML Classifier</span>
    </div>

    <div class="preset-bar" aria-label="Sample URL presets">
      <span class="preset-title">Load sample:</span>
      <button class="btn-preset" id="url-preset-0" aria-label="Load safe URL sample">📗 Safe URL</button>
      <button class="btn-preset" id="url-preset-1" aria-label="Load phishing URL sample">📕 Phishing</button>
      <button class="btn-preset" id="url-preset-2" aria-label="Load suspicious URL sample">⚠️ Suspicious</button>
      <button class="btn-preset" id="url-clear" aria-label="Clear form">✕ Clear</button>
    </div>

    <form id="url-form" novalidate aria-label="URL detection form">
      <div class="form-group">
        <label class="form-label" for="url-input">
          URL to Scan
          <span class="form-hint">http:// or https://</span>
        </label>
        <input
          type="url"
          id="url-input"
          class="form-control mono-font"
          name="url"
          placeholder="https://example.com/path?query=value"
          maxlength="2048"
          required
          aria-required="true"
          aria-describedby="url-input-hint url-err"
          spellcheck="false"
          autocorrect="off"
          autocapitalize="off"
        />
        <span class="validation-msg" id="url-err" role="alert" aria-live="polite" style="display:none"></span>
        <div id="url-input-hint" class="sr-only">Enter the full URL including http:// or https:// to analyse it for phishing or malware</div>
      </div>

      <!-- URL breakdown preview -->
      <div id="url-breakdown" style="display:none;margin-bottom:1.25rem">
        <div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:0.4px">URL Parsed Preview</div>
        <div id="url-breakdown-inner" class="json-code-box" style="max-height:100px;font-size:0.78rem"></div>
      </div>

      <button type="submit" class="btn btn-cyan" id="url-submit" style="width:100%" aria-label="Scan URL for threats">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
        Scan URL
      </button>
    </form>

    <!-- Info: What we check -->
    <div style="margin-top:1.5rem;padding:1rem;border:1px solid var(--border-color);border-radius:var(--radius-md);background:rgba(15,23,42,0.5)">
      <p style="font-size:0.8rem;color:var(--text-muted);font-weight:600;text-transform:uppercase;margin-bottom:0.75rem">What The Classifier Checks</p>
      <ul style="list-style:none;display:flex;flex-direction:column;gap:0.4rem" aria-label="Classification features">
        <li style="font-size:0.825rem;color:var(--text-secondary)"><span style="color:var(--cyan-300)" aria-hidden="true">→</span> Domain age &amp; WHOIS reputation</li>
        <li style="font-size:0.825rem;color:var(--text-secondary)"><span style="color:var(--cyan-300)" aria-hidden="true">→</span> SSL certificate validity &amp; issuer</li>
        <li style="font-size:0.825rem;color:var(--text-secondary)"><span style="color:var(--cyan-300)" aria-hidden="true">→</span> Lexical patterns (typosquatting, brand impersonation)</li>
        <li style="font-size:0.825rem;color:var(--text-secondary)"><span style="color:var(--cyan-300)" aria-hidden="true">→</span> URL length, special characters, redirect depth</li>
        <li style="font-size:0.825rem;color:var(--text-secondary)"><span style="color:var(--cyan-300)" aria-hidden="true">→</span> Known malicious URL blacklist lookup</li>
      </ul>
    </div>
  `;

  /* ── Result Panel ─────────────────────────────────────────────────── */
  const resultPanel = document.createElement('div');
  resultPanel.className = 'result-panel';

  const resultCard = document.createElement('div');
  resultCard.className = 'cyber-card accent-glow';
  resultCard.style.flex = '1';

  const idleState = document.createElement('div');
  idleState.className = 'result-idle';
  idleState.setAttribute('aria-label', 'No URL scanned yet');
  idleState.innerHTML = `
    <div class="result-idle-icon" aria-hidden="true">🔗</div>
    <p class="result-idle-text">Enter a URL above and click "Scan URL" to see the threat analysis.</p>
    <p style="font-size:0.8rem;color:var(--text-muted)">Results are provided by the Flask ML API</p>
  `;

  const resultOutput = document.createElement('div');
  resultOutput.className = 'result-content';
  resultOutput.style.display = 'none';
  resultOutput.setAttribute('aria-live', 'polite');

  resultCard.innerHTML = `<div class="card-header"><h2 class="card-title"><span aria-hidden="true">🛡️</span> Threat Analysis</h2></div>`;
  resultCard.appendChild(idleState);
  resultCard.appendChild(resultOutput);

  const historyCard = document.createElement('div');
  historyCard.className = 'cyber-card';
  historyCard.innerHTML = `<div class="card-header"><h2 class="card-title" style="font-size:0.95rem"><span aria-hidden="true">🕒</span> Scan History</h2></div>`;
  historyCard.appendChild(history.getEl());

  resultPanel.appendChild(resultCard);
  resultPanel.appendChild(historyCard);
  layout.appendChild(inputPanel);
  layout.appendChild(resultPanel);
  page.appendChild(layout);

  /* ── Wire Presets ──────────────────────────────────────────────────── */
  const urlInput = inputPanel.querySelector('#url-input');
  const breakdown = inputPanel.querySelector('#url-breakdown');
  const breakdownInner = inputPanel.querySelector('#url-breakdown-inner');

  PRESET_URLS.forEach((preset, i) => {
    inputPanel.querySelector(`#url-preset-${i}`).addEventListener('click', () => {
      urlInput.value = preset.value;
      urlInput.dispatchEvent(new Event('input'));
      setFieldValidity(urlInput, null);
    });
  });

  inputPanel.querySelector('#url-clear').addEventListener('click', () => {
    urlInput.value = '';
    breakdown.style.display = 'none';
    setFieldValidity(urlInput, null);
    idleState.style.display = '';
    resultOutput.style.display = 'none';
  });

  /* Live URL breakdown preview */
  urlInput.addEventListener('input', () => {
    const val = urlInput.value.trim();
    if (!val) { breakdown.style.display = 'none'; return; }
    try {
      const u = new URL(val);
      breakdown.style.display = 'block';
      breakdownInner.textContent = [
        `Protocol : ${u.protocol}`,
        `Host     : ${u.hostname}`,
        `Port     : ${u.port || '(default)'}`,
        `Path     : ${u.pathname}`,
        `Query    : ${u.search || '(none)'}`,
        `Length   : ${val.length} chars`,
      ].join('\n');
    } catch {
      breakdown.style.display = 'none';
    }
  });

  /* ── Submit ────────────────────────────────────────────────────────── */
  inputPanel.querySelector('#url-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const val = urlInput.value;
    const v   = validateURL(val);

    if (!v.valid) {
      setFieldValidity(urlInput, v.message);
      urlInput.focus();
      return;
    }
    setFieldValidity(urlInput, null);

    const submitBtn = inputPanel.querySelector('#url-submit');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span aria-hidden="true">⏳</span> Scanning…`;

    idleState.style.display = 'none';
    resultOutput.style.display = 'none';
    const loader = createScanLoader(['Parsing URL structure…', 'Checking domain reputation…', 'Analysing SSL certificate…', 'Running ML classifier…', 'Compiling threat report…']);
    resultCard.appendChild(loader.el);
    loader.start();

    try {
      const data = await detectURL({ url: val });

      loader.stop();
      loader.el.remove();

      renderURLResult(resultOutput, data, val);
      resultOutput.style.display = 'flex';

      const verdict = data.verdict || 'UNKNOWN';
      history.add({
        text: val,
        badge: { class: verdict === 'SAFE' ? 'badge-safe' : verdict === 'WARNING' ? 'badge-warning' : 'badge-danger', label: verdict },
      });

      showToast({ type: 'success', title: 'URL Scanned', body: `Verdict: ${verdict}` });

    } catch (err) {
      loader.stop();
      loader.el.remove();
      idleState.style.display = 'flex';
      showToast({ type: 'error', title: 'API Error', body: err.message });
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg> Scan URL`;
    }
  });

  return page;
}

function renderURLResult(container, data, url) {
  const verdict  = data.verdict || 'UNKNOWN';
  const conf     = typeof data.confidence === 'number' ? data.confidence * 100 : 0;
  const features = data.features || [];

  const verdictClass = verdict === 'SAFE' ? 'safe' : verdict === 'WARNING' ? 'warning' : 'danger';
  const verdictIcon  = verdictClass === 'safe' ? '✅' : verdictClass === 'warning' ? '⚠️' : '🚨';

  container.innerHTML = `
    <div class="result-verdict-banner ${verdictClass}" role="status" aria-live="assertive" aria-label="URL verdict: ${verdict}">
      <span class="verdict-icon" aria-hidden="true">${verdictIcon}</span>
      <div>
        <div class="verdict-label">${verdict === 'SAFE' ? 'SAFE' : verdict === 'WARNING' ? 'SUSPICIOUS' : 'MALICIOUS / PHISHING'}</div>
        <div class="verdict-description mono-font" style="font-size:0.78rem;word-break:break-all">${url.substring(0, 60)}${url.length > 60 ? '…' : ''}</div>
      </div>
    </div>
  `;

  container.appendChild(createConfidenceBar(conf, 'Threat Confidence'));

  if (features.length > 0) {
    const featTitle = document.createElement('h3');
    featTitle.style.cssText = 'font-size:0.875rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;margin-top:0.5rem';
    featTitle.textContent = 'Threat Indicators';
    container.appendChild(featTitle);
    container.appendChild(createFeatureList(features));
  }
}
