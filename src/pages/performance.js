/* ==========================================================================
   CYBER SENTINEL - MODEL PERFORMANCE PAGE
   Displays ML metrics, confusion matrices, per-class accuracy bars
   All data is clearly labelled as DEMO DATA
   ========================================================================== */

import { getModelPerformance } from '../api/client.js';
import { createDemoBanner, showToast } from '../components/ui.js';

/* ── DEMO METRICS DATA ──────────────────────────────────────────── */
const DEMO_MODELS = [
  {
    id: 'fake-news',
    name: 'Fake News Detector',
    icon: '📰',
    algorithm: 'BERT + Logistic Regression Ensemble',
    dataset: 'LIAR Dataset (12,836 samples)',
    metrics: { accuracy: 97.3, precision: 96.8, recall: 97.1, f1: 96.9 },
    confusion: { tp: 3842, fp: 128, fn: 112, tn: 3918 },
    classMetrics: [
      { label: 'TRUE / Credible',       precision: 97.5, recall: 97.2, f1: 97.3 },
      { label: 'FALSE / Fake',          precision: 96.1, recall: 97.0, f1: 96.5 },
    ],
    notes: 'Trained on political statements from PolitiFact. Fine-tuned using LIAR-PLUS annotations.',
  },
  {
    id: 'fraud',
    name: 'Fraud Detector',
    icon: '💳',
    algorithm: 'XGBoost + Isolation Forest Hybrid',
    dataset: 'Kaggle Credit Card Fraud (284,807 samples)',
    metrics: { accuracy: 99.2, precision: 91.4, recall: 88.7, f1: 90.0 },
    confusion: { tp: 82, fp: 8, fn: 10, tn: 28317 },
    classMetrics: [
      { label: 'Legitimate Transactions', precision: 99.9, recall: 99.9, f1: 99.9 },
      { label: 'Fraudulent',              precision: 91.4, recall: 88.7, f1: 90.0 },
    ],
    notes: 'Class imbalance handled via SMOTE oversampling. Threshold tuned to minimise false negatives.',
  },
  {
    id: 'url',
    name: 'URL / Phishing Detector',
    icon: '🔗',
    algorithm: 'Random Forest + Lexical Feature Extractor',
    dataset: 'PhishTank + OpenPhish (94,011 samples)',
    metrics: { accuracy: 95.6, precision: 94.2, recall: 96.1, f1: 95.1 },
    confusion: { tp: 9421, fp: 581, fn: 368, tn: 9237 },
    classMetrics: [
      { label: 'Benign URLs',   precision: 96.2, recall: 94.3, f1: 95.2 },
      { label: 'Phishing URLs', precision: 94.2, recall: 96.1, f1: 95.1 },
    ],
    notes: 'Uses 87 lexical, host-based, and content-based features. Domain age and Alexa rank are top predictors.',
  },
];

function createMetricCard(label, value, tag) {
  const card = document.createElement('div');
  card.className = 'metric-card';
  card.setAttribute('aria-label', `${label}: ${value}`);
  card.innerHTML = `
    <div class="metric-value">${value}%</div>
    <div class="metric-label">${label}</div>
    <div class="metric-model-tag">${tag}</div>
  `;
  return card;
}

function createConfusionMatrix(cm) {
  const div = document.createElement('div');
  div.setAttribute('aria-label', 'Confusion matrix');
  div.innerHTML = `
    <div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:0.75rem;text-align:center">Confusion Matrix</div>
    <div style="display:grid;grid-template-columns:auto 1fr 1fr;gap:6px;max-width:340px;margin:0 auto">
      <div></div>
      <div class="cm-header">Pred: Positive</div>
      <div class="cm-header">Pred: Negative</div>
      <div class="cm-header" style="writing-mode:vertical-rl;transform:rotate(180deg);font-size:0.72rem">Actual Pos.</div>
      <div class="cm-cell cm-tp" title="True Positives">
        <div style="font-size:1.25rem;font-weight:800">${cm.tp.toLocaleString()}</div>
        <div style="font-size:0.72rem;opacity:0.8">TP</div>
      </div>
      <div class="cm-cell cm-fp" title="False Positives">
        <div style="font-size:1.25rem;font-weight:800">${cm.fp.toLocaleString()}</div>
        <div style="font-size:0.72rem;opacity:0.8">FP</div>
      </div>
      <div class="cm-header" style="writing-mode:vertical-rl;transform:rotate(180deg);font-size:0.72rem">Actual Neg.</div>
      <div class="cm-cell cm-fn" title="False Negatives">
        <div style="font-size:1.25rem;font-weight:800">${cm.fn.toLocaleString()}</div>
        <div style="font-size:0.72rem;opacity:0.8">FN</div>
      </div>
      <div class="cm-cell cm-tn" title="True Negatives">
        <div style="font-size:1.25rem;font-weight:800">${cm.tn.toLocaleString()}</div>
        <div style="font-size:0.72rem;opacity:0.8">TN</div>
      </div>
    </div>
  `;
  return div;
}

function createClassMetricsTable(classMetrics) {
  const rows = classMetrics.map(cm => `
    <tr>
      <td style="color:var(--text-secondary)">${cm.label}</td>
      <td class="mono-font" style="color:var(--cyan-300)">${cm.precision}%</td>
      <td class="mono-font" style="color:var(--cyan-300)">${cm.recall}%</td>
      <td class="mono-font" style="color:var(--cyan-300)">${cm.f1}%</td>
    </tr>
  `).join('');
  const div = document.createElement('div');
  div.innerHTML = `
    <div style="overflow-x:auto">
      <table class="recent-activity-table" aria-label="Per-class metrics">
        <thead>
          <tr>
            <th scope="col">Class</th>
            <th scope="col">Precision</th>
            <th scope="col">Recall</th>
            <th scope="col">F1 Score</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
  return div;
}

export function renderPerformancePage() {
  const page = document.createElement('div');
  page.className = 'view-page';

  page.innerHTML = `
    <h1 class="page-title"><span aria-hidden="true">📈</span> Model Performance</h1>
    <p class="page-subtitle">Accuracy, precision, recall, F1 scores and confusion matrices for each deployed ML model.</p>
  `;

  page.appendChild(createDemoBanner('⚠️ DEMO DATA — All metrics shown are representative sample figures for UI demonstration. Live metrics will load from GET /api/models/performance when the Flask API is connected.'));

  /* API refresh button */
  const refreshRow = document.createElement('div');
  refreshRow.style.cssText = 'display:flex;justify-content:flex-end;margin-bottom:1.5rem;gap:0.75rem;align-items:center';
  refreshRow.innerHTML = `
    <span style="font-size:0.8rem;color:var(--text-muted)" id="perf-last-updated">Showing demo data</span>
    <button class="btn btn-outline-cyan btn-sm" id="perf-refresh-btn" aria-label="Fetch live metrics from Flask API">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
      Refresh from API
    </button>
  `;
  page.appendChild(refreshRow);

  /* Overall summary metrics grid */
  const summaryCard = document.createElement('div');
  summaryCard.className = 'cyber-card accent-glow';
  summaryCard.style.marginBottom = '1.5rem';
  summaryCard.innerHTML = `
    <div class="card-header">
      <h2 class="card-title"><span aria-hidden="true">🏆</span> Overall Summary</h2>
      <span class="badge badge-demo">Demo Data</span>
    </div>
  `;

  const metricsGrid = document.createElement('div');
  metricsGrid.className = 'metrics-grid';

  const summaryMetrics = [
    { label: 'Fake News Accuracy',  value: '97.3', tag: 'BERT Ensemble' },
    { label: 'Fraud Accuracy',      value: '99.2', tag: 'XGBoost' },
    { label: 'URL Detection Acc.',  value: '95.6', tag: 'Random Forest' },
    { label: 'Avg F1 Score',        value: '94.0', tag: 'All Models' },
  ];

  summaryMetrics.forEach(m => metricsGrid.appendChild(createMetricCard(m.label, m.value, m.tag)));
  summaryCard.appendChild(metricsGrid);
  page.appendChild(summaryCard);

  /* Per-model sections */
  DEMO_MODELS.forEach(model => {
    const card = document.createElement('div');
    card.className = 'cyber-card';
    card.style.marginBottom = '1.5rem';
    card.setAttribute('aria-label', `${model.name} performance metrics`);

    const header = document.createElement('div');
    header.className = 'card-header';
    header.innerHTML = `
      <h2 class="card-title">
        <span aria-hidden="true">${model.icon}</span>
        ${model.name}
      </h2>
      <span class="badge badge-demo">Demo Data</span>
    `;
    card.appendChild(header);

    /* Algorithm info */
    const infoRow = document.createElement('div');
    infoRow.style.cssText = 'display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.5rem;padding:1rem;background:rgba(15,23,42,0.5);border-radius:var(--radius-md);border:1px solid var(--border-color)';
    infoRow.innerHTML = `
      <div>
        <div style="font-size:0.75rem;color:var(--text-muted);text-transform:uppercase;margin-bottom:0.25rem">Algorithm</div>
        <div style="font-size:0.875rem;color:var(--text-primary)">${model.algorithm}</div>
      </div>
      <div>
        <div style="font-size:0.75rem;color:var(--text-muted);text-transform:uppercase;margin-bottom:0.25rem">Training Dataset</div>
        <div style="font-size:0.875rem;color:var(--text-primary)">${model.dataset}</div>
      </div>
    `;
    card.appendChild(infoRow);

    /* Main metrics + confusion matrix side by side */
    const twoCol = document.createElement('div');
    twoCol.style.cssText = 'display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-bottom:1.25rem';

    /* Metrics bars */
    const metricsCol = document.createElement('div');
    const mBarData = [
      { label: 'Accuracy',  val: model.metrics.accuracy },
      { label: 'Precision', val: model.metrics.precision },
      { label: 'Recall',    val: model.metrics.recall },
      { label: 'F1 Score',  val: model.metrics.f1 },
    ];
    metricsCol.innerHTML = `<div style="font-size:0.8rem;color:var(--text-muted);text-transform:uppercase;margin-bottom:0.75rem;letter-spacing:0.4px">Core Metrics</div>`;
    const barChart = document.createElement('div');
    barChart.className = 'bar-chart';
    mBarData.forEach(b => {
      const row = document.createElement('div');
      row.className = 'bar-row';
      row.style.gridTemplateColumns = '90px 1fr 60px';
      row.innerHTML = `
        <span class="bar-row-label">${b.label}</span>
        <div class="bar-track" role="progressbar" aria-valuenow="${b.val}" aria-valuemin="0" aria-valuemax="100" aria-label="${b.label}: ${b.val}%">
          <div class="bar-fill" style="width:0%" data-width="${b.val}"></div>
        </div>
        <span class="bar-row-val">${b.val}%</span>
      `;
      barChart.appendChild(row);
    });
    metricsCol.appendChild(barChart);
    twoCol.appendChild(metricsCol);

    /* Confusion Matrix */
    twoCol.appendChild(createConfusionMatrix(model.confusion));
    card.appendChild(twoCol);

    /* Per-class table */
    const perClassTitle = document.createElement('div');
    perClassTitle.style.cssText = 'font-size:0.8rem;color:var(--text-muted);text-transform:uppercase;margin-bottom:0.5rem;letter-spacing:0.4px';
    perClassTitle.textContent = 'Per-Class Breakdown';
    card.appendChild(perClassTitle);
    card.appendChild(createClassMetricsTable(model.classMetrics));

    /* Notes */
    if (model.notes) {
      const notesBox = document.createElement('div');
      notesBox.style.cssText = 'margin-top:1rem;padding:0.85rem 1rem;background:rgba(6,182,212,0.06);border:1px solid var(--border-cyan);border-radius:var(--radius-md)';
      notesBox.innerHTML = `<p style="font-size:0.825rem;color:var(--text-secondary)"><strong style="color:var(--cyan-300)">📌 Note:</strong> ${model.notes}</p>`;
      card.appendChild(notesBox);
    }

    page.appendChild(card);
  });

  /* Animate bars on render */
  requestAnimationFrame(() => {
    setTimeout(() => {
      page.querySelectorAll('.bar-fill[data-width]').forEach(bar => {
        bar.style.width = bar.dataset.width + '%';
      });
    }, 100);
  });

  /* Refresh Button – fetch from live API */
  const refreshBtn = page.querySelector('#perf-refresh-btn');
  const lastUpdated = page.querySelector('#perf-last-updated');

  refreshBtn.addEventListener('click', async () => {
    refreshBtn.disabled = true;
    refreshBtn.innerHTML = `<span aria-hidden="true">⏳</span> Fetching…`;
    try {
      await getModelPerformance();
      lastUpdated.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
      showToast({ type: 'success', title: 'Metrics Refreshed', body: 'Live metrics loaded from Flask API.' });
    } catch (err) {
      showToast({ type: 'warning', title: 'API Unavailable', body: 'Showing demo data. ' + (err.message || '') });
      lastUpdated.textContent = 'API offline — showing demo data';
    } finally {
      refreshBtn.disabled = false;
      refreshBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg> Refresh from API`;
    }
  });

  return page;
}
