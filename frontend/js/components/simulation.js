/**
 * frontend/js/components/simulation.js - Telemedicine Simulink Workflow Simulation Studio (Person 3)
 */

const SimulationComponent = {
  currentScenario: 'scenario_a',
  simData: null,
  comparisonData: null,

  async render(container) {
    container.innerHTML = `
      <div class="header-actions" style="margin-bottom: 24px; justify-content: space-between; display: flex; align-items: flex-end;">
        <div>
          <h1 style="margin-bottom: 4px;">Telemedicine Workflow Simulink Simulation</h1>
          <p style="margin: 0; color: var(--neutral);">
            Discrete-Event Queuing Network Modeling 100,000+ Patients/Year Across Rural Health Centers
          </p>
        </div>
        <!-- Scenario Presets -->
        <div style="display: flex; gap: 8px;">
          <button class="btn btn-sm btn-secondary scenario-preset active" data-scenario="scenario_a">Scenario A (100k)</button>
          <button class="btn btn-sm btn-secondary scenario-preset" data-scenario="scenario_b">Scenario B (150k)</button>
          <button class="btn btn-sm btn-secondary scenario-preset" data-scenario="scenario_c">Scenario C (200k Stress)</button>
          <button class="btn btn-sm btn-secondary scenario-preset" data-scenario="scenario_d">Scenario D (200k Optimized)</button>
        </div>
      </div>

      <!-- Live Telemetry KPI Cards -->
      <div class="grid-cols-4" style="margin-bottom: 24px;">
        <div class="stat-card">
          <div class="stat-label">Annual Throughput</div>
          <div class="stat-value" id="sim-throughput">-</div>
          <div class="stat-meta">
            <span id="sim-daily-arrivals" style="font-weight: 600;">-</span> patients / clinic day
          </div>
        </div>

        <div class="stat-card" id="card-doctor-util">
          <div class="stat-label">Ophthalmologist Utilization</div>
          <div class="stat-value" id="sim-doctor-util">-</div>
          <div class="stat-meta">
            Queue length: <span id="sim-doctor-queue" style="font-weight: 600;">- cases</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-label">AI Cloud Inference Load</div>
          <div class="stat-value" id="sim-ai-util">-</div>
          <div class="stat-meta">
            Inference queue: <span id="sim-ai-latency" style="font-weight: 600;">- sec</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-label">End-to-End Turnaround</div>
          <div class="stat-value" id="sim-turnaround">-</div>
          <div class="stat-meta">
            From camera to validated report
          </div>
        </div>
      </div>

      <!-- Bottleneck Diagnosis Banner -->
      <div id="sim-bottleneck-banner" class="card" style="margin-bottom: 24px; border-left: 5px solid var(--success); background-color: var(--surface);">
        <div style="display: flex; gap: 16px; align-items: center;">
          <div id="sim-bottleneck-icon" style="color: var(--success);">
            <svg width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          </div>
          <div>
            <div style="font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 2px;">
              System Bottleneck: <span id="sim-bottleneck-stage">Optimal (No Bottleneck)</span>
            </div>
            <div id="sim-bottleneck-rec" style="font-size: 13px; color: var(--text-secondary);">
              System operating within clinical SLA thresholds.
            </div>
          </div>
        </div>
      </div>

      <!-- Interactive Parameter Sliders & Queuing Topology -->
      <div class="grid-cols-2" style="margin-bottom: 24px;">
        <!-- Controls Column -->
        <div class="card">
          <div class="card-title" style="margin-bottom: 16px;">Telemedicine Network Parameters</div>

          <div class="form-group">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span class="stat-label">Annual Patient Volume:</span>
              <span id="slider-val-patients" class="code-font" style="font-weight: 600; color: var(--primary);">100,000</span>
            </div>
            <input type="range" id="slider-patients" min="50000" max="300000" step="10000" value="100000" style="width: 100%; accent-color: var(--primary);">
          </div>

          <div class="form-group">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span class="stat-label">Remote PHC Camera Stations:</span>
              <span id="slider-val-cameras" class="code-font" style="font-weight: 600; color: var(--primary);">25 Centers</span>
            </div>
            <input type="range" id="slider-cameras" min="10" max="80" step="2" value="25" style="width: 100%; accent-color: var(--primary);">
          </div>

          <div class="form-group">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span class="stat-label">Network Bandwidth (Mbps):</span>
              <span id="slider-val-bandwidth" class="code-font" style="font-weight: 600; color: var(--primary);">10 Mbps</span>
            </div>
            <input type="range" id="slider-bandwidth" min="2" max="50" step="2" value="10" style="width: 100%; accent-color: var(--primary);">
          </div>

          <div class="form-group">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span class="stat-label">AI Cloud GPU Nodes:</span>
              <span id="slider-val-ai" class="code-font" style="font-weight: 600; color: var(--primary);">2 Nodes</span>
            </div>
            <input type="range" id="slider-ai" min="1" max="8" step="1" value="2" style="width: 100%; accent-color: var(--primary);">
          </div>

          <div class="form-group">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span class="stat-label">Reviewing Ophthalmologists:</span>
              <span id="slider-val-doctors" class="code-font" style="font-weight: 600; color: var(--primary);">4 Doctors</span>
            </div>
            <input type="range" id="slider-doctors" min="1" max="12" step="1" value="4" style="width: 100%; accent-color: var(--primary);">
          </div>

          <div class="form-group" style="margin-bottom: 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span class="stat-label">Doctor Mean Review Time:</span>
              <span id="slider-val-review-time" class="code-font" style="font-weight: 600; color: var(--primary);">28 Sec</span>
            </div>
            <input type="range" id="slider-review-time" min="15" max="60" step="1" value="28" style="width: 100%; accent-color: var(--primary);">
          </div>
        </div>

        <!-- Telemedicine Workflow Architecture Block Diagram -->
        <div class="card">
          <div class="card-title" style="margin-bottom: 12px;">Simulink / SimEvents Queue Flow</div>
          
          <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 14px;">
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: var(--surface-raised); border-radius: 8px;">
              <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 28px; height: 28px; border-radius: 6px; background: var(--primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px;">1</div>
                <div>
                  <div style="font-weight: 600; font-size: 13px;">Patient Arrival Generator</div>
                  <div style="font-size: 11px; color: var(--neutral);">Poisson arrival process across health centers</div>
                </div>
              </div>
              <span class="code-font" id="topo-arrival" style="font-size: 12px; font-weight: 600;">50 pts/hr</span>
            </div>

            <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: var(--surface-raised); border-radius: 8px;">
              <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 28px; height: 28px; border-radius: 6px; background: var(--primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px;">2</div>
                <div>
                  <div style="font-weight: 600; font-size: 13px;">Fundus Camera Stations</div>
                  <div style="font-size: 11px; color: var(--neutral);">Bilateral 45° macular/disc capture (~4 min)</div>
                </div>
              </div>
              <span class="code-font" id="topo-camera-util" style="font-size: 12px; font-weight: 600;">util: 42%</span>
            </div>

            <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: var(--surface-raised); border-radius: 8px;">
              <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 28px; height: 28px; border-radius: 6px; background: var(--primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px;">3</div>
                <div>
                  <div style="font-weight: 600; font-size: 13px;">Telecom Uplink Store & Forward</div>
                  <div style="font-size: 11px; color: var(--neutral);">Encrypted DICOM / JPEG transfer</div>
                </div>
              </div>
              <span class="code-font" id="topo-net-delay" style="font-size: 12px; font-weight: 600;">delay: 2.4s</span>
            </div>

            <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: var(--surface-raised); border-radius: 8px;">
              <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 28px; height: 28px; border-radius: 6px; background: var(--primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px;">4</div>
                <div>
                  <div style="font-weight: 600; font-size: 13px;">AI Pre-Screening Inference Queue</div>
                  <div style="font-size: 11px; color: var(--neutral);">EfficientNet-B0 + Grad-CAM generation</div>
                </div>
              </div>
              <span class="code-font" id="topo-ai-util" style="font-size: 12px; font-weight: 600;">util: 1.2%</span>
            </div>

            <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: var(--surface-raised); border-radius: 8px;">
              <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 28px; height: 28px; border-radius: 6px; background: var(--primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px;">5</div>
                <div>
                  <div style="font-weight: 600; font-size: 13px;">Ophthalmologist Review Multiserver Queue</div>
                  <div style="font-size: 11px; color: var(--neutral);">Referable case validation & digital sign-off</div>
                </div>
              </div>
              <span class="code-font" id="topo-doctor-util" style="font-size: 12px; font-weight: 600;">util: 48%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Scenarios Comparison Matrix Table -->
      <div class="card">
        <div class="card-title" style="margin-bottom: 12px;">Scenario Benchmark & Capacity Planning Matrix</div>
        <div class="data-table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Scenario</th>
                <th>Annual Patients</th>
                <th>Cameras</th>
                <th>Doctors</th>
                <th>AI Util %</th>
                <th>Doctor Util %</th>
                <th>Doc Wait Time</th>
                <th>System Status</th>
              </tr>
            </thead>
            <tbody id="sim-comparison-body">
              <tr><td colspan="8" style="text-align: center; padding: 20px;">Loading scenario comparisons...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    `;

    this.setupEvents(container);
    await this.updateSimulation(container);
    await this.loadComparison(container);
  },

  setupEvents(container) {
    // Scenario preset buttons
    container.querySelectorAll('.scenario-preset').forEach(btn => {
      btn.addEventListener('click', async () => {
        container.querySelectorAll('.scenario-preset').forEach(b => {
          b.classList.remove('active', 'btn-primary');
          b.classList.add('btn-secondary');
        });
        btn.classList.remove('btn-secondary');
        btn.classList.add('active', 'btn-primary');
        this.currentScenario = btn.dataset.scenario;
        await this.syncSlidersWithPreset(container, this.currentScenario);
        await this.updateSimulation(container);
      });
    });

    // Sliders
    const sliders = ['patients', 'cameras', 'bandwidth', 'ai', 'doctors', 'review-time'];
    sliders.forEach(s => {
      const el = container.querySelector(`#slider-${s}`);
      el.addEventListener('input', () => {
        this.updateSliderLabel(container, s, el.value);
        this.runCustomSimulation(container);
      });
    });
  },

  updateSliderLabel(container, name, val) {
    if (name === 'patients') container.querySelector('#slider-val-patients').textContent = Number(val).toLocaleString();
    if (name === 'cameras') container.querySelector('#slider-val-cameras').textContent = `${val} Centers`;
    if (name === 'bandwidth') container.querySelector('#slider-val-bandwidth').textContent = `${val} Mbps`;
    if (name === 'ai') container.querySelector('#slider-val-ai').textContent = `${val} Nodes`;
    if (name === 'doctors') container.querySelector('#slider-val-doctors').textContent = `${val} Doctors`;
    if (name === 'review-time') container.querySelector('#slider-val-review-time').textContent = `${val} Sec`;
  },

  async syncSlidersWithPreset(container, scenarioKey) {
    const presets = {
      scenario_a: { patients: 100000, cameras: 25, bandwidth: 10, ai: 2, doctors: 4, review_time: 28 },
      scenario_b: { patients: 150000, cameras: 38, bandwidth: 10, ai: 3, doctors: 4, review_time: 28 },
      scenario_c: { patients: 200000, cameras: 50, bandwidth: 10, ai: 3, doctors: 4, review_time: 28 },
      scenario_d: { patients: 200000, cameras: 50, bandwidth: 25, ai: 4, doctors: 6, review_time: 24 }
    };
    const p = presets[scenarioKey] || presets.scenario_a;

    container.querySelector('#slider-patients').value = p.patients;
    container.querySelector('#slider-cameras').value = p.cameras;
    container.querySelector('#slider-bandwidth').value = p.bandwidth;
    container.querySelector('#slider-ai').value = p.ai;
    container.querySelector('#slider-doctors').value = p.doctors;
    container.querySelector('#slider-review-time').value = p.review_time;

    this.updateSliderLabel(container, 'patients', p.patients);
    this.updateSliderLabel(container, 'cameras', p.cameras);
    this.updateSliderLabel(container, 'bandwidth', p.bandwidth);
    this.updateSliderLabel(container, 'ai', p.ai);
    this.updateSliderLabel(container, 'doctors', p.doctors);
    this.updateSliderLabel(container, 'review-time', p.review_time);
  },

  async updateSimulation(container) {
    try {
      const res = await API.runSimulation(this.currentScenario);
      this.displayResults(container, res);
    } catch (err) {
      console.error('Simulation failed:', err);
    }
  },

  async runCustomSimulation(container) {
    const overrides = {
      annual_patients: parseInt(container.querySelector('#slider-patients').value),
      camera_centers: parseInt(container.querySelector('#slider-cameras').value),
      network_bandwidth_mbps: parseInt(container.querySelector('#slider-bandwidth').value),
      ai_workers: parseInt(container.querySelector('#slider-ai').value),
      doctor_count: parseInt(container.querySelector('#slider-doctors').value),
      doctor_review_sec: parseInt(container.querySelector('#slider-review-time').value)
    };

    try {
      const res = await API.runSimulation(this.currentScenario, overrides);
      this.displayResults(container, res);
    } catch (err) {
      console.error('Custom sim failed:', err);
    }
  },

  displayResults(container, res) {
    const r = res.results || {};
    const p = res.parameters || {};

    container.querySelector('#sim-throughput').textContent = Number(r.total_throughput_annual || 0).toLocaleString();
    container.querySelector('#sim-daily-arrivals').textContent = `${p.daily_patients || 0}`;

    const docUtil = r.doctor_utilization_pct || 0;
    const docCard = container.querySelector('#card-doctor-util');
    const docUtilEl = container.querySelector('#sim-doctor-util');
    docUtilEl.textContent = `${docUtil}%`;
    container.querySelector('#sim-doctor-queue').textContent = `${r.doctor_queue_cases || 0} cases (${r.doctor_wait_time_min}m)`;

    if (docUtil >= 95) {
      docCard.style.borderLeft = '4px solid var(--error)';
      docUtilEl.style.color = 'var(--error)';
    } else {
      docCard.style.borderLeft = '4px solid var(--success)';
      docUtilEl.style.color = 'var(--success)';
    }

    container.querySelector('#sim-ai-util').textContent = `${r.ai_server_utilization_pct || 0}%`;
    container.querySelector('#sim-ai-latency').textContent = `${r.ai_queue_latency_sec || 0}s`;

    container.querySelector('#sim-turnaround').textContent = `${r.total_turnaround_min || 0} min`;

    // Bottleneck banner
    const banner = container.querySelector('#sim-bottleneck-banner');
    const stageEl = container.querySelector('#sim-bottleneck-stage');
    const recEl = container.querySelector('#sim-bottleneck-rec');
    const iconEl = container.querySelector('#sim-bottleneck-icon');

    stageEl.textContent = r.bottleneck_stage;
    recEl.textContent = r.recommendation;

    if (r.is_stable) {
      banner.style.borderLeft = '5px solid var(--success)';
      iconEl.style.color = 'var(--success)';
    } else {
      banner.style.borderLeft = '5px solid var(--error)';
      iconEl.style.color = 'var(--error)';
    }

    // Update topology labels
    container.querySelector('#topo-arrival').textContent = `${p.hourly_patients || 0} pts/hr`;
    container.querySelector('#topo-camera-util').textContent = `util: ${r.camera_utilization_pct}%`;
    container.querySelector('#topo-net-delay').textContent = `delay: ${r.network_transfer_sec}s`;
    container.querySelector('#topo-ai-util').textContent = `util: ${r.ai_server_utilization_pct}%`;
    container.querySelector('#topo-doctor-util').textContent = `util: ${r.doctor_utilization_pct}%`;
  },

  async loadComparison(container) {
    try {
      const data = await API.getSimulationComparison();
      const tbody = container.querySelector('#sim-comparison-body');
      if (!tbody) return;

      tbody.innerHTML = Object.entries(data).map(([key, s]) => {
        const r = s.results;
        const p = s.parameters;
        const statusBadge = r.is_stable
          ? `<span class="chip chip-success">OPTIMAL SLA</span>`
          : `<span class="chip chip-error">BOTTLENECK</span>`;

        return `
          <tr>
            <td style="font-weight: 700; color: var(--text-primary);">${s.name.split(':')[0]}</td>
            <td class="code-font">${Number(r.total_throughput_annual).toLocaleString()}</td>
            <td>${p.camera_centers} PHCs</td>
            <td>${p.doctor_count} MDs</td>
            <td class="code-font">${r.ai_server_utilization_pct}%</td>
            <td class="code-font" style="font-weight: 700; color: ${r.doctor_utilization_pct >= 95 ? 'var(--error)' : 'var(--success)'};">${r.doctor_utilization_pct}%</td>
            <td>${r.doctor_wait_time_min} mins</td>
            <td>${statusBadge}</td>
          </tr>
        `;
      }).join('');
    } catch (err) {
      console.error('Failed to load comparison:', err);
    }
  }
};
