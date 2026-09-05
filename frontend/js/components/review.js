/**
 * frontend/js/components/review.js - Ophthalmologist Human-in-the-Loop Review Station (<30s Target)
 */

const ReviewComponent = {
  currentDecision: 'accept',
  overrideLevel: 2,
  referralRoute: 'Urgent referral to ophthalmologist within 2 weeks',

  render(container) {
    const caseData = App.currentScreeningCase;
    if (!caseData) {
      container.innerHTML = `
        <div class="card" style="text-align: center; padding: 48px;">
          <h2 style="margin-bottom: 8px;">No Active Screening Case</h2>
          <p>Please select a case from the Dashboard or initiate a new screening.</p>
          <button class="btn btn-primary btn-md" onclick="App.navigateTo('dashboard')">Go to Dashboard</button>
        </div>
      `;
      return;
    }

    const pred = caseData.prediction || caseData.dr_prediction || {};
    const aiLevel = pred.stage != null ? pred.stage : (pred.level != null ? pred.level : 0);
    const aiLabel = pred.label || 'No DR';
    const conf = Math.round((pred.confidence || 0.0) * 100);
    const triage = caseData.triage || {};
    const isReferable = triage.is_referable != null ? triage.is_referable : caseData.referable_dr;

    container.innerHTML = `
      <div class="header-actions" style="margin-bottom: 24px; justify-content: space-between; display: flex; align-items: flex-end;">
        <div>
          <h1 style="margin-bottom: 4px;">Ophthalmologist Validation Station</h1>
          <p style="margin: 0; color: var(--neutral);">
            Human-in-the-Loop Verification • Target SLA: &lt; 30 Seconds • Case: <span class="code-font" style="font-weight: 600; color: var(--text-primary);">${caseData.id}</span>
          </p>
        </div>
        <div style="display: flex; gap: 12px;">
          <button class="btn btn-secondary btn-md" onclick="App.navigateTo('results')">Back to AI Results</button>
        </div>
      </div>

      <div class="grid-cols-2">
        <!-- Left Column: Case Summary & Telemetry -->
        <div>
          <div class="card">
            <div class="card-title" style="margin-bottom: 12px;">AI Pre-Screening Telemetry</div>
            
            <div style="background: var(--surface-raised); padding: 14px; border-radius: 8px; margin-bottom: 16px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span class="stat-label">AI Stage Prediction:</span>
                <span style="font-size: 16px; font-weight: 700; color: var(--primary);">Level ${aiLevel} — ${aiLabel}</span>
              </div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span class="stat-label">Model Confidence:</span>
                <span class="code-font" style="font-weight: 600;">${conf}%</span>
              </div>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="stat-label">Triage Requirement:</span>
                <span class="chip ${isReferable ? 'chip-error' : 'chip-success'}" style="font-size: 11px;">
                  ${isReferable ? 'REFERABLE' : 'NON-REFERABLE'}
                </span>
              </div>
            </div>

            <!-- Thumbnail inspection -->
            <div style="display: flex; gap: 12px; align-items: center;">
              ${(caseData.visuals && caseData.visuals.original_image) || App.currentCaseImage ? `
                <img src="${(caseData.visuals && caseData.visuals.original_image) || App.currentCaseImage}" style="width: 110px; height: 110px; border-radius: 8px; object-fit: cover; background: #000;" alt="Fundus">
              ` : `
                <div style="width: 110px; height: 110px; border-radius: 8px; background: var(--surface); display: flex; align-items: center; justify-content: center; font-size: 11px; color: var(--neutral); text-align: center; padding: 4px;">
                  No Preview
                </div>
              `}
              <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.4;">
                <strong>Patient:</strong> ${caseData.patient_name} (${caseData.patient_id})<br>
                <strong>Age/Gender:</strong> ${caseData.patient_age}y / ${caseData.patient_gender}<br>
                <strong>Eye:</strong> ${caseData.eye === 'OD' ? 'Right Eye (OD)' : 'Left Eye (OS)'}<br>
                <strong>Duration / HbA1c:</strong> ${caseData.diabetes_duration}y / ${caseData.hba1c}%
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Doctor Review Actions -->
        <div>
          <div class="card active-card">
            <div class="card-title" style="margin-bottom: 16px;">Clinician Diagnostic Sign-off</div>

            <!-- Decision Toggle (Accept vs Override) -->
            <div style="margin-bottom: 18px;">
              <label class="form-label">Clinical Diagnostic Decision</label>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <button type="button" id="btn-decision-accept" class="btn btn-md btn-primary" style="width: 100%;">
                  ✓ Accept AI (Level ${aiLevel})
                </button>
                <button type="button" id="btn-decision-override" class="btn btn-md btn-secondary" style="width: 100%;">
                  ✎ Override Diagnosis
                </button>
              </div>
            </div>

            <!-- Override Level Selector (hidden by default unless override is clicked) -->
            <div id="override-section" style="display: none; background: var(--surface-raised); padding: 14px; border-radius: 8px; margin-bottom: 18px;">
              <label class="form-label">Select Overridden DR Severity Level</label>
              <div style="display: flex; gap: 8px;">
                ${[0, 1, 2, 3, 4].map(lvl => `
                  <button type="button" class="btn btn-sm btn-secondary override-level-btn ${lvl === this.overrideLevel ? 'active btn-primary' : ''}" data-lvl="${lvl}" style="flex: 1;">
                    L${lvl}
                  </button>
                `).join('')}
              </div>
            </div>

            <!-- Referral Action Route -->
            <div class="form-group">
              <label class="form-label">Clinical Referral & Follow-up Action</label>
              <select id="select-referral-route" class="form-select">
                <option value="Routine annual screening (12 months)">Routine annual screening (12 months)</option>
                <option value="Intermediate follow-up within 6 months">Intermediate follow-up within 6 months</option>
                <option value="Urgent referral to ophthalmologist within 2 weeks" selected>Urgent referral to ophthalmologist within 2 weeks</option>
                <option value="Emergency vitreoretinal referral within 48-72 hours">Emergency vitreoretinal referral within 48-72 hours</option>
              </select>
            </div>

            <!-- Quick Note Chips -->
            <div style="margin-bottom: 12px;">
              <label class="form-label">Quick Clinical Note Snippets</label>
              <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                <button type="button" class="btn btn-sm btn-secondary note-chip" data-text="Fundus findings concordant with AI telemetry.">Concordant Findings</button>
                <button type="button" class="btn btn-sm btn-secondary note-chip" data-text="Blot hemorrhages confirmed in superior temporal arcade.">Blot Hemorrhages</button>
                <button type="button" class="btn btn-sm btn-secondary note-chip" data-text="Hard exudates encroaching foveal avascular zone.">Macular Exudates</button>
                <button type="button" class="btn btn-sm btn-secondary note-chip" data-text="Neovascularization fronds identified near optic disc.">Neovascularization</button>
              </div>
            </div>

            <!-- Notes Textarea -->
            <div class="form-group">
              <label class="form-label">Doctor Clinical Notes</label>
              <textarea id="doctor-notes-input" class="form-textarea" rows="3" placeholder="Enter clinical remarks or choose a snippet above...">Clinical examination findings concordant with screening telemetry.</textarea>
            </div>

            <!-- Clinician Name / Signature -->
            <div class="form-group">
              <label class="form-label">Validating Clinician Signature</label>
              <input type="text" id="doctor-name-input" class="form-input" value="Dr. S. Ramanathan, MD (Ophthalmology)">
            </div>

            <!-- Submit Final Review Button -->
            <button id="btn-submit-review" class="btn btn-primary btn-lg" style="width: 100%;">
              <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M5 13l4 4L19 7"/></svg>
              Finalize & Generate Clinical Screening Report
            </button>
          </div>
        </div>
      </div>
    `;

    this.setupEvents(container, caseData, aiLevel);
  },

  setupEvents(container, caseData, aiLevel) {
    const btnAccept = container.querySelector('#btn-decision-accept');
    const btnOverride = container.querySelector('#btn-decision-override');
    const overrideSec = container.querySelector('#override-section');
    const notesInput = container.querySelector('#doctor-notes-input');
    const submitBtn = container.querySelector('#btn-submit-review');

    btnAccept.addEventListener('click', () => {
      this.currentDecision = 'accept';
      btnAccept.className = 'btn btn-md btn-primary';
      btnOverride.className = 'btn btn-md btn-secondary';
      overrideSec.style.display = 'none';
    });

    btnOverride.addEventListener('click', () => {
      this.currentDecision = 'override';
      btnOverride.className = 'btn btn-md btn-primary';
      btnAccept.className = 'btn btn-md btn-secondary';
      overrideSec.style.display = 'block';
    });

    // Override level buttons
    container.querySelectorAll('.override-level-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        container.querySelectorAll('.override-level-btn').forEach(b => b.classList.remove('active', 'btn-primary'));
        btn.classList.add('active', 'btn-primary');
        this.overrideLevel = parseInt(btn.dataset.lvl);
      });
    });

    // Quick note snippets
    container.querySelectorAll('.note-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const text = chip.dataset.text;
        if (notesInput.value && !notesInput.value.includes(text)) {
          notesInput.value = `${notesInput.value} ${text}`;
        } else {
          notesInput.value = text;
        }
      });
    });

    // Submit review
    submitBtn.addEventListener('click', async () => {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Saving & Finalizing...';

      try {
        const reviewData = {
          screening_id: caseData.id,
          doctor_status: this.currentDecision === 'accept' ? 'accepted' : 'overridden',
          doctor_dr_level: this.currentDecision === 'accept' ? aiLevel : this.overrideLevel,
          doctor_referral_action: container.querySelector('#select-referral-route').value,
          doctor_notes: notesInput.value,
          doctor_name: container.querySelector('#doctor-name-input').value
        };

        const resp = await API.submitDoctorReview(reviewData);
        App.currentScreeningCase = resp.screening || caseData;
        App.showToast('Clinical review signed and recorded!', 'success');
        App.navigateTo('report');
      } catch (err) {
        console.error('Failed to submit review:', err);
        App.showToast(`Review error: ${err.message}`, 'error');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Finalize & Generate Report';
      }
    });
  }
};
