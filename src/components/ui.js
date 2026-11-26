/* ==========================================================================
   CYBER SENTINEL - REUSABLE UI COMPONENTS
   Header, Sidebar, Toast, Modal, Gauges, Loaders, Tables
   ========================================================================== */

import { checkApiHealth } from '../api/client.js';

/* ─── Toast Notification System ──────────────────────────────────── */
let toastContainer;

function getToastContainer() {
  if (!toastContainer) {
    toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.id = 'toast-container';
      document.body.appendChild(toastContainer);
    }
  }
  return toastContainer;
}

/**
 * Show a toast notification.
 * @param {object} opts
 * @param {'info'|'success'|'warning'|'error'} opts.type
 * @param {string} opts.title
 * @param {string} [opts.body]
 * @param {number} [opts.duration=4000]
 */
export function showToast({ type = 'info', title, body = '', duration = 4000 }) {
  const icons = { info: '🔵', success: '✅', warning: '⚠️', error: '❌' };
  const container = getToastContainer();

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.setAttribute('role', 'alert');
  toast.setAttribute('aria-live', 'polite');
  toast.innerHTML = `
    <span class="toast-icon">${icons[type]}</span>
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      ${body ? `<div class="toast-body">${body}</div>` : ''}
    </div>
    <button class="toast-close" aria-label="Dismiss notification" onclick="this.parentElement.remove()" style="background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:1.1rem;padding:0 0.25rem;">✕</button>
  `;

  container.appendChild(toast);
  setTimeout(() => toast.style.opacity = '0', duration);
  setTimeout(() => toast.remove(), duration + 400);
}

/* ─── API Status Badge ────────────────────────────────────────────── */
export function createApiStatusBadge() {
  const badge = document.createElement('button');
  badge.id = 'api-status-badge';
  badge.className = 'api-status-badge disconnected';
  badge.setAttribute('aria-label', 'API connection status');
  badge.innerHTML = `<span class="status-dot"></span><span id="api-status-text">API: Checking…</span>`;
  badge.addEventListener('click', () => pollApiStatus(true));
  return badge;
}

export async function pollApiStatus(manual = false) {
  const badge = document.getElementById('api-status-badge');
  const label = document.getElementById('api-status-text');
  if (!badge || !label) return;

  try {
    await checkApiHealth();
    badge.className = 'api-status-badge connected';
    label.textContent = 'API: Connected';
    if (manual) showToast({ type: 'success', title: 'API Connected', body: 'Flask backend is reachable.' });
  } catch (_) {
    badge.className = 'api-status-badge disconnected';
    label.textContent = 'API: Offline';
    if (manual) showToast({ type: 'warning', title: 'API Offline', body: 'Flask backend not reachable. Demo mode active.' });
  }
}

/* ─── Page Header (Sticky) ────────────────────────────────────────── */
export function renderHeader(router) {
  const header = document.createElement('header');
  header.className = 'app-header';
  header.setAttribute('role', 'banner');

  const brand = document.createElement('a');
  brand.className = 'brand-container';
  brand.href = '#';
  brand.setAttribute('aria-label', 'Cyber Sentinel Home');
  brand.innerHTML = `
    <div class="brand-icon" aria-hidden="true">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color:var(--cyan-400)">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>
    </div>
    <span class="brand-title">CyberSentinel</span>
  `;
  brand.addEventListener('click', (e) => { e.preventDefault(); router.navigate('landing'); });

  const actions = document.createElement('div');
  actions.className = 'header-actions';

  const statusBadge = createApiStatusBadge();
  actions.appendChild(statusBadge);

  const mobileMenuBtn = document.createElement('button');
  mobileMenuBtn.className = 'btn btn-secondary btn-sm';
  mobileMenuBtn.setAttribute('aria-label', 'Toggle navigation menu');
  mobileMenuBtn.setAttribute('aria-expanded', 'false');
  mobileMenuBtn.id = 'mobile-menu-btn';
  mobileMenuBtn.style.cssText = 'display:none;@media(max-width:768px){display:flex}';
  mobileMenuBtn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>`;
  actions.appendChild(mobileMenuBtn);

  header.appendChild(brand);
  header.appendChild(actions);
  return header;
}

/* ─── Sidebar Navigation ──────────────────────────────────────────── */
const NAV_ITEMS = [
  { id: 'landing',     icon: '🏠', label: 'Home' },
  { id: 'dashboard',   icon: '📊', label: 'Dashboard' },
  { id: 'fake-news',   icon: '📰', label: 'Fake News Detection' },
  { id: 'fraud',       icon: '💳', label: 'Fraud Detection' },
  { id: 'url',         icon: '🔗', label: 'URL Detection' },
  { id: 'performance', icon: '📈', label: 'Model Performance' },
  { id: 'about',       icon: '🛡️',  label: 'About' },
];

export function renderSidebar(router, activeRoute) {
  const sidebar = document.createElement('aside');
  sidebar.className = 'app-sidebar';
  sidebar.setAttribute('role', 'navigation');
  sidebar.setAttribute('aria-label', 'Main navigation');

  const nav = document.createElement('nav');
  const ul = document.createElement('ul');
  ul.className = 'nav-list';
  ul.setAttribute('role', 'menubar');

  NAV_ITEMS.forEach(({ id, icon, label }) => {
    const li = document.createElement('li');
    li.setAttribute('role', 'none');
    const a = document.createElement('a');
    a.className = `nav-link${activeRoute === id ? ' active' : ''}`;
    a.href = `#${id}`;
    a.setAttribute('role', 'menuitem');
    a.setAttribute('aria-current', activeRoute === id ? 'page' : 'false');
    a.innerHTML = `<span class="nav-icon" aria-hidden="true">${icon}</span><span>${label}</span>`;
    a.addEventListener('click', (e) => { e.preventDefault(); router.navigate(id); });
    li.appendChild(a);
    ul.appendChild(li);
  });

  nav.appendChild(ul);
  sidebar.appendChild(nav);

  const sidebarFooter = document.createElement('div');
  sidebarFooter.style.cssText = 'font-size:0.75rem;color:var(--text-muted);text-align:center;padding:0.5rem';
  sidebarFooter.innerHTML = `<span>v1.0.0 — Demo Mode</span>`;
  sidebar.appendChild(sidebarFooter);

  return sidebar;
}

/* ─── Scan Loading Indicator ──────────────────────────────────────── */
export function createScanLoader(steps = ['Preprocessing input…', 'Running classifier…', 'Generating report…']) {
  let stepIndex = 0;
  let interval;

  const box = document.createElement('div');
  box.className = 'scan-progress-box';
  box.setAttribute('role', 'status');
  box.setAttribute('aria-live', 'polite');
  box.innerHTML = `
    <div class="scan-radar" aria-hidden="true"></div>
    <p class="scan-step-text" id="scan-step-label">${steps[0]}</p>
    <p style="font-size:0.775rem;color:var(--text-muted)">Analysing — please wait</p>
  `;

  const label = box.querySelector('#scan-step-label');

  function start() {
    interval = setInterval(() => {
      stepIndex = (stepIndex + 1) % steps.length;
      label.textContent = steps[stepIndex];
    }, 1000);
  }

  function stop() {
    clearInterval(interval);
  }

  return { el: box, start, stop };
}

/* ─── Confidence Score Bar ────────────────────────────────────────── */
/**
 * @param {number} score 0-100
 * @param {string} label
 */
export function createConfidenceBar(score, label = 'Confidence') {
  const level = score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low';
  const div = document.createElement('div');
  div.className = 'confidence-bar-container';
  div.innerHTML = `
    <div class="confidence-bar-label">
      <span>${label}</span>
      <span style="font-family:var(--font-code);color:var(--cyan-300)">${score.toFixed(1)}%</span>
    </div>
    <div class="confidence-bar" role="progressbar" aria-valuenow="${score}" aria-valuemin="0" aria-valuemax="100" aria-label="${label}: ${score}%">
      <div class="confidence-bar-fill ${level}" style="width:0%"></div>
    </div>
  `;
  // Animate fill
  requestAnimationFrame(() => {
    setTimeout(() => {
      const fill = div.querySelector('.confidence-bar-fill');
      if (fill) fill.style.width = `${score}%`;
    }, 50);
  });
  return div;
}

/* ─── Modal Helper ────────────────────────────────────────────────── */
export function openModal({ title, bodyHTML, footerHTML = '' }) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.id = 'active-modal';
  overlay.setAttribute('role', 'dialog');
  overlay.setAttribute('aria-modal', 'true');
  overlay.setAttribute('aria-labelledby', 'modal-title');

  overlay.innerHTML = `
    <div class="modal-card">
      <div class="modal-header">
        <h2 class="card-title" id="modal-title">${title}</h2>
        <button class="btn btn-secondary btn-sm" id="modal-close-btn" aria-label="Close dialog">✕</button>
      </div>
      <div class="modal-body">${bodyHTML}</div>
      ${footerHTML ? `<div class="modal-footer">${footerHTML}</div>` : ''}
    </div>
  `;

  document.body.appendChild(overlay);
  requestAnimationFrame(() => overlay.classList.add('active'));

  const closeModal = () => {
    overlay.classList.remove('active');
    setTimeout(() => overlay.remove(), 300);
  };

  overlay.querySelector('#modal-close-btn').addEventListener('click', closeModal);
  overlay.addEventListener('click', (e) => { if (e.target === overlay) closeModal(); });
  document.addEventListener('keydown', function handler(e) {
    if (e.key === 'Escape') { closeModal(); document.removeEventListener('keydown', handler); }
  });

  return { close: closeModal };
}

/* ─── Demo Data Notice Banner ─────────────────────────────────────── */
export function createDemoBanner(message = '⚠️ DEMO DATA — All values displayed below are synthetic sample data for UI demonstration purposes only.') {
  const div = document.createElement('div');
  div.className = 'demo-banner';
  div.setAttribute('role', 'note');
  div.setAttribute('aria-label', 'Demo data notice');
  div.innerHTML = message;
  return div;
}

/* ─── Feature Analysis List ───────────────────────────────────────── */
export function createFeatureList(features) {
  const ul = document.createElement('ul');
  ul.className = 'feature-analysis-list';
  ul.setAttribute('aria-label', 'Feature analysis results');
  features.forEach(({ icon, text, type }) => {
    const li = document.createElement('li');
    li.innerHTML = `<span class="${type}" aria-hidden="true">${icon}</span><span>${text}</span>`;
    ul.appendChild(li);
  });
  return ul;
}

/* ─── History Feed ────────────────────────────────────────────────── */
export class HistoryFeed {
  constructor(maxItems = 10) {
    this.items = [];
    this.maxItems = maxItems;
    this.container = document.createElement('div');
    this.container.className = 'history-list';
    this.container.setAttribute('aria-label', 'Analysis history');
    this.container.setAttribute('role', 'log');
    this.container.setAttribute('aria-live', 'polite');
  }

  add({ text, badge, time = new Date().toLocaleTimeString() }) {
    const item = document.createElement('div');
    item.className = 'history-item';
    item.innerHTML = `
      <span class="badge ${badge.class}">${badge.label}</span>
      <span class="history-text" title="${text}">${text}</span>
      <span class="history-time">${time}</span>
    `;
    this.container.prepend(item);
    this.items.unshift({ text, badge, time });
    if (this.container.children.length > this.maxItems) {
      this.container.lastElementChild?.remove();
      this.items = this.items.slice(0, this.maxItems);
    }
  }

  getEl() { return this.container; }
}
