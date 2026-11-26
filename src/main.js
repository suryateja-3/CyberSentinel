/* ==========================================================================
   CYBER SENTINEL - APPLICATION ENTRY POINT
   Bootstraps router, header, sidebar, and page rendering
   ========================================================================== */

import './styles/main.css';
import './styles/components.css';
import './styles/pages.css';

import { Router }             from './router/router.js';
import { renderHeader, renderSidebar, pollApiStatus } from './components/ui.js';

import { renderLandingPage }     from './pages/landing.js';
import { renderDashboardPage }   from './pages/dashboard.js';
import { renderFakeNewsPage }    from './pages/fakeNews.js';
import { renderFraudPage }       from './pages/fraud.js';
import { renderURLPage }         from './pages/urlDetection.js';
import { renderPerformancePage } from './pages/performance.js';
import { renderAboutPage }       from './pages/about.js';

/* ── Route Map ────────────────────────────────────────────────────── */
const ROUTES = {
  'landing':     () => renderLandingPage(router),
  'dashboard':   () => renderDashboardPage(router),
  'fake-news':   () => renderFakeNewsPage(),
  'fraud':       () => renderFraudPage(),
  'url':         () => renderURLPage(),
  'performance': () => renderPerformancePage(),
  'about':       () => renderAboutPage(),
};

/* ── Router ───────────────────────────────────────────────────────── */
const router = new Router(ROUTES);

/* ── App Shell ────────────────────────────────────────────────────── */
function buildShell() {
  const app = document.getElementById('app');
  app.innerHTML = '';

  const header = renderHeader(router);
  app.appendChild(header);

  const layoutContainer = document.createElement('div');
  layoutContainer.className = 'layout-container';

  /* Sidebar — hidden on landing page, shown on inner pages */
  const sidebarPlaceholder = document.createElement('div');
  sidebarPlaceholder.id = 'sidebar-mount';

  const mainContent = document.createElement('main');
  mainContent.className = 'main-content';
  mainContent.id = 'main-content';
  mainContent.setAttribute('role', 'main');
  mainContent.setAttribute('aria-label', 'Main content area');

  layoutContainer.appendChild(sidebarPlaceholder);
  layoutContainer.appendChild(mainContent);
  app.appendChild(layoutContainer);

  return { sidebarPlaceholder, mainContent };
}

/* ── Render Page ──────────────────────────────────────────────────── */
function renderPage(routeId, mainContent, sidebarPlaceholder) {
  /* Manage sidebar visibility */
  const hideSidebarOn = ['landing'];
  if (hideSidebarOn.includes(routeId)) {
    sidebarPlaceholder.innerHTML = '';
  } else {
    sidebarPlaceholder.innerHTML = '';
    const sidebar = renderSidebar(router, routeId);
    sidebarPlaceholder.appendChild(sidebar);
  }

  /* Render page with fade animation */
  mainContent.innerHTML = '';
  const pageEl = ROUTES[routeId] ? ROUTES[routeId]() : ROUTES['landing']();

  /* Wrap non-landing pages in a view-page div if they don't have one */
  mainContent.appendChild(pageEl);

  /* Scroll to top */
  window.scrollTo({ top: 0, behavior: 'smooth' });

  /* Update document title */
  const titles = {
    landing:     'CyberSentinel — AI Cybersecurity Platform',
    dashboard:   'Dashboard | CyberSentinel',
    'fake-news': 'Fake News Detection | CyberSentinel',
    fraud:       'Fraud Detection | CyberSentinel',
    url:         'URL Detection | CyberSentinel',
    performance: 'Model Performance | CyberSentinel',
    about:       'About | CyberSentinel',
  };
  document.title = titles[routeId] || 'CyberSentinel';

  /* Update meta description for basic SEO */
  let metaDesc = document.querySelector('meta[name="description"]');
  if (!metaDesc) {
    metaDesc = document.createElement('meta');
    metaDesc.name = 'description';
    document.head.appendChild(metaDesc);
  }
  const descs = {
    landing:     'CyberSentinel — AI-powered platform for fake news detection, online fraud detection, and URL phishing analysis.',
    dashboard:   'Platform overview and recent scan activity — CyberSentinel.',
    'fake-news': 'Paste any article to detect fake news using NLP classification — CyberSentinel.',
    fraud:       'Analyse transaction metadata for fraud risk with AI — CyberSentinel.',
    url:         'Scan any URL for phishing, malware, and threats — CyberSentinel.',
    performance: 'View model accuracy, F1 scores, and confusion matrices for all detectors — CyberSentinel.',
    about:       'About CyberSentinel — architecture, tech stack, and API reference.',
  };
  metaDesc.content = descs[routeId] || descs.landing;
}

/* ── Bootstrap ────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const { sidebarPlaceholder, mainContent } = buildShell();

  router.onChange((routeId) => {
    renderPage(routeId, mainContent, sidebarPlaceholder);
  });

  router.start();

  /* Poll API health status on load, then every 30 seconds */
  pollApiStatus();
  setInterval(pollApiStatus, 30_000);
});
