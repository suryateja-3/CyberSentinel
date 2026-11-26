/* ==========================================================================
   CYBER SENTINEL - SMS FRAUD DETECTION PAGE
   Connects to POST /api/detect/fraud
   ========================================================================== */

import { detectFraud } from '../api/client.js';
import { createDemoBanner, createScanLoader, createConfidenceBar, createFeatureList, HistoryFeed, showToast } from '../components/ui.js';
import { setFieldValidity, attachCharCounter } from '../utils/validation.js';

const PRESET_SMS = [
  {
    label: 'Safe SMS',
    text: 'Hey John, are we still meeting for coffee at 3pm today?',
  },
  {
    label: 'Phishing SMS',
    text: 'URGENT: Your bank account has been locked due to suspicious activity. Please verify your identity at http://secure-verify-auth.com/login immediately to avoid permanent suspension.',
  },
];

const history = new HistoryFeed(8);

export function renderFraudPage() {
  const page = document.createElement('div');
  page.className = 'view-page';

  page.innerHTML = `
    <h1 class="page-title"><span aria-hidden="true">💬</span> SMS Fraud Detection</h1>
    <p class="page-subtitle">Submit an SMS message to receive a real-time phishing and spam risk assessment.</p>
  `;

  page.appendChild(createDemoBanner('⚠️ DEMO MODE — This form submits to POST /api/detect/fraud.'));

  const layout = document.createElement('div');
  layout.className = 'detection-layout';

  /* ── Input Panel ──────────────────────────────────────────────────── */
  const inputPanel = document.createElement('div');
  inputPanel.className = 'cyber-card accent-glow';

  inputPanel.innerHTML = `
    <div class="card-header">
      <h2 class="card-title"><span aria-hidden="true">🔍</span> Message Details</h2>
      <span class="badge badge-info">LSTM Detector</span>
    </div>

    <div class="preset-bar" aria-label="Sample SMS presets">
      <span class="preset-title">Load sample:</span>
      <button class="btn-preset" id="fr-preset-0" aria-label="Load safe SMS sample">📗 Safe SMS</button>
      <button class="btn-preset" id="fr-preset-1" aria-label="Load phishing SMS sample">📕 Phishing</button>
      <button class="btn-preset" id="fr-clear" aria-label="Clear form">✕ Clear</button>
    </div>

    <form id="fr-form" novalidate aria-label="SMS fraud detection form">
      <div class="form-group">
        <label class="form-label" for="fr-text">
          SMS Message Text
          <span class="form-hint">Required</span>
        </label>
        <textarea id="fr-text" class="form-control" name="text"
          placeholder="Paste SMS text here..." rows="5"
          maxlength="1000"
          required aria-required="true" aria-describedby="fr-text-err fr-text-counter"
        ></textarea>
        <span id="fr-text-counter" class="char-counter" aria-live="polite">0 / 1000</span>
        <span class="validation-msg" id="fr-text-err" role="alert" aria-live="polite" style="display:none"></span>
      </div>

      <button type="submit" class="btn btn-cyan" id="fr-submit" style="width:100%" aria-label="Analyse SMS for fraud">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        Analyse Message
      </button>
    </form>
  `;

  /* ── Result Panel ─────────────────────────────────────────────────── */
  const resultPanel = document.createElement('div');
  resultPanel.className = 'result-panel';

  const resultCard = document.createElement('div');
  resultCard.className = 'cyber-card accent-glow';
  resultCard.style.flex = '1';

  const idleState = document.createElement('div');
  idleState.className = 'result-idle';
  idleState.setAttribute('aria-label', 'No analysis result yet');
  idleState.innerHTML = `
    <div class="result-idle-icon" aria-hidden="true">💬</div>
    <p class="result-idle-text">Paste an SMS message and submit to see the fraud risk assessment.</p>
  `;

  const resultOutput = document.createElement('div');
  resultOutput.className = 'result-content';
  resultOutput.style.display = 'none';
  resultOutput.setAttribute('aria-live', 'polite');

  resultCard.innerHTML = `<div class="card-header"><h2 class="card-title"><span aria-hidden="true">🔒</span> Risk Assessment</h2></div>`;
  resultCard.appendChild(idleState);
  resultCard.appendChild(resultOutput);

  const historyCard = document.createElement('div');
  historyCard.className = 'cyber-card';
  historyCard.innerHTML = `<div class="card-header"><h2 class="card-title" style="font-size:0.95rem"><span aria-hidden="true">🕒</span> Session History</h2></div>`;
  historyCard.appendChild(history.getEl());

  resultPanel.appendChild(resultCard);
  resultPanel.appendChild(historyCard);
  layout.appendChild(inputPanel);
  layout.appendChild(resultPanel);
  page.appendChild(layout);

  /* ── Presets ──────────────────────────────────────────────────────── */
  const textArea = inputPanel.querySelector('#fr-text');
  
  PRESET_SMS.forEach((preset, i) => {
    inputPanel.querySelector(`#fr-preset-${i}`).addEventListener('click', () => {
      textArea.value = preset.text;
      textArea.dispatchEvent(new Event('input'));
      setFieldValidity(textArea, null);
    });
  });

  inputPanel.querySelector('#fr-clear').addEventListener('click', () => {
    inputPanel.querySelector('#fr-form').reset();
    textArea.dispatchEvent(new Event('input'));
    setFieldValidity(textArea, null);
    idleState.style.display = '';
    resultOutput.style.display = 'none';
  });

  attachCharCounter(textArea, 1000);

  /* ── Submit ───────────────────────────────────────────────────────── */
  inputPanel.querySelector('#fr-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const text = textArea.value.trim();
    if (!text) {
        setFieldValidity(textArea, "SMS text cannot be empty.");
        return;
    }
    setFieldValidity(textArea, null);

    const submitBtn = inputPanel.querySelector('#fr-submit');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span aria-hidden="true">⏳</span> Analysing…`;

    idleState.style.display = 'none';
    resultOutput.style.display = 'none';
    const loader = createScanLoader(['Tokenizing text…', 'Evaluating sequential patterns…', 'Computing fraud score…']);
    resultCard.appendChild(loader.el);
    loader.start();

    try {
      const data = await detectFraud({ text });

      loader.stop();
      loader.el.remove();

      renderFraudResult(resultOutput, data, { text });
      resultOutput.style.display = 'flex';

      history.add({
        text: text.substring(0, 40) + '...',
        badge: { class: data.verdict === 'SAFE' ? 'badge-safe' : data.verdict === 'WARNING' ? 'badge-warning' : 'badge-danger', label: data.verdict },
      });

      showToast({ type: 'success', title: 'Risk Assessment Complete', body: `Risk Level: ${data.verdict}` });

    } catch (err) {
      loader.stop();
      loader.el.remove();
      idleState.style.display = 'flex';
      showToast({ type: 'error', title: 'API Error', body: err.message });
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg> Analyse Message`;
    }
  });

  return page;
}

function renderFraudResult(container, data, txnMeta) {
  const verdict = data.verdict || 'UNKNOWN';
  const conf    = typeof data.confidence === 'number' ? data.confidence * 100 : 0;
  const features = data.features || [];

  const verdictClass = verdict === 'SAFE' ? 'safe' : verdict === 'WARNING' ? 'warning' : 'danger';
  const verdictIcon  = verdictClass === 'safe' ? '✅' : verdictClass === 'warning' ? '⚠️' : '🚨';

  container.innerHTML = `
    <div class="result-verdict-banner ${verdictClass}" role="status" aria-live="assertive" aria-label="Fraud verdict: ${verdict}">
      <span class="verdict-icon" aria-hidden="true">${verdictIcon}</span>
      <div>
        <div class="verdict-label">${verdict === 'SAFE' ? 'LOW RISK' : verdict === 'WARNING' ? 'MEDIUM RISK' : 'HIGH RISK — SUSPICIOUS'}</div>
        <div class="verdict-description">Classification based on LSTM sequential analysis</div>
      </div>
    </div>
  `;

  container.appendChild(createConfidenceBar(conf, 'Risk Score'));

  if (features.length > 0) {
    const featTitle = document.createElement('h3');
    featTitle.style.cssText = 'font-size:0.875rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;margin-top:0.5rem';
    featTitle.textContent = 'Risk Factors';
    container.appendChild(featTitle);
    container.appendChild(createFeatureList(features));
  }
}
