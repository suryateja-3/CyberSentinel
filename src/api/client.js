/* ==========================================================================
   CYBER SENTINEL - API CLIENT
   Handles all Flask REST API communication
   Base URL is read from a config; defaults to localhost:5000 for development
   ========================================================================== */

const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
};

/**
 * Core fetch wrapper with error normalisation, timeout, and status checking.
 * @param {string} path   - Endpoint path (e.g. '/api/detect/fake-news')
 * @param {object} opts   - Optional fetch options override
 * @returns {Promise<object>} - Parsed JSON response
 */
async function apiFetch(path, opts = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

  try {
    const response = await fetch(`${API_CONFIG.baseURL}${path}`, {
      signal: controller.signal,
      headers: { ...API_CONFIG.headers, ...opts.headers },
      ...opts,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errBody;
      try { errBody = await response.json(); } catch (_) { errBody = {}; }
      const err = new Error(errBody.message || `HTTP ${response.status}: ${response.statusText}`);
      err.status = response.status;
      err.body = errBody;
      throw err;
    }

    return await response.json();
  } catch (err) {
    clearTimeout(timeoutId);
    console.error(`[API Error] ${opts.method || 'GET'} ${path}:`, err);
    if (err.name === 'AbortError') {
      const timeoutErr = new Error('Request timed out. The server may be unavailable.');
      timeoutErr.isTimeout = true;
      throw timeoutErr;
    }
    if (err.name === 'TypeError' && (err.message === 'Failed to fetch' || err.message.includes('Network'))) {
      throw new Error(`Cannot connect to backend server at ${API_CONFIG.baseURL}. Please ensure the Flask API is running.`);
    }
    throw err;
  }
}

/* ── Health Check ─────────────────────────────────────────────────── */
export async function checkApiHealth() {
  return apiFetch('/api/health', { method: 'GET' });
}

/* ── Fake News Detection ─────────────────────────────────────────── */
/**
 * POST /api/detect/fake-news
 * @param {{ text: string, title?: string }} payload
 */
export async function detectFakeNews(payload) {
  return apiFetch('/api/detect/fake-news', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/* ── Evidence Verification ───────────────────────────────────────── */
/**
 * POST /api/verify/evidence
 * @param {{ text: string }} payload
 */
export async function verifyEvidence(payload) {
  return apiFetch('/api/verify/evidence', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/* ── Online Fraud Detection ──────────────────────────────────────── */
/**
 * POST /api/detect/fraud
 * @param {{ amount: number, merchant: string, location: string, device_id: string, hour: number }} payload
 */
export async function detectFraud(payload) {
  return apiFetch('/api/detect/fraud', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/* ── URL / Phishing Detection ────────────────────────────────────── */
/**
 * POST /api/detect/url
 * @param {{ url: string }} payload
 */
export async function detectURL(payload) {
  return apiFetch('/api/detect/url', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/* ── Model Performance Metrics ───────────────────────────────────── */
/**
 * GET /api/models/performance
 */
export async function getModelPerformance() {
  return apiFetch('/api/models/performance', { method: 'GET' });
}

/* ── Dashboard Stats ─────────────────────────────────────────────── */
/**
 * GET /api/dashboard/stats
 */
export async function getDashboardStats() {
  return apiFetch('/api/dashboard/stats', { method: 'GET' });
}

/* ── Model Status Health ─────────────────────────────────────────── */
/**
 * GET /api/models/status
 * Returns per-model load state, artifact existence, and last error.
 */
export async function checkModelStatus() {
  return apiFetch('/api/models/status', { method: 'GET' });
}

export default {
  checkApiHealth,
  checkModelStatus,
  detectFakeNews,
  verifyEvidence,
  detectFraud,
  detectURL,
  getModelPerformance,
  getDashboardStats,
};
