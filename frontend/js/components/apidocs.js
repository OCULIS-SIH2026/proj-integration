/**
 * frontend/js/components/apidocs.js - Interactive Clinical REST API Documentation
 * Conforms to OpenAPI 3.1 & HL7 FHIR Interoperability Guidelines
 */

const ApiDocsComponent = {
  activeSnippetTab: {},

  render(container) {
    const origin = window.location.origin || 'http://localhost:8000';

    container.innerHTML = `
      <div class="api-hero">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 20px; flex-wrap: wrap;">
          <div>
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
              <span class="chip chip-primary" style="font-family: var(--font-code); font-weight: 700;">REST API v2.4</span>
              <span class="chip chip-success">Production Endpoint Active</span>
              <span class="chip chip-neutral">IEC 62304 / DICOM PS 3.16</span>
            </div>
            <h1 style="margin-bottom: 6px;">Clinical Tele-Ophthalmology API Documentation</h1>
            <p style="margin: 0; max-width: 820px; color: var(--text-secondary);">
              Programmatic interface for fundus photography ingestion, deep learning DR classification (0–4), 
              optical quality assurance, Explainable AI (Grad-CAM saliency heatmaps), clinician review validation, 
              and rural telemedicine queuing simulation.
            </p>
          </div>
          <div style="text-align: right; background: var(--surface); padding: 12px 18px; border-radius: 10px; border: 1px solid var(--border);">
            <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--neutral); margin-bottom: 4px;">Host Base URL</div>
            <div class="code-font" style="font-weight: 600; color: var(--primary); font-size: 14px;" id="api-base-url">${origin}</div>
          </div>
        </div>

        <!-- Diagnostic Engine Specification Banner -->
        <div style="margin-top: 18px; padding: 10px 14px; background: var(--surface-raised); border-radius: 8px; border: 1px solid var(--border-subtle); display: flex; align-items: center; gap: 10px; font-size: 13px; color: var(--text-secondary); flex-wrap: wrap;">
          <span class="chip chip-primary" style="font-size: 11px; padding: 2px 8px; font-weight: 700;">SPEC</span>
          <span style="font-weight: 600; color: var(--text-primary); font-family: var(--font-code); font-size: 12.5px;">OculisAI Diagnostic Engine v2.4 • EfficientNet-B0 (DR 0–4) • Grad-CAM XAI • CDSCO Compliant</span>
        </div>

        <div style="display: flex; gap: 24px; margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--border-subtle); flex-wrap: wrap;">
          <div>
            <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--neutral);">Auth Format</span>
            <div style="font-size: 13px; font-weight: 600; color: var(--text-primary);">Bearer &lt;JWT&gt; / Session</div>
          </div>
          <div>
            <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--neutral);">Data Standards</span>
            <div style="font-size: 13px; font-weight: 600; color: var(--text-primary);">HL7 FHIR &amp; DICOM</div>
          </div>
          <div>
            <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--neutral);">Media Types</span>
            <div style="font-size: 13px; font-weight: 600; color: var(--text-primary);">multipart/form-data, application/json</div>
          </div>
          <div>
            <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--neutral);">Avg AI Latency</span>
            <div style="font-size: 13px; font-weight: 600; color: var(--success);">&lt; 350 ms</div>
          </div>
        </div>
      </div>

      <!-- Endpoints Explorer Section -->
      <div style="margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
        <h2 style="font-size: 20px; margin: 0;">API Endpoint Directory</h2>
        <span style="font-size: 12px; color: var(--neutral);">8 Endpoints Available</span>
      </div>

      <!-- Endpoint 1: POST /api/screen -->
      ${this.renderEndpointCard({
        id: 'endpoint-screen',
        method: 'POST',
        path: '/api/screen',
        title: 'Run AI Retinal Screening Pipeline',
        description: 'Uploads a retinal fundus image and executes automated optical quality assessment, EfficientNet-B0 DR grading (0–4), blood vessel segmentation, and Grad-CAM explainability heatmaps.',
        params: [
          { name: 'file', type: 'binary', in: 'formData', required: 'Conditional', desc: 'Retinal fundus image (JPG, PNG, BMP). Required if not sending sample_id.' },
          { name: 'sample_id', type: 'string', in: 'body (JSON)', required: 'Conditional', desc: 'Benchmark sample ID (e.g., sample-001, sample-002).' },
          { name: 'patient_id', type: 'string', in: 'formData / JSON', required: 'No', desc: 'Medical Record Number / Patient Identifier (default: PAT-NEW).' },
          { name: 'patient_name', type: 'string', in: 'formData / JSON', required: 'No', desc: 'Full clinical name of the patient.' },
          { name: 'patient_age', type: 'integer', in: 'formData / JSON', required: 'No', desc: 'Patient age in years.' },
          { name: 'patient_gender', type: 'string', in: 'formData / JSON', required: 'No', desc: 'Gender (Female, Male, Other).' },
          { name: 'eye', type: 'string', in: 'formData / JSON', required: 'No', desc: 'OD (Right eye) or OS (Left eye).' }
        ],
        curlSnippet: `curl -X POST "${origin}/api/screen" \\
  -H "Content-Type: application/json" \\
  -d '{
    "sample_id": "sample-002",
    "patient_meta": {
      "patient_id": "PAT-4821",
      "patient_name": "Rukmini Devi",
      "patient_age": 58,
      "patient_gender": "Female",
      "eye": "OD"
    }
  }'`,
        jsSnippet: `const response = await fetch('${origin}/api/screen', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    sample_id: 'sample-002',
    patient_meta: {
      patient_id: 'PAT-4821',
      patient_name: 'Rukmini Devi',
      patient_age: 58,
      patient_gender: 'Female',
      eye: 'OD'
    }
  })
});
const data = await response.json();
console.log('DR Stage:', data.prediction.stage, data.prediction.label);`,
        pythonSnippet: `import requests

url = "${origin}/api/screen"
payload = {
    "sample_id": "sample-002",
    "patient_meta": {
        "patient_id": "PAT-4821",
        "patient_name": "Rukmini Devi",
        "patient_age": 58,
        "patient_gender": "Female",
        "eye": "OD"
    }
}
response = requests.post(url, json=payload)
result = response.json()
print("Prediction:", result["prediction"]["label"], f"(Stage {result['prediction']['stage']})")`,
        defaultTestPayload: JSON.stringify({
          sample_id: "sample-002",
          patient_meta: {
            patient_id: "PAT-4821",
            patient_name: "Rukmini Devi",
            patient_age: 58,
            patient_gender: "Female",
            eye: "OD"
          }
        }, null, 2)
      })}

      <!-- Endpoint 2: GET /api/screenings -->
      ${this.renderEndpointCard({
        id: 'endpoint-screenings-list',
        method: 'GET',
        path: '/api/screenings',
        title: 'List All Screenings & Dashboard KPIs',
        description: 'Retrieves active patient screening records and real-time aggregated triage telemetry (total cases, referable rate, review queue depth, review turnaround times).',
        params: [
          { name: 'limit', type: 'integer', in: 'query', required: 'No', desc: 'Maximum number of records to return (default: 50).' }
        ],
        curlSnippet: `curl -X GET "${origin}/api/screenings"`,
        jsSnippet: `const res = await fetch('${origin}/api/screenings');
const { stats, screenings } = await res.json();
console.log('Total Screenings:', stats.total_screenings);`,
        pythonSnippet: `import requests
res = requests.get("${origin}/api/screenings")
data = res.json()
print("Stats:", data["stats"])`,
        defaultTestPayload: ''
      })}

      <!-- Endpoint 3: GET /api/screenings/{id} -->
      ${this.renderEndpointCard({
        id: 'endpoint-screening-detail',
        method: 'GET',
        path: '/api/screenings/{id}',
        title: 'Get Single Screening Case Detail',
        description: 'Fetches the comprehensive medical dossier of a screening case, including full feature vectors, Grad-CAM heatmap base64, vessel mask, and doctor sign-off history.',
        params: [
          { name: 'id', type: 'string', in: 'path', required: 'Yes', desc: 'Unique screening case identifier (e.g., SCR-9001, SCR-9002).' }
        ],
        curlSnippet: `curl -X GET "${origin}/api/screenings/SCR-9001"`,
        jsSnippet: `const res = await fetch('${origin}/api/screenings/SCR-9001');
const caseDetail = await res.json();
console.log('Case Detail:', caseDetail);`,
        pythonSnippet: `import requests
res = requests.get("${origin}/api/screenings/SCR-9001")
print(res.json())`,
        defaultTestPayload: '',
        pathParamName: 'id',
        defaultPathParam: 'SCR-9001'
      })}

      <!-- Endpoint 4: POST /api/review -->
      ${this.renderEndpointCard({
        id: 'endpoint-doctor-review',
        method: 'POST',
        path: '/api/review',
        title: 'Submit Doctor Review & Clinical Sign-off',
        description: 'Records human-in-the-loop ophthalmologist validation, confirmed DR stage, treatment plan, referral facility, and clinical prescription.',
        params: [
          { name: 'screening_id', type: 'string', in: 'body (JSON)', required: 'Yes', desc: 'Target screening record ID.' },
          { name: 'decision', type: 'string', in: 'body (JSON)', required: 'Yes', desc: 'Doctor decision: agree, disagree, or escalate.' },
          { name: 'confirmed_dr_level', type: 'integer', in: 'body (JSON)', required: 'Yes', desc: 'Confirmed Diabetic Retinopathy grade (0 to 4).' },
          { name: 'clinical_notes', type: 'string', in: 'body (JSON)', required: 'No', desc: 'Doctor observations and clinical recommendations.' },
          { name: 'doctor_name', type: 'string', in: 'body (JSON)', required: 'No', desc: 'Validating clinician name.' }
        ],
        curlSnippet: `curl -X POST "${origin}/api/review" \\
  -H "Content-Type: application/json" \\
  -d '{
    "screening_id": "SCR-9001",
    "decision": "agree",
    "confirmed_dr_level": 2,
    "clinical_notes": "Moderate NPDR confirmed. Scattered microaneurysms. Refer to retina specialist within 30 days.",
    "doctor_name": "Dr. S. Ramanathan, MD"
  }'`,
        jsSnippet: `const res = await fetch('${origin}/api/review', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    screening_id: 'SCR-9001',
    decision: 'agree',
    confirmed_dr_level: 2,
    clinical_notes: 'Moderate NPDR confirmed.',
    doctor_name: 'Dr. S. Ramanathan, MD'
  })
});
const result = await res.json();
console.log('Review Result:', result);`,
        pythonSnippet: `import requests
res = requests.post("${origin}/api/review", json={
    "screening_id": "SCR-9001",
    "decision": "agree",
    "confirmed_dr_level": 2,
    "clinical_notes": "Moderate NPDR confirmed."
})
print(res.json())`,
        defaultTestPayload: JSON.stringify({
          screening_id: "SCR-9001",
          decision: "agree",
          confirmed_dr_level: 2,
          clinical_notes: "Moderate NPDR verified by remote clinician.",
          doctor_name: "Dr. S. Ramanathan, MD"
        }, null, 2)
      })}

      <!-- Endpoint 5: GET /api/report/{id} -->
      ${this.renderEndpointCard({
        id: 'endpoint-report',
        method: 'GET',
        path: '/api/report/{id}',
        title: 'Generate Print-Ready Clinical Report HTML',
        description: 'Generates an official clinical tele-ophthalmology diagnostic report formatted with ICD-10 codification, explainability heatmaps, patient demographics, and doctor sign-off blocks.',
        params: [
          { name: 'id', type: 'string', in: 'path', required: 'Yes', desc: 'Screening case ID to render (e.g., SCR-9001).' }
        ],
        curlSnippet: `curl -X GET "${origin}/api/report/SCR-9001"`,
        jsSnippet: `const res = await fetch('${origin}/api/report/SCR-9001');
const htmlReport = await res.text();
console.log('Report HTML Length:', htmlReport.length);`,
        pythonSnippet: `import requests
res = requests.get("${origin}/api/report/SCR-9001")
with open("report.html", "w") as f:
    f.write(res.text)`,
        defaultTestPayload: '',
        pathParamName: 'id',
        defaultPathParam: 'SCR-9001'
      })}

      <!-- Endpoint 6: POST /api/simulate -->
      ${this.renderEndpointCard({
        id: 'endpoint-simulate',
        method: 'POST',
        path: '/api/simulate',
        title: 'Run Telemedicine Queuing Simulation',
        description: 'Simulates the rural primary health center tele-ophthalmology network under specified volume (100,000 to 200,000+ patients/year). Returns queuing telemetry, doctor utilization, and bottleneck analysis.',
        params: [
          { name: 'scenario', type: 'string', in: 'body (JSON)', required: 'No', desc: 'Preset scenario identifier: scenario_a, scenario_b, scenario_c, scenario_d.' },
          { name: 'overrides', type: 'object', in: 'body (JSON)', required: 'No', desc: 'Custom simulation parameters: annual_patients, num_doctors, ai_latency_sec, doctor_review_time_sec.' }
        ],
        curlSnippet: `curl -X POST "${origin}/api/simulate" \\
  -H "Content-Type: application/json" \\
  -d '{
    "scenario": "scenario_a"
  }'`,
        jsSnippet: `const res = await fetch('${origin}/api/simulate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ scenario: 'scenario_a' })
});
const simResult = await res.json();
console.log('Doctor Utilization:', simResult.results.doctor_utilization_pct);`,
        pythonSnippet: `import requests
res = requests.post("${origin}/api/simulate", json={"scenario": "scenario_a"})
print(res.json()["results"])`,
        defaultTestPayload: JSON.stringify({
          scenario: "scenario_a"
        }, null, 2)
      })}

      <!-- Endpoint 7: GET /api/simulate/comparison -->
      ${this.renderEndpointCard({
        id: 'endpoint-simulate-comparison',
        method: 'GET',
        path: '/api/simulate/comparison',
        title: 'Fetch Multi-Scenario Telemedicine Comparison',
        description: 'Retrieves comparative queuing benchmarks across all 4 reference scenarios (100k Baseline, 150k Expansion, 200k Stress, 200k Optimized with Edge AI).',
        params: [],
        curlSnippet: `curl -X GET "${origin}/api/simulate/comparison"`,
        jsSnippet: `const res = await fetch('${origin}/api/simulate/comparison');
const comparison = await res.json();
console.log('Scenarios:', Object.keys(comparison));`,
        pythonSnippet: `import requests
res = requests.get("${origin}/api/simulate/comparison")
print(res.json())`,
        defaultTestPayload: ''
      })}

      <!-- Endpoint 8: GET /api/samples -->
      ${this.renderEndpointCard({
        id: 'endpoint-samples',
        method: 'GET',
        path: '/api/samples',
        title: 'Fetch Preloaded Benchmark Fundus Dataset',
        description: 'Returns preloaded high-resolution fundus images (Levels 0 to 4) with ground truth labels and base64 encoded data for rapid offline testing and clinical validation.',
        params: [],
        curlSnippet: `curl -X GET "${origin}/api/samples"`,
        jsSnippet: `const res = await fetch('${origin}/api/samples');
const samples = await res.json();
console.log('Loaded Samples:', samples.length);`,
        pythonSnippet: `import requests
res = requests.get("${origin}/api/samples")
print("Total samples:", len(res.json()))`,
        defaultTestPayload: ''
      })}
    `;

    this.attachEventListeners(container);
  },

  renderEndpointCard(ep) {
    const isGet = ep.method === 'GET';
    const badgeClass = isGet ? 'get' : 'post';

    const paramsHtml = ep.params.length ? `
      <div style="margin-bottom: 16px;">
        <div style="font-size: 13px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px;">Parameters &amp; Schema</div>
        <div class="data-table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Field Name</th>
                <th>Type</th>
                <th>In</th>
                <th>Required</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              ${ep.params.map(p => `
                <tr>
                  <td class="code-font" style="font-weight: 600; color: var(--primary);">${p.name}</td>
                  <td class="code-font" style="color: var(--neutral);">${p.type}</td>
                  <td><span class="chip chip-neutral" style="font-size: 10px;">${p.in}</span></td>
                  <td>${p.required === 'Yes' ? '<span class="chip chip-error" style="font-size: 10px;">Required</span>' : (p.required === 'Conditional' ? '<span class="chip chip-warning" style="font-size: 10px;">Conditional</span>' : '<span style="color: var(--neutral); font-size: 12px;">Optional</span>')}</td>
                  <td style="font-size: 12.5px; color: var(--text-secondary);">${p.desc}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    ` : '';

    return `
      <div class="api-endpoint-card" id="${ep.id}">
        <div class="api-endpoint-header" onclick="ApiDocsComponent.toggleEndpoint('${ep.id}')">
          <div style="display: flex; align-items: center; gap: 12px; flex: 1; min-width: 0;">
            <span class="api-method-badge ${badgeClass}">${ep.method}</span>
            <span class="api-endpoint-path">${ep.path}</span>
            <span style="font-size: 13px; color: var(--neutral); font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
              — ${ep.title}
            </span>
          </div>
          <svg class="endpoint-toggle-icon" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="transition: transform 200ms ease; flex-shrink: 0;">
            <path d="M19 9l-7 7-7-7"/>
          </svg>
        </div>

        <div class="api-endpoint-body" style="display: block;">
          <p style="font-size: 14px; margin-bottom: 18px;">${ep.description}</p>

          ${paramsHtml}

          <!-- Code Snippets Tabs -->
          <div style="margin-bottom: 20px;">
            <div style="font-size: 13px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px;">Code Examples</div>
            <div class="api-tabs">
              <button class="api-tab-btn active" onclick="ApiDocsComponent.switchSnippetTab('${ep.id}', 'curl')">cURL</button>
              <button class="api-tab-btn" onclick="ApiDocsComponent.switchSnippetTab('${ep.id}', 'js')">JavaScript (Fetch)</button>
              <button class="api-tab-btn" onclick="ApiDocsComponent.switchSnippetTab('${ep.id}', 'python')">Python (Requests)</button>
            </div>
            
            <div class="snippet-content" id="${ep.id}-snippet-curl">
              <div class="code-snippet-box">
                <button class="copy-snippet-btn" onclick="ApiDocsComponent.copySnippet('${ep.id}', 'curl')">Copy cURL</button>
                <pre><code>${this.escapeHtml(ep.curlSnippet)}</code></pre>
              </div>
            </div>

            <div class="snippet-content" id="${ep.id}-snippet-js" style="display: none;">
              <div class="code-snippet-box">
                <button class="copy-snippet-btn" onclick="ApiDocsComponent.copySnippet('${ep.id}', 'js')">Copy JS</button>
                <pre><code>${this.escapeHtml(ep.jsSnippet)}</code></pre>
              </div>
            </div>

            <div class="snippet-content" id="${ep.id}-snippet-python" style="display: none;">
              <div class="code-snippet-box">
                <button class="copy-snippet-btn" onclick="ApiDocsComponent.copySnippet('${ep.id}', 'python')">Copy Python</button>
                <pre><code>${this.escapeHtml(ep.pythonSnippet)}</code></pre>
              </div>
            </div>
          </div>

          <!-- Interactive Live Sandbox -->
          <div class="api-test-sandbox">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 13px; font-weight: 700; color: var(--text-primary);">Interactive Test Sandbox</span>
                <span class="chip chip-neutral" style="font-size: 10px;">Live API Call</span>
              </div>
              <button class="btn btn-sm btn-primary" onclick="ApiDocsComponent.executeLiveTest('${ep.id}', '${ep.method}', '${ep.path}', '${ep.pathParamName || ''}')">
                <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M5 3l14 9-14 9V3z"/></svg>
                Send Request
              </button>
            </div>

            ${ep.pathParamName ? `
              <div class="form-group" style="margin-bottom: 12px;">
                <label class="form-label" style="font-size: 12px;">Path Parameter: {${ep.pathParamName}}</label>
                <input type="text" id="${ep.id}-param-${ep.pathParamName}" class="form-input code-font" value="${ep.defaultPathParam}" style="max-width: 320px; font-size: 13px; padding: 6px 10px;">
              </div>
            ` : ''}

            ${!isGet ? `
              <div class="form-group" style="margin-bottom: 10px;">
                <label class="form-label" style="font-size: 12px;">Request Body (JSON)</label>
                <textarea id="${ep.id}-payload" class="form-textarea code-font" style="font-size: 12.5px; height: 110px;">${ep.defaultTestPayload}</textarea>
              </div>
            ` : ''}

            <div id="${ep.id}-response" class="live-response-pane" style="display: none;">
              <!-- Populated after clicking Send Request -->
            </div>
          </div>
        </div>
      </div>
    `;
  },

  toggleEndpoint(id) {
    const card = document.getElementById(id);
    if (!card) return;
    const body = card.querySelector('.api-endpoint-body');
    const header = card.querySelector('.api-endpoint-header');
    const icon = card.querySelector('.endpoint-toggle-icon');

    if (body.style.display === 'none') {
      body.style.display = 'block';
      header.classList.add('expanded');
      icon.style.transform = 'rotate(180deg)';
    } else {
      body.style.display = 'none';
      header.classList.remove('expanded');
      icon.style.transform = 'rotate(0deg)';
    }
  },

  switchSnippetTab(endpointId, lang) {
    const card = document.getElementById(endpointId);
    if (!card) return;

    card.querySelectorAll('.api-tab-btn').forEach(b => b.classList.remove('active'));
    card.querySelectorAll('.snippet-content').forEach(s => s.style.display = 'none');

    const targetSnippet = document.getElementById(`${endpointId}-snippet-${lang}`);
    if (targetSnippet) targetSnippet.style.display = 'block';

    const buttons = card.querySelectorAll('.api-tab-btn');
    if (lang === 'curl' && buttons[0]) buttons[0].classList.add('active');
    if (lang === 'js' && buttons[1]) buttons[1].classList.add('active');
    if (lang === 'python' && buttons[2]) buttons[2].classList.add('active');
  },

  async copySnippet(endpointId, lang) {
    const snippetEl = document.querySelector(`#${endpointId}-snippet-${lang} code`);
    if (!snippetEl) return;
    try {
      await navigator.clipboard.writeText(snippetEl.textContent);
      App.showToast('Code snippet copied to clipboard!', 'success');
    } catch (e) {
      App.showToast('Failed to copy snippet', 'error');
    }
  },

  async executeLiveTest(endpointId, method, pathTemplate, pathParamName) {
    const responseBox = document.getElementById(`${endpointId}-response`);
    if (!responseBox) return;

    responseBox.style.display = 'block';
    responseBox.innerHTML = '<span style="color: var(--neutral);">Executing request against local server...</span>';

    let url = pathTemplate;
    if (pathParamName) {
      const paramVal = document.getElementById(`${endpointId}-param-${pathParamName}`)?.value?.trim() || 'SCR-9001';
      url = url.replace(`{${pathParamName}}`, paramVal);
    }

    const startTime = performance.now();

    try {
      let options = { method };
      if (method === 'POST') {
        const payloadStr = document.getElementById(`${endpointId}-payload`)?.value || '{}';
        options.headers = { 'Content-Type': 'application/json' };
        options.body = payloadStr;
      }

      const res = await fetch(url, options);
      const elapsed = Math.round(performance.now() - startTime);

      let responseContent = '';
      const contentType = res.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        const json = await res.json();
        responseContent = JSON.stringify(json, null, 2);
      } else {
        const text = await res.text();
        responseContent = text.length > 500 ? text.substring(0, 500) + '...\n[Truncated HTML Report Preview]' : text;
      }

      const statusColor = res.ok ? '#22C55E' : '#EF4444';

      responseBox.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid #292524; padding-bottom: 6px;">
          <div>
            <span style="background: ${statusColor}20; color: ${statusColor}; border: 1px solid ${statusColor}40; padding: 2px 8px; border-radius: 4px; font-weight: 700; margin-right: 8px;">HTTP ${res.status} ${res.statusText}</span>
            <span style="color: var(--neutral);">Latency: <strong style="color: var(--text-primary);">${elapsed} ms</strong></span>
          </div>
          <button class="copy-snippet-btn" style="position: static;" onclick="navigator.clipboard.writeText(document.getElementById('${endpointId}-raw-output').innerText); App.showToast('Response copied!', 'success');">Copy Response</button>
        </div>
        <pre id="${endpointId}-raw-output" style="color: ${res.ok ? '#86EFAC' : '#FCA5A5'}; font-size: 12px; margin: 0; max-height: 260px; overflow-y: auto;"><code>${this.escapeHtml(responseContent)}</code></pre>
      `;
    } catch (err) {
      const elapsed = Math.round(performance.now() - startTime);
      responseBox.innerHTML = `
        <div style="color: #EF4444; font-weight: 700; margin-bottom: 6px;">
          Network / Request Error (${elapsed} ms)
        </div>
        <div style="color: #FCA5A5;">${this.escapeHtml(err.message)}</div>
      `;
    }
  },

  escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  },

  attachEventListeners(container) {
    // Initial active states
  }
};
