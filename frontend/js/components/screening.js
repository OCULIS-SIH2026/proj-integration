/**
 * frontend/js/components/screening.js - New Screening & Image Ingestion Component
 */

const ScreeningComponent = {
  selectedFile: null,
  selectedSampleId: null,
  selectedImageBase64: null,
  samples: [],

  render(container) {
    const autoId = `PAT-${Math.floor(1000 + Math.random() * 9000)}`;

    container.innerHTML = `
      <div class="header-actions" style="margin-bottom: 24px;">
        <div>
          <h1 style="margin-bottom: 4px;">Initiate New Retinal Screening</h1>
          <p style="margin: 0; color: var(--neutral);">Upload Fundus Camera Image or Select Clinical Validation Benchmark</p>
        </div>
      </div>

      <div class="grid-cols-2">
        <!-- Left Column: Patient Demographics & Upload -->
        <div>
          <!-- Patient Clinical Demographics Form -->
          <div class="card">
            <div class="card-title" style="margin-bottom: 16px;">1. Patient Demographics & History</div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
              <div class="form-group">
                <label class="form-label">Patient ID</label>
                <input type="text" id="input-patient-id" class="form-input code-font" value="${autoId}">
              </div>
              <div class="form-group">
                <label class="form-label">Patient Full Name</label>
                <input type="text" id="input-patient-name" class="form-input" value="Rukmini Devi">
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px;">
              <div class="form-group">
                <label class="form-label">Age (Years)</label>
                <input type="number" id="input-patient-age" class="form-input" value="58" min="18" max="100">
              </div>
              <div class="form-group">
                <label class="form-label">Gender</label>
                <select id="input-patient-gender" class="form-select">
                  <option value="Female" selected>Female</option>
                  <option value="Male">Male</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Examined Eye</label>
                <select id="input-patient-eye" class="form-select">
                  <option value="OD" selected>OD (Right Eye)</option>
                  <option value="OS">OS (Left Eye)</option>
                </select>
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label">Diabetes Duration (Years)</label>
                <input type="number" id="input-diabetes-duration" class="form-input" value="9" min="0" max="60">
              </div>
              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label">HbA1c Level (%)</label>
                <input type="number" id="input-hba1c" class="form-input" value="8.4" step="0.1" min="4" max="18">
              </div>
            </div>
          </div>

          <!-- Image Upload Dropzone -->
          <div class="card">
            <div class="card-title" style="margin-bottom: 12px;">2. Upload Fundus Camera Image</div>
            <div class="upload-dropzone" id="dropzone-area">
              <input type="file" id="file-input" accept="image/*" style="display: none;">
              <svg class="dropzone-icon" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
              </svg>
              <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">
                Drag and drop fundus photograph here
              </div>
              <div style="font-size: 13px; color: var(--neutral); margin-bottom: 14px;">
                Supports JPG, PNG, BMP (Standard macular & disc 45° field of view)
              </div>
              <button type="button" class="btn btn-sm btn-secondary" onclick="document.getElementById('file-input').click()">
                Browse Local Files
              </button>
            </div>

            <!-- Active Selected Image Preview Box -->
            <div id="selected-preview-box" style="display: none; margin-top: 16px; padding: 12px; background: var(--surface-raised); border-radius: 8px; align-items: center; justify-content: space-between;">
              <div style="display: flex; align-items: center; gap: 12px;">
                <img id="preview-thumb" style="width: 48px; height: 48px; border-radius: 6px; object-fit: cover;" src="" alt="Thumbnail">
                <div>
                  <div id="preview-filename" style="font-weight: 600; font-size: 14px; color: var(--text-primary);">image.jpg</div>
                  <div id="preview-meta" style="font-size: 12px; color: var(--neutral);">Ready for analysis</div>
                </div>
              </div>
              <button class="btn btn-sm btn-ghost" id="btn-clear-selection" style="color: var(--error);">Clear</button>
            </div>
          </div>
        </div>

        <!-- Right Column: Quick Benchmark Samples & Pipeline Trigger -->
        <div>
          <div class="card">
            <div class="card-header">
              <div>
                <div class="card-title">Or Choose a Clinical Benchmark Sample</div>
                <div class="card-subtitle">Instant test cases covering all 5 DR severity levels & image quality anomalies</div>
              </div>
            </div>

            <div id="samples-container" class="sample-grid" style="grid-template-columns: 1fr 1fr;">
              <div style="grid-column: 1 / -1; text-align: center; padding: 24px; color: var(--neutral);">
                Loading benchmark samples...
              </div>
            </div>

            <!-- Pipeline Action Box -->
            <div style="margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--border-subtle);">
              <div style="margin-bottom: 12px; font-size: 13px; color: var(--neutral); line-height: 1.4;">
                Clicking start executes the complete pipeline: <strong>Image Quality Assessment</strong> → <strong>CLAHE Enhancement</strong> (if needed) → <strong>EfficientNet-B0 DR Classification</strong> → <strong>Grad-CAM Heatmap</strong> → <strong>Triage Recommendation</strong>.
              </div>

              <button id="btn-start-screening" class="btn btn-primary btn-lg" style="width: 100%;">
                <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                Run AI Screening Pipeline
              </button>
            </div>
          </div>
        </div>
      </div>
    `;

    this.setupEvents(container);
    this.loadSamples(container);
  },

  setupEvents(container) {
    const dropzone = container.querySelector('#dropzone-area');
    const fileInput = container.querySelector('#file-input');
    const clearBtn = container.querySelector('#btn-clear-selection');
    const startBtn = container.querySelector('#btn-start-screening');

    // Drag & Drop
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        this.handleFileSelect(e.dataTransfer.files[0], container);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        this.handleFileSelect(e.target.files[0], container);
      }
    });

    clearBtn.addEventListener('click', () => {
      this.clearSelection(container);
    });

    startBtn.addEventListener('click', () => {
      this.runPipeline(container);
    });
  },

  async loadSamples(container) {
    try {
      const samples = await API.getSamples();
      this.samples = samples;
      const samplesGrid = container.querySelector('#samples-container');
      if (!samplesGrid) return;

      samplesGrid.innerHTML = samples.map(s => {
        const levelBadge = s.dr_level !== null
          ? `<span class="chip ${s.referable ? 'chip-error' : 'chip-success'}" style="font-size: 10px; padding: 1px 6px;">L${s.dr_level} ${s.referable ? 'Referable' : 'Non-ref'}</span>`
          : `<span class="chip chip-warning" style="font-size: 10px; padding: 1px 6px;">Quality Alert</span>`;

        return `
          <div class="sample-card" data-sample-id="${s.id}">
            <img class="sample-thumb" src="${s.image_data}" alt="${s.label}">
            <div style="flex: 1; overflow: hidden;">
              <div style="font-size: 13px; font-weight: 700; color: var(--text-primary); white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">
                ${s.label}
              </div>
              <div style="margin-top: 4px; display: flex; align-items: center; gap: 4px;">
                ${levelBadge}
              </div>
            </div>
          </div>
        `;
      }).join('');

      // Attach click to sample cards
      samplesGrid.querySelectorAll('.sample-card').forEach(card => {
        card.addEventListener('click', () => {
          samplesGrid.querySelectorAll('.sample-card').forEach(c => c.classList.remove('selected'));
          card.classList.add('selected');
          const sampleId = card.dataset.sampleId;
          this.handleSampleSelect(sampleId, container);
        });
      });

      // Default select Moderate NPDR (Level 2) sample for instant testing
      const defaultSample = samples.find(s => s.dr_level === 2);
      if (defaultSample) {
        const defaultCard = samplesGrid.querySelector(`[data-sample-id="${defaultSample.id}"]`);
        if (defaultCard) defaultCard.click();
      }

    } catch (err) {
      console.error('Failed to load samples:', err);
    }
  },

  handleSampleSelect(sampleId, container) {
    this.selectedSampleId = sampleId;
    this.selectedFile = null;
    const sample = this.samples.find(s => s.id === sampleId);
    if (!sample) return;

    this.selectedImageBase64 = sample.image_data;
    const previewBox = container.querySelector('#selected-preview-box');
    const thumb = container.querySelector('#preview-thumb');
    const filename = container.querySelector('#preview-filename');
    const meta = container.querySelector('#preview-meta');

    previewBox.style.display = 'flex';
    thumb.src = sample.image_data;
    filename.textContent = `${sample.label} (${sample.filename})`;
    meta.textContent = sample.description;
  },

  handleFileSelect(file, container) {
    this.selectedFile = file;
    this.selectedSampleId = null;

    // Deselect sample cards
    container.querySelectorAll('.sample-card').forEach(c => c.classList.remove('selected'));

    const reader = new FileReader();
    reader.onload = (e) => {
      this.selectedImageBase64 = e.target.result;
      const previewBox = container.querySelector('#selected-preview-box');
      const thumb = container.querySelector('#preview-thumb');
      const filename = container.querySelector('#preview-filename');
      const meta = container.querySelector('#preview-meta');

      previewBox.style.display = 'flex';
      thumb.src = e.target.result;
      filename.textContent = file.name;
      meta.textContent = `${(file.size / 1024).toFixed(1)} KB • Custom Fundus Photograph`;
    };
    reader.readAsDataURL(file);
  },

  clearSelection(container) {
    this.selectedFile = null;
    this.selectedSampleId = null;
    this.selectedImageBase64 = null;
    container.querySelector('#selected-preview-box').style.display = 'none';
    container.querySelectorAll('.sample-card').forEach(c => c.classList.remove('selected'));
  },

  async runPipeline(container) {
    if (!this.selectedFile && !this.selectedSampleId && !this.selectedImageBase64) {
      App.showToast('Please select a fundus image or a benchmark sample first.', 'warning');
      return;
    }

    const startBtn = container.querySelector('#btn-start-screening');
    const originalText = startBtn.innerHTML;
    startBtn.disabled = true;
    startBtn.innerHTML = `
      <svg class="animate-spin" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"/><path d="M12 2a10 10 0 0110 10"/></svg>
      Processing Image Pipeline...
    `;

    try {
      const selectedSample = this.samples ? this.samples.find(s => s.id === this.selectedSampleId) : null;
      const resolvedHint = selectedSample 
        ? `${selectedSample.id} ${selectedSample.label || ''} ${selectedSample.filename || ''}`
        : (this.selectedSampleId || (this.selectedFile ? this.selectedFile.name : ""));

      const patientMeta = {
        patient_id: container.querySelector('#input-patient-id')?.value?.trim() || 'PAT-NEW',
        patient_name: container.querySelector('#input-patient-name')?.value?.trim() || 'Walk-in Patient',
        patient_age: parseInt(container.querySelector('#input-patient-age')?.value) || 55,
        patient_gender: container.querySelector('#input-patient-gender')?.value || 'Female',
        diabetes_duration: parseInt(container.querySelector('#input-diabetes-duration')?.value) || 6,
        hba1c: parseFloat(container.querySelector('#input-hba1c')?.value) || 7.2,
        eye: container.querySelector('#input-patient-eye')?.value || 'OD',
        sample_hint: resolvedHint,
        filename: this.selectedFile ? this.selectedFile.name : (selectedSample ? selectedSample.filename : "")
      };

      if (selectedSample && selectedSample.dr_level != null) {
        patientMeta.target_level = selectedSample.dr_level;
      }

      let result;
      if (this.selectedFile) {
        const formData = new FormData();
        formData.append('file', this.selectedFile);
        formData.append('filename', this.selectedFile.name);
        formData.append('sample_hint', this.selectedFile.name);
        Object.entries(patientMeta).forEach(([k, v]) => {
          if (v !== undefined && v !== null) formData.append(k, v);
        });
        result = await API.screenImage(formData);
      } else {
        result = await API.screenImage({
          sample_id: this.selectedSampleId,
          image_base64: this.selectedImageBase64,
          patient_meta: patientMeta
        });
      }

      App.showToast('Screening completed successfully!', 'success');

      // Check if image quality triggered recapture
      const recaptureNeeded = result.recapture_needed || result.status === 'rejected' || (result.quality && result.quality.is_acceptable === false);
      App.currentScreeningCase = result;
      App.currentCaseImage = (result.visuals && result.visuals.original_image) || this.selectedImageBase64;

      if (recaptureNeeded) {
        App.navigateTo('quality');
      } else {
        App.navigateTo('results');
      }

    } catch (err) {
      console.error('Screening failed:', err);
      App.showToast(`Screening error: ${err.message}`, 'error');
    } finally {
      startBtn.disabled = false;
      startBtn.innerHTML = originalText;
    }
  }
};
