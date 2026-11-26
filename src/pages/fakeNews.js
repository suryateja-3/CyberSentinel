/* ==========================================================================
   CYBER SENTINEL - FAKE NEWS DETECTION PAGE
   Connects to POST /api/detect/fake-news and POST /api/verify/evidence
   Features: Real/Fake/Uncertain verdict, actual probabilities, live news search,
             real-world evidence verification, and source transparency.
   ========================================================================== */

import { detectFakeNews, verifyEvidence, checkApiHealth, checkModelStatus } from '../api/client.js';
import { createScanLoader, createConfidenceBar, createFeatureList, HistoryFeed, showToast } from '../components/ui.js';
import { validateArticleText, setFieldValidity, attachCharCounter } from '../utils/validation.js';

const PRESET_ARTICLES = [
  {
    label: 'Credible Sample',
    title: 'NASA Confirms Water Ice on Moon Poles',
    text: `NASA scientists have confirmed the presence of water ice in permanently shadowed regions near the lunar poles, a finding based on data gathered by the Lunar Reconnaissance Orbiter over several years. The discovery strengthens the case for using the Moon as a long-term base for human exploration. Scientists from multiple universities corroborated the data using infrared spectroscopy. The results were published in the peer-reviewed journal Nature Geoscience and underwent extensive verification before release.`,
  },
  {
    label: 'Suspicious Sample',
    title: 'Government Plans Secret Mind Control Using 5G',
    text: `EXCLUSIVE: Whistleblowers inside the deep state have revealed a classified government program to use 5G towers to transmit frequency waves that alter human brain chemistry and suppress critical thinking. The project, codenamed "SILENT WAVE," has been running since 2018 according to anonymous sources. Tech giants are complicit in hiding the truth from the public. Share this before it gets taken down! Scientists who tried to expose this have reportedly gone missing. The mainstream media refuses to report this.`,
  },
  {
    label: 'Wire Report',
    title: 'French inflation falls more than expected in September',
    text: `PARIS (Reuters) - French inflation fell more than expected in September, preliminary EU-harmonised data showed on Friday, supporting bets on further European Central Bank rate cuts. EU-harmonised consumer prices in the euro zone's second-biggest economy rose 1.5% year-on-year in September, statistics agency INSEE said in a preliminary report, slowing from 2.2% in August.`,
  },
  {
    label: 'Ex A: Health Advice',
    title: 'Daily Water Intake and Kidney Function',
    text: `Most adults with normal kidney function do well drinking about 1.5 to 3 liters of plain water daily, adjusting for climate, exercise, and sweat.`,
  },
  {
    label: 'Ex B: Campus Protests',
    title: 'Lovely Professional University Protests Late September 2026',
    text: `Violent student protests and campus vandalism erupted at Lovely Professional University in Phagwara, Punjab, in late September 2026, triggered by unverified social media rumors regarding an alleged sexual assault.`,
  }
];

const history = new HistoryFeed(8);

export function renderFakeNewsPage() {
  const page = document.createElement('div');
  page.className = 'view-page';

  /* Title & Subtitle */
  page.innerHTML = `
    <h1 class="page-title"><span aria-hidden="true">📰</span> Fake News Detection</h1>
    <p class="page-subtitle">Evaluate news authenticity using DistilBERT semantic classification and live independent evidence retrieval.</p>
  `;

  /* Dynamic Health / Status Banner Container (Task 1) */
  const bannerContainer = document.createElement('div');
  bannerContainer.id = 'fn-status-banner-container';
  page.appendChild(bannerContainer);

  // Two-phase check: (1) is Flask alive, (2) did the fake-news model load?
  checkApiHealth()
    .then((healthData) => {
      // Flask is up. Now check whether the DistilBERT model actually loaded.
      const fnStatus = healthData?.models?.fake_news;
      if (fnStatus && !fnStatus.loaded) {
        const banner = document.createElement('div');
        banner.className = 'demo-banner';
        banner.style.borderColor = 'var(--color-warning)';
        banner.style.background = 'rgba(245, 158, 11, 0.12)';
        banner.style.color = 'var(--color-warning)';
        const errDetail = fnStatus.error
          ? `<br><code style="font-size:0.78rem;opacity:0.85">${fnStatus.error}</code>`
          : '';
        const cause = !fnStatus.artifacts_complete
          ? 'Model artifacts not found — retraining required.'
          : 'Model artifacts exist but failed to load — check Flask server logs.';
        banner.innerHTML = `
          <strong>⚠️ DistilBERT Not Ready:</strong> ${cause}${errDetail}
        `;
        bannerContainer.appendChild(banner);
      } else {
        bannerContainer.innerHTML = ''; // Backend online and model ready.
      }
    })
    .catch(() => {
      const banner = document.createElement('div');
      banner.className = 'demo-banner';
      banner.style.borderColor = 'var(--color-warning)';
      banner.style.background = 'rgba(245, 158, 11, 0.12)';
      banner.style.color = 'var(--color-warning)';
      banner.innerHTML = `
        <strong>⚠️ Backend Offline:</strong> Flask API is not reachable at <code>http://localhost:5000</code>.
        Please ensure the backend is running (<code>npm run api</code>) to perform AI classification and live evidence retrieval.
      `;
      bannerContainer.appendChild(banner);
    });

  const layout = document.createElement('div');
  layout.className = 'detection-layout';

  /* ── LEFT: Input Panel ──────────────────────────────────────────── */
  const inputPanel = document.createElement('div');
  inputPanel.className = 'cyber-card accent-glow';

  inputPanel.innerHTML = `
    <div class="card-header">
      <h2 class="card-title"><span aria-hidden="true">✍️</span> Input Article</h2>
      <span class="badge badge-info">NLP & Evidence Verification</span>
    </div>

    <!-- Presets -->
    <div class="preset-bar" aria-label="Sample article presets">
      <span class="preset-title">Load sample:</span>
      <button class="btn-preset" id="fn-preset-0" aria-label="Load credible article sample">📗 Credible</button>
      <button class="btn-preset" id="fn-preset-1" aria-label="Load suspicious article sample">📕 Suspicious</button>
      <button class="btn-preset" id="fn-preset-2" aria-label="Load wire report sample">📋 Wire Report</button>
      <button class="btn-preset" id="fn-preset-3" aria-label="Load health advice sample">💧 Ex A: Health</button>
      <button class="btn-preset" id="fn-preset-4" aria-label="Load campus protest claim sample">🔍 Ex B: Claim</button>
      <button class="btn-preset" id="fn-clear" aria-label="Clear form">✕ Clear</button>
    </div>

    <form id="fn-form" novalidate aria-label="Fake news detection form">
      <div class="form-group">
        <label class="form-label" for="fn-title">
          Article Title / Headline
          <span class="form-hint">Used for live evidence search</span>
        </label>
        <input
          type="text"
          id="fn-title"
          class="form-control"
          name="title"
          placeholder="Enter article headline or claim…"
          maxlength="300"
          aria-describedby="fn-title-hint"
        />
        <div id="fn-title-hint" class="sr-only">Optional headline of the article being analysed</div>
        <span class="validation-msg" role="alert" aria-live="polite" style="display:none"></span>
      </div>

      <div class="form-group">
        <label class="form-label" for="fn-text">
          Article Body
          <span class="form-hint">Min. 5 words</span>
        </label>
        <textarea
          id="fn-text"
          class="form-control"
          name="text"
          rows="8"
          placeholder="Paste article text here… (minimum 5 words for analysis)"
          maxlength="10000"
          required
          aria-required="true"
          aria-describedby="fn-text-hint fn-text-counter"
        ></textarea>
        <span id="fn-text-counter" class="char-counter" aria-live="polite">0 / 10000</span>
        <div id="fn-text-hint" class="sr-only">Full body text of the article to be analysed for credibility</div>
        <span class="validation-msg" role="alert" aria-live="polite" style="display:none"></span>
      </div>

      <button type="submit" class="btn btn-cyan" id="fn-submit" style="width:100%" aria-label="Analyse article for fake news">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        Analyse Article & Verify Evidence
      </button>
    </form>
  `;

  /* ── RIGHT: Result Panel ─────────────────────────────────────────── */
  const resultPanel = document.createElement('div');
  resultPanel.className = 'result-panel';

  const resultCard = document.createElement('div');
  resultCard.className = 'cyber-card accent-glow';
  resultCard.style.flex = '1';

  const idleState = document.createElement('div');
  idleState.className = 'result-idle';
  idleState.setAttribute('aria-label', 'No analysis result yet');
  idleState.innerHTML = `
    <div class="result-idle-icon" aria-hidden="true">📰</div>
    <p class="result-idle-text">Submit an article to see model classification and live evidence verification.</p>
    <p style="font-size:0.8rem;color:var(--text-muted)">Powered by DistilBERT NLP and live GNews independent verification</p>
  `;

  const resultOutput = document.createElement('div');
  resultOutput.className = 'result-content';
  resultOutput.style.display = 'none';
  resultOutput.setAttribute('aria-live', 'polite');
  resultOutput.setAttribute('aria-label', 'Analysis result');

  resultCard.innerHTML = `<div class="card-header"><h2 class="card-title"><span aria-hidden="true">📋</span> Analysis & Evidence Report</h2></div>`;
  resultCard.appendChild(idleState);
  resultCard.appendChild(resultOutput);

  /* Evidence Card */
  const evidenceCard = document.createElement('div');
  evidenceCard.className = 'cyber-card';
  evidenceCard.style.marginTop = '1rem';
  evidenceCard.style.display = 'none';
  const evidenceOutput = document.createElement('div');
  evidenceCard.appendChild(evidenceOutput);

  /* History card */
  const historyCard = document.createElement('div');
  historyCard.className = 'cyber-card';
  historyCard.style.marginTop = '1rem';
  historyCard.innerHTML = `<div class="card-header"><h2 class="card-title" style="font-size:0.95rem"><span aria-hidden="true">🕒</span> Session History</h2></div>`;
  historyCard.appendChild(history.getEl());

  resultPanel.appendChild(resultCard);
  resultPanel.appendChild(evidenceCard);
  resultPanel.appendChild(historyCard);

  layout.appendChild(inputPanel);
  layout.appendChild(resultPanel);
  page.appendChild(layout);

  /* ── Wire Up Presets ─────────────────────────────────────────────── */
  const titleInput = inputPanel.querySelector('#fn-title');
  const textArea   = inputPanel.querySelector('#fn-text');

  PRESET_ARTICLES.forEach((preset, i) => {
    inputPanel.querySelector(`#fn-preset-${i}`)?.addEventListener('click', () => {
      titleInput.value = preset.title;
      textArea.value   = preset.text;
      textArea.dispatchEvent(new Event('input'));
      setFieldValidity(textArea, null);
    });
  });

  inputPanel.querySelector('#fn-clear').addEventListener('click', () => {
    titleInput.value = '';
    textArea.value = '';
    textArea.dispatchEvent(new Event('input'));
    setFieldValidity(textArea, null);
    idleState.style.display = '';
    resultOutput.style.display = 'none';
    evidenceCard.style.display = 'none';
  });

  attachCharCounter(textArea, 10000);

  /* ── Form Submit ─────────────────────────────────────────────────── */
  inputPanel.querySelector('#fn-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const text = textArea.value.trim();
    const title = titleInput.value.trim();
    const combinedWords = `${title} ${text}`.trim().split(/\s+/).filter(Boolean);

    if (combinedWords.length < 5) {
      setFieldValidity(textArea, 'Please provide at least 5 words for analysis.');
      textArea.focus();
      return;
    }
    setFieldValidity(textArea, null);

    const submitBtn = inputPanel.querySelector('#fn-submit');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span aria-hidden="true">⏳</span> Analysing & Searching News…`;

    /* Show scanner */
    idleState.style.display = 'none';
    resultOutput.style.display = 'none';
    evidenceCard.style.display = 'none';

    const loader = createScanLoader([
      'Preprocessing text & extracting claim…',
      'Running DistilBERT sequence classifier…',
      'Querying live independent news index…',
      'Corroborating claims with retrieved sources…',
      'Compiling verification report…'
    ]);
    resultCard.appendChild(loader.el);
    loader.start();

    try {
      const payload = { text, title: title || undefined };
      
      // Parallel requests to ML classifier and Evidence search
      const [mlRes, evidenceRes] = await Promise.allSettled([
        detectFakeNews(payload),
        verifyEvidence(payload)
      ]);

      loader.stop();
      loader.el.remove();

      const mlData = mlRes.status === 'fulfilled' ? mlRes.value : null;
      const evidenceData = evidenceRes.status === 'fulfilled' ? evidenceRes.value : null;

      if (mlData) {
        renderModelResult(resultOutput, mlData, evidenceData);
        resultOutput.style.display = 'flex';

        let badgeClass = 'badge-info';
        if (mlData.verdict === 'REAL') badgeClass = 'badge-safe';
        else if (mlData.verdict === 'FAKE') badgeClass = 'badge-danger';
        else if (mlData.verdict === 'UNCERTAIN') badgeClass = 'badge-warning';
        else if (mlData.verdict === 'INFORMATIONAL') badgeClass = 'badge-info';

        history.add({
          text: title || text.substring(0, 60) + '…',
          badge: { class: badgeClass, label: mlData.verdict },
        });
      } else {
        throw mlRes.reason;
      }

      evidenceCard.style.display = 'flex';
      renderEvidenceSection(evidenceOutput, evidenceRes, mlData);

      showToast({ type: 'success', title: 'Analysis Complete', body: 'NLP classification and evidence retrieval completed.' });

    } catch (err) {
      loader.stop();
      loader.el.remove();
      idleState.style.display = 'flex';
      resultOutput.style.display = 'none';
      evidenceCard.style.display = 'none';

      const errorMsg = err.message || 'Could not connect to Flask backend.';
      showToast({ type: 'error', title: 'API Request Failed', body: errorMsg });

      // Show informative error card in result panel
      idleState.innerHTML = `
        <div class="result-idle-icon" style="color:var(--color-danger);opacity:1;">⚠️</div>
        <p class="result-idle-text" style="color:var(--color-danger);font-weight:600;">Request Failed</p>
        <p style="font-size:0.85rem;color:var(--text-secondary);max-width:400px;line-height:1.5;">${errorMsg}</p>
        <button class="btn btn-secondary btn-sm" id="fn-retry-btn" style="margin-top:0.75rem;">Retry Request</button>
      `;
      idleState.querySelector('#fn-retry-btn')?.addEventListener('click', () => {
        inputPanel.querySelector('#fn-form').dispatchEvent(new Event('submit'));
      });
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg> Analyse Article & Verify Evidence`;
    }
  });

  return page;
}

/* ── Render Model Classification Section (Task 2 & 5) ─────────────── */
/* ── Render Model Classification Section (Task 2 & 5) ─────────────── */
function renderModelResult(container, data, evidenceData) {
  const verdict = data.verdict || 'UNCERTAIN';
  const confidencePct = typeof data.confidence === 'number' ? (data.confidence * 100).toFixed(1) : '0.0';
  const probs = data.probabilities || {};
  const probRealPct = typeof probs.real === 'number' ? (probs.real * 100).toFixed(1) : '0.0';
  const probFakePct = typeof probs.fake === 'number' ? (probs.fake * 100).toFixed(1) : '0.0';
  const inputClass = data.input_classification || {};

  let verdictClass = 'warning';
  let verdictIcon = '⚠️';
  let verdictLabel = verdict;
  let verdictDesc = 'Linguistic analysis does not strongly distinguish real from fake.';

  if (verdict === 'INFORMATIONAL') {
    verdictClass = 'safe';
    verdictIcon = '💡';
    verdictLabel = 'INFORMATIONAL / GENERAL ADVICE';
    verdictDesc = 'General factual or physiological guidance. Linguistic news classifiers are not calibrated for medical or health advice.';
  } else if (verdict === 'OPINION') {
    verdictClass = 'warning';
    verdictIcon = '💬';
    verdictLabel = 'OPINION / COMMENTARY';
    verdictDesc = 'Personal viewpoint or commentary. Algorithmic news classification is not suitable for subjective text.';
  } else if (verdict === 'REAL') {
    verdictClass = 'safe';
    verdictIcon = '✅';
    verdictLabel = 'REAL';
    verdictDesc = 'Text exhibits semantic patterns characteristic of verified news.';
  } else if (verdict === 'FAKE') {
    verdictClass = 'danger';
    verdictIcon = '🚨';
    verdictLabel = 'FAKE';
    verdictDesc = 'Text exhibits semantic patterns typical of sensationalism or unverified claims in training data.';
  }

  // 1. Optional Input Type Advisory Banner (e.g. for Health Guidance)
  let genreBanner = '';
  if (inputClass.genre === 'general_health_advice') {
    genreBanner = `
      <div style="background:rgba(6, 182, 212, 0.12);border:1px solid rgba(6, 182, 212, 0.4);border-radius:var(--radius-md);padding:1rem;margin-bottom:1rem;">
        <div style="display:flex;align-items:center;gap:0.5rem;font-weight:700;color:var(--cyan-300);font-size:0.95rem;margin-bottom:0.35rem;">
          <span aria-hidden="true">💡</span> Input Advisory: General Health Advice / Factual Guidance
        </div>
        <p style="font-size:0.85rem;color:var(--text-secondary);margin:0;line-height:1.5;">
          This input provides general physiological guidance rather than an event-based news report.
          Linguistic news classifiers (like DistilBERT trained on WELFake) were trained on news articles and cannot verify medical guidelines.
          ${escapeHtml(inputClass.domain_guidance || 'Recommended fluid intake generally varies by individual health, climate, and exercise.')}
        </p>
      </div>
    `;
  }

  // 2. Disagreement Banner (Model says FAKE, but Evidence is SUPPORTED)
  let disagreementBanner = '';
  const evVerdict = (evidenceData?.verdict || '').toUpperCase();
  const isDisagreement = (data.verdict === 'FAKE' || (data.verdict === 'UNCERTAIN' && (probs.fake || 0) > 0.65)) && 
                         (evVerdict === 'SUPPORTED');
  if (isDisagreement) {
    const suppCount = evidenceData?.supporting_count || evidenceData?.total_sources || 0;
    disagreementBanner = `
      <div style="background:rgba(245, 158, 11, 0.15);border:1px solid var(--color-warning);border-radius:var(--radius-md);padding:1rem;margin-bottom:1rem;">
        <div style="display:flex;align-items:center;gap:0.5rem;font-weight:700;color:var(--color-warning);font-size:0.95rem;margin-bottom:0.35rem;">
          <span aria-hidden="true">⚠️</span> Model vs Evidence Disagreement Notice
        </div>
        <p style="font-size:0.85rem;color:var(--text-secondary);margin:0;line-height:1.5;">
          The DistilBERT model leaned towards <strong>FAKE (${probFakePct}%)</strong> based on stylistic text patterns.
          However, independent live news search found <strong>${suppCount} published reports</strong>
          from credible news organizations confirming this event. Real-world published reporting takes precedence over stylistic model scores.
        </p>
      </div>
    `;
  }

  container.innerHTML = `
    ${genreBanner}
    ${disagreementBanner}

    <!-- 1. Model Prediction Section -->
    <div class="result-verdict-banner ${verdictClass}" role="status" aria-live="assertive" aria-label="Model Verdict: ${verdictLabel}">
      <span class="verdict-icon" aria-hidden="true">${verdictIcon}</span>
      <div>
        <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.5px;color:var(--text-muted)">DistilBERT Model Assessment</div>
        <div class="verdict-label">${verdictLabel}</div>
        <div class="verdict-description">${verdictDesc}</div>
      </div>
    </div>

    <!-- Model Details Note -->
    <div style="font-size:0.75rem;color:var(--text-muted);margin:0.5rem 0;line-height:1.4;">
      Model: <strong>DistilBERT (distilbert-base-uncased)</strong> • Training: <strong>WELFake & Multi-Domain News Corpus (Class 0: REAL, Class 1: FAKE)</strong>
    </div>

    <!-- 2. Model Confidence Bar -->
    <div style="margin-top:0.25rem;">
      <div style="display:flex;justify-content:space-between;font-size:0.825rem;color:var(--text-secondary);margin-bottom:0.25rem;">
        <span>Model Output Confidence</span>
        <strong style="color:var(--cyan-300);">${confidencePct}%</strong>
      </div>
      <div class="confidence-bar">
        <div class="confidence-bar-fill ${verdict === 'REAL' ? 'high' : (verdict === 'FAKE' ? 'low' : 'medium')}" style="width:${confidencePct}%"></div>
      </div>
    </div>

    <!-- Probability Breakdown -->
    <div class="prob-breakdown-card">
      <div style="font-size:0.8rem;font-weight:700;color:var(--text-secondary);text-transform:uppercase;letter-spacing:0.4px;">
        Predicted Class Probabilities
      </div>
      <div class="prob-row">
        <div class="prob-row-header">
          <span style="color:var(--color-safe);">Real News (Class 0)</span>
          <span style="color:var(--color-safe);">${probRealPct}%</span>
        </div>
        <div class="prob-bar-track">
          <div class="prob-bar-fill real" style="width:${probRealPct}%"></div>
        </div>
      </div>
      <div class="prob-row">
        <div class="prob-row-header">
          <span style="color:var(--color-danger);">Fake News (Class 1)</span>
          <span style="color:var(--color-danger);">${probFakePct}%</span>
        </div>
        <div class="prob-bar-track">
          <div class="prob-bar-fill fake" style="width:${probFakePct}%"></div>
        </div>
      </div>
      
      <!-- Calibration Warning -->
      <div style="background:rgba(15, 23, 42, 0.4);border:1px solid rgba(148, 163, 184, 0.15);border-radius:var(--radius-sm);padding:0.75rem;margin-top:0.5rem;font-size:0.75rem;color:var(--text-muted);line-height:1.45;">
        ⚠️ <strong>Calibration Notice:</strong> Class scores are softmax similarities to the WELFake training corpus.
        They are NOT verified probabilities of factual truth unless calibrated against real-world distributions.
      </div>
    </div>
  `;

  // Raw API Response Toggle
  const toggle = document.createElement('button');
  toggle.className = 'btn btn-secondary btn-sm';
  toggle.textContent = 'Show Model Details & Logits';
  toggle.style.marginTop = '0.5rem';
  toggle.style.alignSelf = 'flex-start';

  const codeBox = document.createElement('pre');
  codeBox.className = 'json-code-box';
  codeBox.style.display = 'none';
  codeBox.textContent = JSON.stringify({
    verdict: data.verdict,
    confidence: data.confidence,
    probabilities: data.probabilities,
    logits: data.logits,
    predicted_class: data.predicted_class,
    input_classification: data.input_classification,
    model_assessment: data.model_assessment,
    calibration_note: data.calibration_note
  }, null, 2);

  toggle.addEventListener('click', () => {
    const hidden = codeBox.style.display === 'none';
    codeBox.style.display = hidden ? 'block' : 'none';
    toggle.textContent = hidden ? 'Hide Model Details & Logits' : 'Show Model Details & Logits';
  });

  container.appendChild(toggle);
  container.appendChild(codeBox);
}

/* ── Render Evidence Verification Section (Task 3, 4, 5) ───────────── */
function renderEvidenceSection(container, evidenceRes, mlData) {
  container.innerHTML = `
    <div class="card-header" style="margin-bottom:0.75rem;">
      <h2 class="card-title" style="font-size:1.05rem;"><span aria-hidden="true">🔍</span> Real-World Evidence Verification</h2>
    </div>
  `;

  if (evidenceRes.status === 'rejected') {
    container.innerHTML += `
      <div style="padding:1rem;background:rgba(239, 68, 68, 0.1);border:1px solid rgba(239, 68, 68, 0.3);border-radius:var(--radius-md);">
        <strong style="color:var(--color-danger);">Verification unavailable:</strong>
        <p style="font-size:0.85rem;color:var(--text-secondary);margin-top:0.25rem;">${escapeHtml(evidenceRes.reason?.message || 'External search request failed.')}</p>
        <p style="font-size:0.75rem;color:var(--text-muted);margin-top:0.25rem;font-style:italic;">Note: A failed external API request is never proof that a claim is false.</p>
      </div>
    `;
    return;
  }

  const data = evidenceRes.value;
  if (data.status === 'error') {
    container.innerHTML += `
      <div style="padding:1rem;background:rgba(245, 158, 11, 0.1);border:1px solid rgba(245, 158, 11, 0.3);border-radius:var(--radius-md);">
        <strong style="color:var(--color-warning);">Verification unavailable:</strong>
        <p style="font-size:0.85rem;color:var(--text-secondary);margin-top:0.25rem;">${escapeHtml(data.message)}</p>
        <p style="font-size:0.75rem;color:var(--text-muted);margin-top:0.25rem;font-style:italic;">Note: A failed external API request is never proof that a claim is false.</p>
      </div>
    `;
    return;
  }

  const rawVerdict = (data.verdict || 'UNVERIFIED').toUpperCase();
  let verdictBadgeClass = 'badge-info';
  let verdictLabel = 'UNVERIFIED / INSUFFICIENT EVIDENCE';

  if (rawVerdict === 'SUPPORTED' || rawVerdict === 'SUPPORTING') {
    verdictBadgeClass = 'badge-safe';
    verdictLabel = 'SUPPORTED';
  } else if (rawVerdict === 'CONTRADICTED') {
    verdictBadgeClass = 'badge-danger';
    verdictLabel = 'CONTRADICTED';
  } else if (rawVerdict === 'MIXED EVIDENCE' || rawVerdict === 'MIXED') {
    verdictBadgeClass = 'badge-warning';
    verdictLabel = 'MIXED EVIDENCE';
  }

  const providerInfo = data.provider_info || {};
  const freshnessLabel = providerInfo.freshness || 'News Search Provider';
  const freshnessNotice = providerInfo.freshness_notice || 'Subject to provider indexing lag.';

  // Disagreement Banner in Evidence Section
  let disagreementNotice = '';
  const isEvidenceDisagreement = (mlData?.verdict === 'FAKE' || (mlData?.verdict === 'UNCERTAIN' && (mlData?.probabilities?.fake || 0) > 0.65)) && 
                                 (rawVerdict === 'SUPPORTED');
  if (isEvidenceDisagreement) {
    disagreementNotice = `
      <div style="background:rgba(245, 158, 11, 0.15);border:1px solid var(--color-warning);border-radius:var(--radius-md);padding:0.75rem;margin-bottom:1rem;font-size:0.85rem;color:var(--text-secondary);">
        <strong style="color:var(--color-warning);">⚠️ Model Disagreement Notice:</strong>
        DistilBERT scored this claim as leaning FAKE, but independent live news coverage corroborates this event.
        Published journalism takes precedence over stylistic model predictions.
      </div>
    `;
  }

  // Health / Domain Guidance Box
  let domainAdvisory = '';
  if (data.domain_guidance) {
    domainAdvisory = `
      <div style="background:rgba(6, 182, 212, 0.1);border:1px solid rgba(6, 182, 212, 0.3);border-radius:var(--radius-sm);padding:0.75rem;margin-bottom:1rem;font-size:0.85rem;color:var(--text-secondary);">
        <strong style="color:var(--cyan-300);">🩺 Medical Consensus Context:</strong>
        ${escapeHtml(data.domain_guidance)}
      </div>
    `;
  }

  container.innerHTML += `
    ${disagreementNotice}
    ${domainAdvisory}

    <!-- Evidence Verdict & Source Counts -->
    <div style="background:rgba(15, 23, 42, 0.4);border:1px solid var(--border-color);border-radius:var(--radius-md);padding:1.25rem;margin-bottom:1rem;">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.75rem;">
        <div>
          <span style="font-size:0.8rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.4px;">Evidence Assessment:</span>
          <span class="badge ${verdictBadgeClass}" style="margin-left:0.5rem;font-size:0.85rem;text-transform:uppercase;">${verdictLabel}</span>
        </div>
        <span class="freshness-pill" title="${escapeHtml(freshnessNotice)}">🕒 ${escapeHtml(freshnessLabel)}</span>
      </div>

      <p style="font-size:0.875rem;color:var(--text-secondary);margin-top:0.75rem;line-height:1.5;">
        ${escapeHtml(data.explanation || 'Claim evaluated against indexed articles.')}
      </p>

      <div class="evidence-header-stats">
        <span style="font-size:0.8rem;color:var(--text-muted);">Sources evaluated: <strong style="color:var(--text-primary);">${data.total_sources || 0}</strong></span>
        <span style="font-size:0.8rem;color:var(--color-safe);">Supporting: <strong>${data.supporting_count || 0}</strong></span>
        <span style="font-size:0.8rem;color:var(--color-danger);">Contradicting: <strong>${data.contradicting_count || 0}</strong></span>
        ${data.claim_extracted ? `<span style="font-size:0.8rem;color:var(--cyan-300);">Search query: <em>"${escapeHtml(data.claim_extracted)}"</em></span>` : ''}
      </div>

      <div style="font-size:0.75rem;color:var(--text-muted);margin-top:0.25rem;font-style:italic;">
        ${escapeHtml(freshnessNotice)}
      </div>
    </div>
  `;

  // Supporting Sources Section
  if (data.supporting_evidence && data.supporting_evidence.length > 0) {
    const suppTitle = document.createElement('h3');
    suppTitle.style.cssText = 'font-size:0.9rem;font-weight:700;color:var(--color-safe);margin:1rem 0 0.5rem;display:flex;align-items:center;gap:0.4rem;';
    suppTitle.innerHTML = `<span aria-hidden="true">📗</span> Supporting Sources (${data.supporting_evidence.length})`;
    container.appendChild(suppTitle);

    const suppList = renderSourceCards(data.supporting_evidence, 'supporting');
    container.appendChild(suppList);
  }

  // Contradicting Sources Section
  if (data.contradicting_evidence && data.contradicting_evidence.length > 0) {
    const contraTitle = document.createElement('h3');
    contraTitle.style.cssText = 'font-size:0.9rem;font-weight:700;color:var(--color-danger);margin:1.25rem 0 0.5rem;display:flex;align-items:center;gap:0.4rem;';
    contraTitle.innerHTML = `<span aria-hidden="true">📕</span> Contradicting / Fact-Checking Sources (${data.contradicting_evidence.length})`;
    container.appendChild(contraTitle);

    const contraList = renderSourceCards(data.contradicting_evidence, 'contradicting');
    container.appendChild(contraList);
  }

  // Neutral / Context Sources Section
  if (data.neutral_evidence && data.neutral_evidence.length > 0) {
    const neutralTitle = document.createElement('h3');
    neutralTitle.style.cssText = 'font-size:0.9rem;font-weight:700;color:var(--text-secondary);margin:1.25rem 0 0.5rem;display:flex;align-items:center;gap:0.4rem;';
    neutralTitle.innerHTML = `<span aria-hidden="true">📄</span> Additional Coverage (${data.neutral_evidence.length})`;
    container.appendChild(neutralTitle);

    const neutralList = renderSourceCards(data.neutral_evidence, 'neutral');
    container.appendChild(neutralList);
  }

  if (!data.evidence || data.evidence.length === 0) {
    const noSources = document.createElement('p');
    noSources.style.cssText = 'font-size:0.875rem;color:var(--text-muted);padding:0.75rem 0;';
    noSources.textContent = 'No matching news articles found. A lack of coverage does NOT prove the claim is false; the event may be unindexed, localized, or very recent.';
    container.appendChild(noSources);
  }

  // Important Definitive Proof Warning Card
  const warningCard = document.createElement('div');
  warningCard.className = 'verification-warning-card';
  warningCard.innerHTML = `
    <span class="warning-icon" aria-hidden="true">⚠️</span>
    <div class="warning-text">
      <strong>Important Verification Note:</strong>
      AI predictions evaluate textual structure and live searches capture published coverage;
      <strong>neither represents definitive proof of factual truth</strong>.
      Search results depend on publisher syndication and index freshness (12-hour provider delay on free tier).
      Lack of matching coverage is not proof of falsehood, and matching keywords do not guarantee veracity.
      Always cross-reference critical claims with primary government records, official press offices, or peer-reviewed literature.
    </div>
  `;
  container.appendChild(warningCard);
}

function renderSourceCards(articles, category) {
  const list = document.createElement('div');
  list.style.cssText = 'display:flex;flex-direction:column;gap:0.75rem;margin-bottom:0.75rem;';

  articles.forEach(art => {
    const card = document.createElement('div');
    card.className = `evidence-source-card ${category}`;

    const formattedDate = formatDateString(art.date);

    card.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;">
        <a href="${escapeHtml(art.url)}" target="_blank" rel="noopener noreferrer" class="source-article-link">
          ${escapeHtml(art.title || 'Untitled Article')} ↗
        </a>
      </div>
      <div class="evidence-card-meta">
        <span class="source-publisher">🏢 ${escapeHtml(art.source || 'News Outlet')}</span>
        <span>•</span>
        <span>📅 ${formattedDate}</span>
      </div>
      ${art.excerpt ? `<p style="font-size:0.85rem;color:var(--text-secondary);margin:0;line-height:1.4;">${escapeHtml(art.excerpt)}</p>` : ''}
    `;
    list.appendChild(card);
  });

  return list;
}

function formatDateString(dateStr) {
  if (!dateStr) return 'Date unknown';
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (_) {
    return dateStr;
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
