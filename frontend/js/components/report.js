/**
 * frontend/js/components/report.js - Clinical Screening Report Viewer Component (Person 3)
 */

const ReportComponent = {
  render(container) {
    const caseData = App.currentScreeningCase;
    if (!caseData) {
      container.innerHTML = `
        <div class="card" style="text-align: center; padding: 48px;">
          <h2 style="margin-bottom: 8px;">No Report Loaded</h2>
          <p>Please select a case from the Dashboard or complete a screening review.</p>
          <button class="btn btn-primary btn-md" onclick="App.navigateTo('dashboard')">Go to Dashboard</button>
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <div class="header-actions" style="margin-bottom: 24px; justify-content: space-between; display: flex; align-items: flex-end;">
        <div>
          <h1 style="margin-bottom: 4px;">Standardized Clinical Screening Report</h1>
          <p style="margin: 0; color: var(--neutral);">
            Official SIH Tele-Ophthalmology Screening Document • Report ID: <span class="code-font" style="font-weight: 600; color: var(--text-primary);">${caseData.id}</span>
          </p>
        </div>
        <div style="display: flex; gap: 12px;">
          <button class="btn btn-secondary btn-md" onclick="App.navigateTo('dashboard')">
            Back to Dashboard
          </button>
          <button class="btn btn-primary btn-md" id="btn-print-report">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M6 9V2h12v7M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2m-4 0v4H8v-4m0 0h8"/></svg>
            Print / Save as PDF
          </button>
        </div>
      </div>

      <!-- Embedded Clean Report Card -->
      <div class="card" style="max-width: 960px; margin: 0 auto 32px; padding: 32px; background: #FFFFFF; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">
        <iframe id="report-frame" src="/api/report/${caseData.id}" style="width: 100%; min-height: 840px; border: none; border-radius: 8px;"></iframe>
      </div>
    `;

    container.querySelector('#btn-print-report').addEventListener('click', () => {
      const frame = document.getElementById('report-frame');
      if (frame && frame.contentWindow) {
        frame.contentWindow.print();
      } else {
        window.open(`/api/report/${caseData.id}`, '_blank');
      }
    });
  }
};
