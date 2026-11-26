/* ==========================================================================
   CYBER SENTINEL - CLIENT-SIDE ROUTER
   Hash-based SPA routing with history support
   ========================================================================== */

export class Router {
  constructor(routes) {
    this.routes    = routes;  // { routeId: renderFn }
    this.current   = null;
    this.listeners = [];

    window.addEventListener('hashchange', () => this._handleHashChange());
  }

  /**
   * Navigate to a route by ID.
   * @param {string} routeId
   */
  navigate(routeId) {
    window.location.hash = routeId;
  }

  /**
   * Register a listener called on every route change.
   * @param {function} fn
   */
  onChange(fn) {
    this.listeners.push(fn);
  }

  /** Start the router — resolve the current hash or default to 'landing'. */
  start() {
    this._handleHashChange();
  }

  _handleHashChange() {
    const hash    = window.location.hash.replace('#', '') || 'landing';
    const routeId = this.routes[hash] ? hash : 'landing';

    if (routeId === this.current) return;
    this.current = routeId;
    this.listeners.forEach(fn => fn(routeId));
  }
}
