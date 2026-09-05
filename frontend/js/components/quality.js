/**
 * frontend/js/components/quality.js - Image Quality Assessment & Recapture Component
 * Reads mock_response.json quality schema: quality.status, quality.overall_score, quality.metrics.*
 */

const QualityComponent = {
  render(container) {
    const caseData = App.currentScreeningCase;
    if (!caseData) {
      container.innerHTML = `
        <div class="card" style="text-align: center; padding: 48px;">
          <h2 style="margin-bottom: 8px;">No Active Screening Loaded</h2>
          <p>Please initiate a screening from the New Screening tab or select a case from the Dashboard.</p>
          <button class="btn btn-primary btn-md" onclick="App.navigateTo('screening')">Go to New Screening</button>
        </div>
      `;
      return;
    }

    // --- New schema: quality.* ---
    const q = caseData.quality || caseData.image_quality || {};
    const rawStatus = (q.status || 'Pass');
    const statusUpper = rawStatus.toUpperCase();
    const score = Math.round((q.overall_score || q.score || 0.9) * 100);
    const isAcceptable = q.is_acceptable !== false;
    const rejectionReasons = q.rejection_reasons || [];

    // Recapture flag (from triage or legacy)
    const recapture = !isAcceptable || (caseData.triage && !caseData.triage.is_referable && rejectionReasons.length > 0) || caseData.recapture_needed || false;
    const recaptureReason = rejectionReasons.join(' | ') || caseData.recapture_reason || '';
    const enhanced = (caseData.enhancement && caseData.enhancement.applied) || false;
    const enhancementMethod = (caseData.enhancement && caseData.enhancement.method) || 'CLAHE';

    // --- Status chip ---
    let statusChip = `<span class="chip chip-success" style="font-size: 14px; padding: 6px 16px;">PASS — GOOD QUALITY (${score}%)</span>`;
    if (statusUpper === 'BORDERLINE' || score < 70) {
      statusChip = `<span class="chip chip-warning" style="font-size: 14px; padding: 6px 16px;">BORDERLINE QUALITY (${score}%)</span>`;
    } else if (statusUpper === 'FAIL' || !isAcceptable) {
      statusChip = `<span class="chip chip-error" style="font-size: 14px; padding: 6px 16px;">FAIL — RECAPTURE REQUIRED (${score}%)</span>`;
    }

    // --- Metrics: support both new (sharpness/brightness/contrast/fov_valid) and legacy detail metrics ---
    const newMetrics = q.metrics || {};
    const legacyDetail = q._detail || {};
    const legacyFocus = legacyDetail.focus || {};
    const legacyIllum = legacyDetail.illumination || {};
    const legacyContrast = legacyDetail.contrast || {};
    const legacyFov = legacyDetail.field_of_view || {};

    // Sharpness (focus)
    const sharpnessVal = newMetrics.sharpness != null
      ? (newMetrics.sharpness * 100).toFixed(1)
      : (legacyFocus.value || 128.4);
    const sharpnessPass = newMetrics.sharpness != null ? newMetrics.sharpness >= 0.5 : legacyFocus.status === 'pass';
    const sharpnessThresh = legacyFocus.threshold ? `≥ ${legacyFocus.threshold}` : '≥ 0.50';

    // Brightness (illumination)
    const brightnessVal = newMetrics.brightness != null
      ? (newMetrics.brightness * 100).toFixed(1)
      : (legacyIllum.value || 114.2);
    const brightnessPass = newMetrics.brightness != null ? newMetrics.brightness > 0.1 && newMetrics.brightness < 1.0 : legacyIllum.status === 'pass';

    // Contrast
    const contrastVal = newMetrics.contrast != null
      ? (newMetrics.contrast * 100).toFixed(1)
      : (legacyContrast.value || 47.8);
    const contrastPass = newMetrics.contrast != null ? newMetrics.contrast >= 0.25 : legacyContrast.status === 'pass';

    // FOV
    const fovValid = newMetrics.fov_valid != null ? newMetrics.fov_valid : legacyFov.status === 'pass';
    const fovVal = legacyFov.value != null ? legacyFov.value : (fovValid ? 0.84 : 0.38);

    // Images from visuals (new) or legacy paths
    const visuals = caseData.visuals || {};
    const originalImg = visuals.original_image || App.currentCaseImage || '';
    const enhancedImg = visuals.enhanced_image || (caseData.enhancement && caseData.enhancement.enhanced_base64) || App.currentCaseImage || '';

    container.innerHTML = `
      <div class="header-actions" style="margin-bottom: 24px; justify-content: space-between; display: flex; align-items: flex-end;">
        <div>
          <h1 style="margin-bottom: 4px;">Image Quality Assessment (IQA)</h1>
          <p style="margin: 0; color: var(--neutral);">
            Case ID: <span class="code-font" style="font-weight: 600; color: var(--text-primary);">${caseData.id}</span> • Patient: ${caseData.patient_name} (${caseData.patient_id})
          </p>
        </div>
        <div style="display: flex; gap: 12px;">
          <button class="btn btn-secondary btn-md" onclick="App.navigateTo('screening')">New Image</button>
          <button class="btn btn-primary btn-md" id="btn-proceed-results">
            Proceed to AI Diagnostic View
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg>
          </button>
        </div>
      </div>

      ${recapture ? `
        <!-- Recapture Alert Banner -->
        <div class="card" style="border-left: 5px solid var(--error); background-color: var(--error-bg); margin-bottom: 24px;">
          <div style="display: flex; gap: 16px; align-items: flex-start;">
            <div style="color: var(--error); padding-top: 2px;">
              <svg width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
            </div>
            <div>
              <div style="font-size: 17px; font-weight: 700; color: var(--error-text); margin-bottom: 4px;">
                Image Rejected — Clinical Screening SLA Not Met
              </div>
              <div style="font-size: 14px; color: var(--error-text); line-height: 1.4; margin-bottom: 12px;">
                ${recaptureReason}
              </div>
              <div style="display: flex; gap: 12px;">
                <button class="btn btn-sm btn-destructive" onclick="App.navigateTo('screening')">
                  Recapture Immediately
                </button>
                <button class="btn btn-sm btn-secondary" id="btn-force-inspect">
                  Inspect Poor Image Anyway
                </button>
              </div>
            </div>
          </div>
        </div>
      ` : ''}

      <!-- Status & Gauges Grid -->
      <div class="grid-cols-4" style="margin-bottom: 24px;">
        <div class="card" style="margin-bottom: 0;">
          <div class="stat-label" style="margin-bottom: 8px;">Focus & Sharpness</div>
          <div style="display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 6px;">
            <span style="font-size: 24px; font-weight: 700; font-family: var(--font-code);">${sharpnessVal}</span>
            <span class="chip ${sharpnessPass ? 'chip-success' : 'chip-error'}">${sharpnessPass ? 'PASS' : 'FAIL'}</span>
          </div>
          <div style="font-size: 12px; color: var(--neutral);">Sharpness score (Threshold ${sharpnessThresh})</div>
        </div>

        <div class="card" style="margin-bottom: 0;">
          <div class="stat-label" style="margin-bottom: 8px;">Illumination / Brightness</div>
          <div style="display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 6px;">
            <span style="font-size: 24px; font-weight: 700; font-family: var(--font-code);">${brightnessVal}</span>
            <span class="chip ${brightnessPass ? 'chip-success' : 'chip-error'}">${brightnessPass ? 'PASS' : 'FAIL'}</span>
          </div>
          <div style="font-size: 12px; color: var(--neutral);">Brightness score (Optimal: 0.10 – 0.99)</div>
        </div>

        <div class="card" style="margin-bottom: 0;">
          <div class="stat-label" style="margin-bottom: 8px;">Contrast Ratio</div>
          <div style="display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 6px;">
            <span style="font-size: 24px; font-weight: 700; font-family: var(--font-code);">${contrastVal}</span>
            <span class="chip ${contrastPass ? 'chip-success' : 'chip-error'}">${contrastPass ? 'PASS' : 'FAIL'}</span>
          </div>
          <div style="font-size: 12px; color: var(--neutral);">RMS Contrast Index (Threshold ≥ 0.25)</div>
        </div>

        <div class="card" style="margin-bottom: 0;">
          <div class="stat-label" style="margin-bottom: 8px;">Field of View (FOV)</div>
          <div style="display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 6px;">
            <span style="font-size: 24px; font-weight: 700; font-family: var(--font-code);">${fovVal}</span>
            <span class="chip ${fovValid ? 'chip-success' : 'chip-error'}">${fovValid ? 'VALID' : 'INVALID'}</span>
          </div>
          <div style="font-size: 12px; color: var(--neutral);">Retinal disk coverage (≥ 0.45)</div>
        </div>
      </div>

      <!-- Image Preprocessing & Enhancement Stage -->
      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">Retinal Preprocessing & CLAHE Enhancement Pipeline</div>
            <div class="card-subtitle">Adaptive contrast equalization normalizes illumination across camera hardware models</div>
          </div>
          <div>${statusChip}${enhanced ? `<span class="chip chip-primary" style="font-size: 11px; margin-left: 8px;">ENHANCED</span>` : ''}</div>
        </div>

        <div class="viewer-container" style="margin-top: 12px;">
          <!-- Original Fundus Stage -->
          <div class="image-stage-box">
            <div style="font-size: 13px; font-weight: 600; color: #FFFFFF; margin-bottom: 8px;">Raw Input Camera Image</div>
            <div class="stage-canvas-wrap">
              ${originalImg ? `<img class="stage-img-base" id="quality-original-img" src="${originalImg}" alt="Raw Fundus">` : `<div style="display:flex;align-items:center;justify-content:center;height:240px;color:var(--neutral);font-size:13px;">No Raw Image Loaded</div>`}
            </div>
            <div style="font-size: 11px; color: var(--neutral); margin-top: 8px;">Raw 45° Posterior Pole Photograph</div>
          </div>

          <!-- Enhanced Preview Stage -->
          <div class="image-stage-box">
            <div style="font-size: 13px; font-weight: 600; color: #FFFFFF; margin-bottom: 8px;">
              CLAHE Normalized & Denoised View
              ${enhanced ? `<span class="chip chip-primary" style="font-size: 10px; margin-left: 6px;">Active</span>` : ''}
            </div>
            <div class="stage-canvas-wrap">
              ${enhancedImg ? `<img class="stage-img-base" id="quality-enhanced-img" src="${enhancedImg}" alt="Enhanced Fundus">` : `<div style="display:flex;align-items:center;justify-content:center;height:240px;color:var(--neutral);font-size:13px;">No Enhanced Image Generated</div>`}
            </div>
            <div style="font-size: 11px; color: var(--neutral); margin-top: 8px;">
              ${enhanced ? enhancementMethod : 'Tile-grid 8x8 • Clip limit 2.5 • Lab Color Space Luminance Transfer'}
            </div>
          </div>
        </div>
      </div>
    `;

    container.querySelector('#btn-proceed-results').addEventListener('click', () => {
      App.navigateTo('results');
    });

    const forceBtn = container.querySelector('#btn-force-inspect');
    if (forceBtn) {
      forceBtn.addEventListener('click', () => {
        App.navigateTo('results');
      });
    }
  }
};
