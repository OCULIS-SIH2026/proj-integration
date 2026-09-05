/**
 * frontend/js/components/dashboard.js - Dashboard Overview Component
 */

const DashboardComponent = {
  currentFilter: 'all',
  searchQuery: '',
  screeningsData: [],
  statsData: {},

  setSearchQuery(q) {
    // Store query so it persists if component re-renders
    this.searchQuery = (q || '').trim();
    // If data already loaded, filter immediately
    if (this.screeningsData.length > 0 || this._hasLoaded) {
      this.renderTableRows();
    }
    // If data not loaded yet, renderTableRows() will be called from loadData()
  },

  render(container) {
    // Reset data state each render; preserve searchQuery so global search persists
    this.screeningsData = [];
    this.statsData = {};
    this._hasLoaded = false;
    container.innerHTML = `
      <div class="header-actions" style="margin-bottom: 24px; justify-content: space-between; display: flex; align-items: flex-end;">
        <div>
          <h1 style="margin-bottom: 4px;">Clinical Screening Dashboard</h1>
          <p style="margin: 0; color: var(--neutral);">Real-time Tele-Ophthalmology Telemetry & Triage Worklist</p>
        </div>
        <button id="btn-dashboard-new-screening" class="btn btn-primary btn-md">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>
          New Screening
        </button>
      </div>

      <!-- KPI Stat Cards -->
      <div class="grid-cols-4" style="margin-bottom: 28px;">
        <div class="stat-card">
          <div class="stat-header">
            <span class="stat-label">Total Screenings</span>
            <span class="chip chip-neutral" style="font-size: 11px;">All Time</span>
          </div>
          <div class="stat-value" id="kpi-total-screenings">-</div>
          <div class="stat-meta">
            <svg width="14" height="14" fill="none" stroke="var(--success)" stroke-width="2" viewBox="0 0 24 24"><path d="M5 10l7-7m0 0l7 7m-7-7v18"/></svg>
            <span style="color: var(--success); font-weight: 600;">+12%</span> vs last week
          </div>
        </div>

        <div class="stat-card" style="border-left: 4px solid var(--error);">
          <div class="stat-header">
            <span class="stat-label">Referable Cases</span>
            <span class="chip chip-error" style="font-size: 11px;">Level ≥ 2</span>
          </div>
          <div class="stat-value" id="kpi-referable-cases" style="color: var(--error);">-</div>
          <div class="stat-meta">
            <span id="kpi-referable-pct" style="font-weight: 600;">-%</span> triage referral rate
          </div>
        </div>

        <div class="stat-card" style="border-left: 4px solid var(--accent);">
          <div class="stat-header">
            <span class="stat-label">Pending Doctor Review</span>
            <span class="chip chip-warning" style="font-size: 11px;">Action Req</span>
          </div>
          <div class="stat-value" id="kpi-pending-review" style="color: var(--warning);">-</div>
          <div class="stat-meta">
            Target SLA: <span style="font-weight: 600; color: var(--text-primary);">&lt; 30s per case</span>
          </div>
        </div>

        <div class="stat-card" style="border-left: 4px solid var(--success);">
          <div class="stat-header">
            <span class="stat-label">Reviewed & Signed</span>
            <span class="chip chip-success" style="font-size: 11px;">Validated</span>
          </div>
          <div class="stat-value" id="kpi-reviewed-cases" style="color: var(--success);">-</div>
          <div class="stat-meta">
            Avg review time: <span style="font-weight: 600;">24.8 sec</span>
          </div>
        </div>
      </div>

      <!-- Worklist Table Card -->
      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">Screening Worklist & Telemetry</div>
            <div class="card-subtitle">Automated AI 0–4 Classifications with Ophthalmologist Human-in-the-Loop Decisions</div>
          </div>
          <!-- Filter Tabs -->
          <div style="display: flex; gap: 8px;">
            <button class="btn btn-sm btn-secondary filter-btn active" data-filter="all">All Cases</button>
            <button class="btn btn-sm btn-secondary filter-btn" data-filter="referable">Referable (≥2)</button>
            <button class="btn btn-sm btn-secondary filter-btn" data-filter="pending">Pending Review</button>
            <button class="btn btn-sm btn-secondary filter-btn" data-filter="reviewed">Reviewed</button>
          </div>
        </div>

        <div class="data-table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Patient ID / Name</th>
                <th>Eye / Age</th>
                <th>Image Quality</th>
                <th>AI Classification</th>
                <th>Confidence</th>
                <th>Triage Status</th>
                <th>Doctor Validation</th>
                <th style="text-align: right;">Action</th>
              </tr>
            </thead>
            <tbody id="screenings-table-body">
              <tr>
                <td colspan="8" style="text-align: center; padding: 32px; color: var(--neutral);">Loading screenings...</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;

    document.getElementById('btn-dashboard-new-screening').addEventListener('click', () => {
      App.navigateTo('screening');
    });

    // Attach filter tabs
    container.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        container.querySelectorAll('.filter-btn').forEach(b => {
          b.classList.remove('active', 'btn-primary');
          b.classList.add('btn-secondary');
        });
        btn.classList.remove('btn-secondary');
        btn.classList.add('active', 'btn-primary');
        this.currentFilter = btn.dataset.filter;
        this.renderTableRows();
      });
    });

    this.loadData();
  },

  async loadData() {
    try {
      const resp = await API.getScreenings();
      this.screeningsData = resp.screenings || [];
      this.statsData = resp.stats || {};
      this._hasLoaded = true;

      // Update KPIs
      const kpiTotal = document.getElementById('kpi-total-screenings');
      const kpiRef = document.getElementById('kpi-referable-cases');
      const kpiRefPct = document.getElementById('kpi-referable-pct');
      const kpiPending = document.getElementById('kpi-pending-review');
      const kpiReviewed = document.getElementById('kpi-reviewed-cases');
      if (kpiTotal) kpiTotal.textContent = this.statsData.total_screenings || 0;
      if (kpiRef) kpiRef.textContent = this.statsData.referable_cases || 0;
      if (kpiRefPct) kpiRefPct.textContent = `${this.statsData.referable_percentage || 0}%`;
      if (kpiPending) kpiPending.textContent = this.statsData.pending_review || 0;
      if (kpiReviewed) kpiReviewed.textContent = this.statsData.reviewed_cases || 0;

      this.renderTableRows();
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      const tbody = document.getElementById('screenings-table-body');
      if (tbody) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 24px; color: var(--error);">Error loading data: ${err.message}</td></tr>`;
      }
    }
  },

  renderTableRows() {
    const tbody = document.getElementById('screenings-table-body');
    if (!tbody) return;

    let list = [...this.screeningsData];
    if (this.currentFilter === 'referable') {
      list = list.filter(item => item.referable === 1 || item.referable_dr === true);
    } else if (this.currentFilter === 'pending') {
      list = list.filter(item => item.doctor_status === 'pending');
    } else if (this.currentFilter === 'reviewed') {
      list = list.filter(item => item.doctor_status !== 'pending');
    }

    if (this.searchQuery && this.searchQuery.trim()) {
      const q = this.searchQuery.toLowerCase().trim();
      list = list.filter(item => {
        const predLabel = (item.prediction && item.prediction.label) || item.dr_label || '';
        const predStage = (item.prediction && item.prediction.stage != null) ? item.prediction.stage : item.dr_level;
        return (
          (item.patient_id && item.patient_id.toLowerCase().includes(q)) ||
          (item.patient_name && item.patient_name.toLowerCase().includes(q)) ||
          predLabel.toLowerCase().includes(q) ||
          (item.doctor_status && item.doctor_status.toLowerCase().includes(q)) ||
          (item.id && item.id.toLowerCase().includes(q)) ||
          `level ${predStage}`.includes(q) ||
          `stage ${predStage}`.includes(q)
        );
      });
    }

    if (list.length === 0) {
      const emptyMsg = this.searchQuery ? `No clinical cases found matching "${this.escapeHtml(this.searchQuery)}".` : 'No screenings found matching this filter.';
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 24px; color: var(--neutral);">${emptyMsg}</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(item => {
      const qRaw = (item.quality && item.quality.status) || item.image_quality_status || 'Pass';
      const qStatus = String(qRaw).toUpperCase();
      const qClass = (qStatus === 'GOOD' || qStatus === 'PASS') ? 'chip-success' : (qStatus === 'BORDERLINE' ? 'chip-warning' : 'chip-error');

      const level = (item.prediction && item.prediction.stage !== null && item.prediction.stage !== undefined)
        ? item.prediction.stage
        : (item.dr_level !== null && item.dr_level !== undefined ? item.dr_level : '-');
      const label = (item.prediction && item.prediction.label) || item.dr_label || 'Inconclusive';
      const confVal = (item.prediction && item.prediction.confidence !== undefined) ? item.prediction.confidence : (item.confidence || 0);
      const conf = Math.round(Number(confVal) * 100);

      const isReferable = (item.triage && item.triage.is_referable !== undefined)
        ? Boolean(item.triage.is_referable)
        : (item.referable === 1 || item.referable_dr === true);
      const refChip = isReferable
        ? `<span class="chip chip-error">REFERABLE</span>`
        : `<span class="chip chip-success">NON-REFERABLE</span>`;

      const docStatus = item.doctor_status || 'pending';
      let docChip = `<span class="chip chip-warning">Pending Review</span>`;
      if (docStatus === 'accepted') {
        docChip = `<span class="chip chip-success">Validated (L${item.doctor_dr_level !== null ? item.doctor_dr_level : level})</span>`;
      } else if (docStatus === 'overridden') {
        docChip = `<span class="chip chip-error">Overridden (L${item.doctor_dr_level})</span>`;
      }

      return `
        <tr>
          <td>
            <div style="font-weight: 700; color: var(--text-primary); font-family: var(--font-code); font-size: 13px;">${item.patient_id}</div>
            <div style="font-size: 12px; color: var(--neutral);">${item.patient_name || 'Walk-in'}</div>
          </td>
          <td>
            <span class="chip chip-neutral" style="font-size: 11px; padding: 2px 6px;">${item.eye || 'OD'}</span>
            <span style="font-size: 13px; color: var(--text-secondary); margin-left: 4px;">${item.patient_age || 55}y</span>
          </td>
          <td>
            <span class="chip ${qClass}">${qStatus}</span>
          </td>
          <td>
            <div style="font-weight: 600; color: var(--primary);">Level ${level}</div>
            <div style="font-size: 12px; color: var(--text-secondary);">${label}</div>
          </td>
          <td>
            <span style="font-family: var(--font-code); font-weight: 600;">${conf}%</span>
          </td>
          <td>${refChip}</td>
          <td>${docChip}</td>
          <td style="text-align: right;">
            <button class="btn btn-sm btn-secondary view-case-btn" data-id="${item.id}">
              Inspect & Review
            </button>
          </td>
        </tr>
      `;
    }).join('');

    // Attach click handlers to row action buttons
    tbody.querySelectorAll('.view-case-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.id;
        App.viewScreeningCase(id);
      });
    });
  },

  escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
};
