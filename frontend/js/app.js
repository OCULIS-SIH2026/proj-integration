/**
 * frontend/js/app.js - RetinaAI Main Application Controller
 * Precision Clinical Healthtech System Architecture
 */

const App = {
  activeTab: 'dashboard',
  currentScreeningCase: null,
  currentCaseImage: null,
  currentTheme: 'light',
  latencyCheckInterval: null,

  init() {
    this.initTheme();
    this.setupNavigation();
    this.setupGlobalSearch();
    this.startHeartbeatMonitor();
    this.navigateTo('dashboard');
  },

  /* ==========================================================================
     Theme Management (Precision Clinical Light / Dark Mode)
     ========================================================================== */
  initTheme() {
    // Read saved preference first, then system preference
    const savedTheme = localStorage.getItem('retinaai_theme');
    if (savedTheme === 'dark' || savedTheme === 'light') {
      this.applyTheme(savedTheme);
    } else {
      const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.applyTheme(prefersDark ? 'dark' : 'light');
    }
  },

  applyTheme(theme) {
    this.currentTheme = theme;
    // Must set on <html> element so CSS selectors [data-theme="dark"] work
    document.documentElement.setAttribute('data-theme', theme);
    const themeBtn = document.getElementById('btn-theme-toggle');
    if (themeBtn) {
      themeBtn.title = theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
      themeBtn.setAttribute('aria-label', theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode');
    }
  },

  toggleTheme() {
    const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
    this.applyTheme(newTheme);
    localStorage.setItem('retinaai_theme', newTheme);
  },

  /* ==========================================================================
     Navigation & Routing  (simple – no hash manipulation to avoid loops)
     ========================================================================== */
  setupNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const tab = item.dataset.tab;
        if (tab) {
          this.navigateTo(tab);
          this.toggleMobileSidebar(false);
        }
      });
    });
  },

  navigateTo(tab) {
    this.activeTab = tab;

    // Update sidebar active states
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.toggle('active', item.dataset.tab === tab);
    });

    const container = document.getElementById('view-container');
    if (!container) return;
    container.innerHTML = '';

    // Render corresponding component
    switch (tab) {
      case 'dashboard':
        DashboardComponent.render(container);
        break;
      case 'screening':
        ScreeningComponent.render(container);
        break;
      case 'quality':
        QualityComponent.render(container);
        break;
      case 'results':
        ResultsComponent.render(container);
        break;
      case 'review':
        ReviewComponent.render(container);
        break;
      case 'report':
        ReportComponent.render(container);
        break;
      case 'simulation':
        SimulationComponent.render(container);
        break;
      case 'apidocs':
        ApiDocsComponent.render(container);
        break;
      default:
        DashboardComponent.render(container);
    }

    // Scroll to top of the main scrollable area
    const mainContent = document.querySelector('.main-content');
    if (mainContent) mainContent.scrollTop = 0;
  },

  toggleMobileSidebar(isOpen) {
    const sidebar = document.getElementById('app-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (isOpen) {
      sidebar && sidebar.classList.add('open');
      overlay && overlay.classList.add('active');
    } else {
      sidebar && sidebar.classList.remove('open');
      overlay && overlay.classList.remove('active');
    }
  },

  /* ==========================================================================
     Global Patient Search
     Search defers to dashboard component's filter after ensuring it is rendered
     ========================================================================== */
  setupGlobalSearch() {
    const searchInput = document.getElementById('header-global-search');
    if (!searchInput) return;

    let debounceTimer = null;

    searchInput.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      const query = e.target.value;

      debounceTimer = setTimeout(() => {
        if (this.activeTab === 'dashboard') {
          // Already on dashboard — filter in place without re-rendering
          if (typeof DashboardComponent.setSearchQuery === 'function') {
            DashboardComponent.setSearchQuery(query);
          }
        } else {
          // Navigate to dashboard first, then search after component loads
          DashboardComponent.searchQuery = (query || '').trim();
          this.navigateTo('dashboard');
          // Data loads async, so setSearchQuery will pick it up via _hasLoaded check
        }
      }, 180);
    });

    // Escape clears search
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        searchInput.value = '';
        searchInput.blur();
        if (typeof DashboardComponent.setSearchQuery === 'function') {
          DashboardComponent.setSearchQuery('');
        }
      }
    });
  },

  /* ==========================================================================
     Live Health & Telemetry Monitor
     ========================================================================== */
  startHeartbeatMonitor() {
    const pingServer = async () => {
      const t0 = performance.now();
      try {
        const res = await fetch('/api/health', { method: 'GET', cache: 'no-store' });
        const latency = Math.round(performance.now() - t0);
        if (res.ok) {
          const latencyEl = document.getElementById('header-latency-text');
          const statusEl = document.getElementById('header-status-text');
          if (latencyEl) latencyEl.textContent = `${latency}ms`;
          if (statusEl) statusEl.textContent = 'System Operational';
        }
      } catch (err) {
        const statusEl = document.getElementById('header-status-text');
        if (statusEl) statusEl.textContent = 'Offline / Connecting';
      }
    };

    pingServer();
    this.latencyCheckInterval = setInterval(pingServer, 30000);
  },

  /* ==========================================================================
     Case Dossier View Helper
     ========================================================================== */
  async viewScreeningCase(id) {
    try {
      this.showToast(`Loading screening case ${id}...`, 'neutral');
      const detail = await API.getScreeningDetail(id);
      this.currentScreeningCase = detail;

      // Extract image preview if available (checking new visuals object first)
      if (detail.visuals && detail.visuals.original_image) {
        this.currentCaseImage = detail.visuals.original_image;
      } else if (detail.image_data) {
        this.currentCaseImage = detail.image_data;
      } else if (detail.visuals && detail.visuals.gradcam_overlay) {
        this.currentCaseImage = detail.visuals.gradcam_overlay;
      } else if (detail.explainability && detail.explainability.heatmap_base64) {
        this.currentCaseImage = detail.explainability.heatmap_base64;
      } else {
        // Fallback sample image
        const samples = await API.getSamples();
        const targetLevel = (detail.prediction && detail.prediction.stage != null)
          ? detail.prediction.stage
          : (detail.dr_prediction ? detail.dr_prediction.level : 2);
        const matchingSample = samples.find(s => s.dr_level === targetLevel) || samples[0];
        this.currentCaseImage = matchingSample ? matchingSample.image_data : '';
      }

      this.navigateTo('results');
    } catch (err) {
      console.error('Failed to view case:', err);
      this.showToast(`Error viewing case: ${err.message}`, 'error');
    }
  },

  /* ==========================================================================
     Toast Notifications
     ========================================================================== */
  showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast';

    let icon = `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4m0-4h.01"/></svg>`;
    if (type === 'success') {
      toast.style.borderLeftColor = 'var(--success)';
      icon = `<svg width="18" height="18" fill="none" stroke="var(--success)" stroke-width="2" viewBox="0 0 24 24"><path d="M5 13l4 4L19 7"/></svg>`;
    } else if (type === 'error') {
      toast.style.borderLeftColor = 'var(--error)';
      icon = `<svg width="18" height="18" fill="none" stroke="var(--error)" stroke-width="2" viewBox="0 0 24 24"><path d="M6 18L18 6M6 6l12 12"/></svg>`;
    } else if (type === 'warning') {
      toast.style.borderLeftColor = 'var(--warning)';
      icon = `<svg width="18" height="18" fill="none" stroke="var(--warning)" stroke-width="2" viewBox="0 0 24 24"><path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>`;
    }

    toast.innerHTML = `${icon} <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 200ms ease';
      setTimeout(() => toast.remove(), 200);
    }, 3200);
  }
};

document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
