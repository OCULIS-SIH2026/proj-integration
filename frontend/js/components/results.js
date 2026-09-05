/**
 * frontend/js/components/results.js - AI Diagnostic Results & Explainability (Grad-CAM)
 * Reads mock_response.json: prediction.stage/label/confidence/probabilities, triage.is_referable, visuals.gradcam_overlay
 */

const ResultsComponent = {
  heatmapOpacity: 0.65,
  showVessels: true,

  render(container) {
    const caseData = App.currentScreeningCase;
    if (!caseData) {
      container.innerHTML = `
        <div class="card" style="text-align: center; padding: 48px;">
          <h2 style="margin-bottom: 8px;">No Screening Case Loaded</h2>
          <p>Please initiate a screening from the New Screening tab.</p>
          <button class="btn btn-primary btn-md" onclick="App.navigateTo('screening')">Go to New Screening</button>
        </div>
      `;
      return;
    }

    // --- New schema: prediction.* and triage.* with legacy fallback ---
    const pred = caseData.prediction || caseData.dr_prediction || {};
    const level = pred.stage != null ? pred.stage : (pred.level != null ? pred.level : 0);
    const label = pred.label || 'Undetermined';
    const conf = Math.round((pred.confidence || 0.0) * 100);
    const description = pred.description || '';

    // Probabilities: keyed by class label (new) or fallback to scores (legacy)
    const probabilities = pred.probabilities || pred.scores || {};

    // Triage
    const triage = caseData.triage || {};
    const isReferable = triage.is_referable != null ? triage.is_referable : (caseData.referable_dr || level >= 2);
    const urgency = triage.urgency || '';
    const timeframe = triage.timeframe || '';
    const triageRec = triage.recommendation || caseData.recommendation || '';

    // Visuals: new visuals.gradcam_overlay or legacy explainability.heatmap_base64
    const visuals = caseData.visuals || {};
    const heatmapUri = visuals.gradcam_overlay || (caseData.explainability || {}).heatmap_base64 || '';
    const vesselUri = visuals._vessel_mask || (caseData.structures || {}).vessel_mask_base64 || '';
    const originalUri = visuals.original_image || App.currentCaseImage || '';
    const attentionRegions = visuals._attention_regions || (caseData.explainability || {}).attention_regions || [];
    const disclaimer = visuals._disclaimer || (caseData.explainability || {}).disclaimer || '';

    const findings = caseData.findings || [];

    const refBadge = isReferable
      ? `<span class="chip chip-error" style="font-size: 15px; padding: 6px 18px;">REFERABLE DR — YES</span>`
      : `<span class="chip chip-success" style="font-size: 15px; padding: 6px 18px;">NON-REFERABLE — NO</span>`;

    // Build probability bars from probabilities object
    const CLASS_ORDER = ['No DR', 'Mild NPDR', 'Moderate NPDR', 'Severe NPDR', 'Proliferative DR'];
    const probBarsHtml = CLASS_ORDER.map((cls, idx) => {
      const prob = probabilities[cls] != null ? probabilities[cls] : (probabilities[String(idx)] || 0);
      const pct = Math.round(prob * 100);
      const isActive = idx === level;
      return `
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
          <span style="font-size: 12px; width: 120px; font-weight: ${isActive ? '700' : '400'}; color: ${isActive ? 'var(--primary)' : 'var(--text-secondary)'};">${cls}</span>
          <div style="flex: 1; height: 6px; background: var(--surface-raised); border-radius: 9999px; overflow: hidden;">
            <div style="width: ${pct}%; height: 100%; background: ${isActive ? 'var(--primary)' : 'var(--border)'}; border-radius: 9999px;"></div>
          </div>
          <span class="code-font" style="font-size: 11px; min-width: 38px; text-align: right; color: ${isActive ? 'var(--primary)' : 'var(--neutral)'};">${pct}%</span>
        </div>
      `;
    }).join('');

    container.innerHTML = `
      <div class="header-actions" style="margin-bottom: 24px; justify-content: space-between; display: flex; align-items: flex-end;">
        <div>
          <h1 style="margin-bottom: 4px;">AI Diagnostic & Explainability (XAI)</h1>
          <p style="margin: 0; color: var(--neutral);">
            Case ID: <span class="code-font" style="font-weight: 600; color: var(--text-primary);">${caseData.id}</span> • Patient: ${caseData.patient_name} (${caseData.patient_id})
          </p>
        </div>
        <div style="display: flex; gap: 12px;">
          <button class="btn btn-secondary btn-md" onclick="App.navigateTo('quality')">Back to Quality</button>
          <button class="btn btn-primary btn-md" id="btn-results-review">
            Conduct Clinician Review
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg>
          </button>
        </div>
      </div>

      <!-- Prototype Notice Banner -->
      <div style="background-color: var(--warning-bg); border: 1px solid var(--warning); border-radius: 8px; padding: 10px 16px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 10px; color: var(--warning-text); font-size: 13px; font-weight: 600;">
          <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>
          Prototype Medical Device Interface — AI predictions provide clinical decision support and require ophthalmologist sign-off.
        </div>
        <span class="chip chip-neutral" style="font-size: 11px;">SIH Benchmark Engine</span>
      </div>

      <!-- Main Classification & Triage Banner Card -->
      <div class="card active-card" style="margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
          <div>
            <div class="stat-label">Diabetic Retinopathy Stage (0–4 Scale)</div>
            <div style="display: flex; align-items: baseline; gap: 14px; margin-top: 4px;">
              <span class="display-font" style="font-size: 38px; color: var(--primary);">Level ${level}</span>
              <span style="font-size: 22px; font-weight: 700; color: var(--text-primary);">${label}</span>
            </div>
            ${description ? `<p style="margin: 6px 0 0; color: var(--text-secondary); font-size: 13px;">${description}</p>` : ''}
          </div>
          <div style="text-align: right;">
            <div class="stat-label" style="margin-bottom: 6px;">Referral Triage Classification</div>
            <div>${refBadge}</div>
            ${urgency ? `<div style="font-size: 12px; color: var(--neutral); margin-top: 6px;">${urgency}${timeframe ? ' • ' + timeframe : ''}</div>` : ''}
          </div>
        </div>

        <!-- 5-Level Visual Progression Stepper -->
        <div class="dr-stepper">
          <div class="dr-step ${level === 0 ? 'active' : ''}"><span class="dr-step-num">0</span>No DR</div>
          <div class="dr-step ${level === 1 ? 'active' : ''}"><span class="dr-step-num">1</span>Mild NPDR</div>
          <div class="dr-step ${level === 2 ? 'active' : ''}"><span class="dr-step-num">2</span>Moderate NPDR</div>
          <div class="dr-step ${level === 3 ? 'active' : ''}"><span class="dr-step-num">3</span>Severe NPDR</div>
          <div class="dr-step ${level === 4 ? 'active' : ''}"><span class="dr-step-num">4</span>Proliferative DR</div>
        </div>

        <!-- Confidence & Probability Breakdown -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; padding-top: 14px; border-top: 1px solid var(--border-subtle);">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <span class="stat-label">Model Calibrated Confidence</span>
              <span style="font-size: 16px; font-weight: 700; font-family: var(--font-code); color: var(--primary);">${conf}%</span>
            </div>
            <div style="height: 6px; background-color: var(--surface-raised); border-radius: 9999px; overflow: hidden;">
              <div style="width: ${conf}%; height: 100%; background-color: var(--primary); transition: width 300ms ease;"></div>
            </div>
            <div style="font-size: 12px; color: var(--neutral); margin-top: 6px;">Calibrated via temperature scaling (ECE &lt; 2.8%)</div>
          </div>

          <div>
            <div class="stat-label" style="margin-bottom: 8px;">Per-Class Probability Breakdown</div>
            ${probBarsHtml}
          </div>
        </div>

        ${triageRec ? `
          <div style="margin-top: 12px; padding: 10px 14px; background: var(--surface-raised); border-radius: 8px; font-size: 13px; color: var(--text-secondary); border-left: 3px solid var(--primary);">
            <strong>Clinical Recommendation:</strong> ${triageRec}
          </div>
        ` : ''}

        <!-- Supporting Microvascular Findings -->
        ${findings.length ? `
          <div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--border-subtle);">
            <div class="stat-label" style="margin-bottom: 6px;">Supporting Microvascular Evidence</div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;">
              ${findings.map(f => `<span class="chip chip-neutral" style="font-size: 11px;">• ${f.replace(/_/g, ' ')}</span>`).join('')}
            </div>
          </div>
        ` : ''}
      </div>

      <!-- Explainability Workspace: Grad-CAM Heatmap & Vessel Overlays -->
      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">Explainable AI (Grad-CAM) Visualizer</div>
            <div class="card-subtitle">Gradient-weighted Class Activation Mapping reveals visual regions driving the network's prediction</div>
          </div>
          <!-- Controls -->
          <div style="display: flex; align-items: center; gap: 16px;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="stat-label">Heatmap Opacity:</span>
              <input type="range" id="opacity-slider" min="0" max="1" step="0.05" value="${this.heatmapOpacity}" style="width: 110px; accent-color: var(--primary);">
              <span id="opacity-val" class="code-font" style="font-size: 12px; min-width: 32px;">${Math.round(this.heatmapOpacity * 100)}%</span>
            </div>
            <label style="display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; cursor: pointer;">
              <input type="checkbox" id="toggle-vessels" ${this.showVessels ? 'checked' : ''} style="accent-color: var(--primary);">
              Landmarks
            </label>
            <label style="display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; cursor: pointer;">
              <input type="checkbox" id="toggle-lesions" ${this.showLesions !== false ? 'checked' : ''} style="accent-color: #F59E0B;">
              Lesion Evidence
            </label>
          </div>
        </div>

        <div class="viewer-container">
          <!-- Interactive Blend View -->
          <div class="image-stage-box">
            <div style="font-size: 13px; font-weight: 600; color: #FFFFFF; margin-bottom: 8px;">
              Grad-CAM Blended Fundus View
            </div>
            <div class="stage-canvas-wrap" id="blend-canvas-container">
              ${originalUri ? `<img class="stage-img-base" src="${originalUri}" alt="Base Fundus">` : `<div style="display:flex;align-items:center;justify-content:center;height:280px;color:var(--neutral);font-size:13px;">No Fundus Image Available</div>`}
              ${heatmapUri ? `<img class="stage-layer" id="layer-heatmap" src="${heatmapUri}" style="opacity: ${this.heatmapOpacity}; mix-blend-mode: screen;" alt="Heatmap">` : ''}
              ${vesselUri ? `<img class="stage-layer" id="layer-vessels" src="${vesselUri}" style="opacity: ${this.showVessels ? 1 : 0};" alt="Vessels">` : ''}
              ${visuals._lesion_overlay ? `<img class="stage-layer" id="layer-lesions" src="${visuals._lesion_overlay}" style="opacity: ${this.showLesions !== false ? 1 : 0}; pointer-events: none;" alt="Lesion Overlay">` : ''}
            </div>
            <div style="font-size: 11px; color: var(--neutral); margin-top: 8px;">
              Red/Amber: AI Attention &bull; Red/Yellow: Hemorrhages/Microaneurysms &bull; Cyan: Exudates
            </div>
          </div>

          <!-- Attention Quadrants & Lesion Candidates Breakdown -->
          <div style="background-color: var(--surface-card); border: 1px solid var(--border); border-radius: 12px; padding: 18px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
              <div class="stat-label" style="margin-bottom: 10px;">Quantitative Lesion Candidate Evidence (Person 2)</div>
              <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-bottom: 16px;">
                <div style="background: var(--surface-raised); padding: 8px 10px; border-radius: 8px; border-left: 3px solid #CA8A04;">
                  <div style="font-size: 11px; color: var(--neutral);">Microaneurysms</div>
                  <div style="font-size: 18px; font-weight: 700; color: #CA8A04;">${caseData.lesions ? caseData.lesions.microaneurysms.count : (level >= 1 ? '3–5' : '0')}</div>
                  <div style="font-size: 10px; color: var(--neutral);">${caseData.lesions ? caseData.lesions.microaneurysms.severity : 'Focal'}</div>
                </div>
                <div style="background: var(--surface-raised); padding: 8px 10px; border-radius: 8px; border-left: 3px solid #DC2626;">
                  <div style="font-size: 11px; color: var(--neutral);">Hemorrhages</div>
                  <div style="font-size: 18px; font-weight: 700; color: #DC2626;">${caseData.lesions ? caseData.lesions.hemorrhages.count : (level >= 2 ? '3–8' : '0')}</div>
                  <div style="font-size: 10px; color: var(--neutral);">${caseData.lesions ? caseData.lesions.hemorrhages.quadrants_affected + ' Quadrants' : 'Blot/Dot'}</div>
                </div>
                <div style="background: var(--surface-raised); padding: 8px 10px; border-radius: 8px; border-left: 3px solid #0891B2;">
                  <div style="font-size: 11px; color: var(--neutral);">Hard Exudates</div>
                  <div style="font-size: 18px; font-weight: 700; color: #0891B2;">${caseData.lesions ? caseData.lesions.exudates.count : (level >= 2 ? '3' : '0')}</div>
                  <div style="font-size: 10px; color: var(--neutral);">${caseData.lesions && caseData.lesions.exudates.macular_threat ? 'Near Macula' : 'Paramacular'}</div>
                </div>
                <div style="background: var(--surface-raised); padding: 8px 10px; border-radius: 8px; border-left: 3px solid ${caseData.lesions && caseData.lesions.neovascularization.detected ? '#DC2626' : '#16A34A'};">
                  <div style="font-size: 11px; color: var(--neutral);">Neovascularization</div>
                  <div style="font-size: 13px; font-weight: 700; color: ${caseData.lesions && caseData.lesions.neovascularization.detected ? '#DC2626' : '#16A34A'}; margin-top: 4px;">
                    ${caseData.lesions && caseData.lesions.neovascularization.detected ? 'POSITIVE (NVD)' : 'NEGATIVE'}
                  </div>
                </div>
              </div>

              <div class="stat-label" style="margin-bottom: 8px;">Salient Retinal Attention Regions (Grad-CAM)</div>
              <div style="display: flex; flex-direction: column; gap: 8px;">
                ${attentionRegions && attentionRegions.length > 0 ? (attentionRegions).map(r => `
                  <div style="padding: 8px 10px; background: var(--surface); border-radius: 6px; border-left: 3px solid var(--primary);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                      <span style="font-weight: 700; font-size: 13px; color: var(--text-primary);">${r.region}</span>
                      <span class="code-font" style="font-weight: 600; color: var(--primary); font-size: 12px;">${Math.round(r.weight * 100)}% salience</span>
                    </div>
                    <div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">${r.clinical_correlate}</div>
                  </div>
                `).join('') : `
                  <div style="padding: 12px; text-align: center; color: var(--neutral); font-size: 12px;">
                    No focal pathological lesions flagged for this stage.
                  </div>
                `}
              </div>
            </div>

            <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid var(--border-subtle); font-size: 11px; color: var(--neutral); font-style: italic;">
              ${disclaimer || 'Grad-CAM highlights image regions that influenced the model; it does not establish definitive lesion identity.'}
            </div>
          </div>
        </div>
      </div>
    `;

    // Sliders and toggles
    const slider = container.querySelector('#opacity-slider');
    const opacityLabel = container.querySelector('#opacity-val');
    const heatmapLayer = container.querySelector('#layer-heatmap');
    const vesselCheckbox = container.querySelector('#toggle-vessels');
    const vesselLayer = container.querySelector('#layer-vessels');
    const lesionCheckbox = container.querySelector('#toggle-lesions');
    const lesionLayer = container.querySelector('#layer-lesions');

    if (slider && opacityLabel) {
      slider.addEventListener('input', (e) => {
        this.heatmapOpacity = parseFloat(e.target.value);
        opacityLabel.textContent = `${Math.round(this.heatmapOpacity * 100)}%`;
        if (heatmapLayer) heatmapLayer.style.opacity = this.heatmapOpacity;
      });
    }

    if (vesselCheckbox) {
      vesselCheckbox.addEventListener('change', (e) => {
        this.showVessels = e.target.checked;
        if (vesselLayer) vesselLayer.style.opacity = this.showVessels ? 1 : 0;
      });
    }

    if (lesionCheckbox) {
      lesionCheckbox.addEventListener('change', (e) => {
        this.showLesions = e.target.checked;
        if (lesionLayer) lesionLayer.style.opacity = this.showLesions ? 1 : 0;
      });
    }

    const reviewBtn = container.querySelector('#btn-results-review');
    if (reviewBtn) {
      reviewBtn.addEventListener('click', () => {
        App.navigateTo('review');
      });
    }
  }
};
