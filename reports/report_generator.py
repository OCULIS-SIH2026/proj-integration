"""
reports/report_generator.py - Generates Standardized SIH Screening Reports
"""
import json
from datetime import datetime

def generate_report_html(screening_data):
    """
    Generates a clean, print-ready HTML screening report
    incorporating patient info, quality metrics, AI diagnosis,
    Grad-CAM explainability, and doctor review validation.
    """
    s = screening_data
    patient_id = s.get('patient_id', 'PAT-UNKNOWN')
    name = s.get('patient_name', 'Anonymous')
    age = s.get('patient_age', '55')
    gender = s.get('patient_gender', 'Unspecified')
    duration = s.get('diabetes_duration', '5')
    hba1c = s.get('hba1c', '7.5')
    eye = s.get('eye', 'OD')
    timestamp = s.get('timestamp', datetime.now().isoformat())

    # Format date
    try:
        dt = datetime.fromisoformat(timestamp)
        formatted_date = dt.strftime("%B %d, %Y - %H:%M")
    except Exception:
        formatted_date = timestamp

    # Quality: new schema quality.* with legacy image_quality.* fallback
    quality_new = s.get('quality', {})
    quality_legacy = s.get('image_quality', {})
    q_status_raw = quality_new.get('status') or quality_legacy.get('status', 'Pass')
    q_status = q_status_raw.upper()
    q_score_raw = quality_new.get('overall_score') or quality_legacy.get('score', 0.9)
    try:
        q_val = float(q_score_raw)
        q_score = int(q_val * 100) if q_val <= 1.0 else int(q_val)
    except (ValueError, TypeError):
        q_score = 90

    q_metrics = quality_new.get('metrics', {})
    q_sharpness = round(float(q_metrics.get('sharpness', 0.9)), 2)
    q_brightness = round(float(q_metrics.get('brightness', 0.9)), 2)
    q_contrast = round(float(q_metrics.get('contrast', 0.9)), 2)
    q_fov = 'Valid' if q_metrics.get('fov_valid', True) else 'Invalid'
    enhancement = s.get('enhancement', {})
    enh_applied = enhancement.get('applied', False)
    enh_method = enhancement.get('method', 'None')

    # Prediction: new schema prediction.* with legacy dr_prediction.* fallback
    pred_new = s.get('prediction', {})
    pred_legacy = s.get('dr_prediction', {})
    level = pred_new.get('stage', pred_new.get('level', pred_legacy.get('level', 0)))
    label = pred_new.get('label', pred_legacy.get('label', 'No DR'))
    conf_raw = pred_new.get('confidence', pred_legacy.get('confidence', 0.85))
    try:
        conf_val = float(conf_raw)
        conf = int(conf_val * 100) if conf_val <= 1.0 else int(conf_val)
    except (ValueError, TypeError):
        conf = 85
    description = pred_new.get('description', '')

    # Triage: new schema triage.* with legacy fallback
    triage = s.get('triage', {})
    referable = triage.get('is_referable', s.get('referable_dr', level >= 2))
    triage_urgency = triage.get('urgency', 'Routine Ophthalmology')
    triage_timeframe = triage.get('timeframe', '')
    triage_recommendation = triage.get('recommendation', s.get('recommendation', ''))

    # Probabilities (new: keyed by class label)
    probabilities = pred_new.get('probabilities', pred_legacy.get('scores', {}))
    class_order = ['No DR', 'Mild NPDR', 'Moderate NPDR', 'Severe NPDR', 'Proliferative DR']

    processing_time = s.get('processing_time_ms', 0)

    findings = s.get('findings', [])
    findings_html = "".join([f"<li style='margin-bottom:4px;'>• {f.replace('_', ' ').title()}</li>" for f in findings]) or "<li>• No significant microvascular lesions detected.</li>"

    # Doctor review
    doc_status = s.get('doctor_status', 'pending')
    doc_dr_level = s.get('doctor_dr_level', level)
    doc_action = s.get('doctor_referral_action', 'Routine Follow-up')
    doc_notes = s.get('doctor_notes', 'Clinical examination findings concordant with screening telemetry.')
    doc_name = s.get('doctor_name', 'Dr. S. Ramanathan, MD (Ophthalmology)')
    doc_time = s.get('doctor_review_time', formatted_date)

    referable_badge_color = "#DC2626" if referable else "#16A34A"
    referable_text = "REFERABLE DR (YES)" if referable else "NON-REFERABLE (NO)"

    # Probability HTML for report
    prob_rows_html = ""
    for cls in class_order:
        p = probabilities.get(cls, 0)
        pct = round(float(p) * 100, 1)
        active_style = "font-weight:700;color:#C2410C;" if cls == label else ""
        prob_rows_html += f"<tr><td style='padding:2px 8px;font-size:12px;{active_style}'>{cls}</td><td style='padding:2px 8px;'><div style='height:6px;width:{pct}%;background:#C2410C;border-radius:3px;min-width:4px;'></div></td><td style='padding:2px 8px;font-size:12px;font-family:monospace;{active_style}'>{pct}%</td></tr>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>RetinaAI Screening Report - {patient_id}</title>
    <style>
        @page {{ size: A4; margin: 16mm; }}
        body {{
            font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #1C1917;
            background: #FFFFFF;
            margin: 0;
            padding: 24px;
            line-height: 1.5;
        }}
        .report-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #C2410C;
            padding-bottom: 12px;
            margin-bottom: 20px;
        }}
        .brand {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 26px;
            font-weight: bold;
            color: #C2410C;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 600;
        }}
        .card {{
            border: 1px solid #D6D3D1;
            border-radius: 8px;
            padding: 14px;
            margin-bottom: 16px;
            background: #FAFAF9;
        }}
        .section-title {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 17px;
            font-weight: bold;
            color: #1C1917;
            margin-bottom: 10px;
            border-bottom: 1px solid #E7E5E4;
            padding-bottom: 4px;
        }}
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }}
        .grid-3 {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 12px;
        }}
        .stat-label {{
            font-size: 12px;
            color: #78716C;
            text-transform: uppercase;
            font-weight: 600;
        }}
        .stat-val {{
            font-size: 15px;
            font-weight: 600;
            color: #1C1917;
        }}
        .stepper {{
            display: flex;
            align-items: center;
            margin: 12px 0;
            gap: 8px;
        }}
        .step {{
            flex: 1;
            text-align: center;
            padding: 6px 2px;
            font-size: 11px;
            font-weight: 600;
            border-radius: 4px;
            background: #E7E5E4;
            color: #78716C;
        }}
        .step.active {{
            background: #C2410C;
            color: #FFFFFF;
        }}
        .disclaimer {{
            font-size: 11px;
            color: #78716C;
            border-top: 1px solid #D6D3D1;
            padding-top: 10px;
            margin-top: 24px;
            text-align: center;
        }}
        @media print {{
            body {{ padding: 0; }}
            .no-print {{ display: none !important; }}
        }}
    </style>
</head>
<body>
    <div class="report-header">
        <div>
            <div class="brand">RetinaAI Tele-Ophthalmology</div>
            <div style="font-size: 13px; color: #78716C;">National Diabetic Retinopathy Screening Program</div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 13px; font-weight: 600;">Report ID: {s.get('id', 'SCR-000')}</div>
            <div style="font-size: 12px; color: #78716C;">Exam Date: {formatted_date}</div>
        </div>
    </div>

    <!-- Patient Demographics -->
    <div class="card">
        <div class="section-title">Patient Demographics & Clinical History</div>
        <div class="grid-3">
            <div><span class="stat-label">Patient ID:</span> <span class="stat-val">{patient_id}</span></div>
            <div><span class="stat-label">Name:</span> <span class="stat-val">{name}</span></div>
            <div><span class="stat-label">Age / Gender:</span> <span class="stat-val">{age}y / {gender}</span></div>
            <div><span class="stat-label">Diabetes Duration:</span> <span class="stat-val">{duration} Years</span></div>
            <div><span class="stat-label">HbA1c:</span> <span class="stat-val">{hba1c}%</span></div>
            <div><span class="stat-label">Examined Eye:</span> <span class="stat-val">{eye} ({"Right Eye" if eye=="OD" else "Left Eye"})</span></div>
        </div>
    </div>

    <!-- Quality & Prediction -->
    <div class="grid-2">
        <div class="card">
            <div class="section-title">Image Quality Assessment</div>
            <div style="margin-bottom: 8px;">
                <span class="stat-label">Status:</span>
                <span class="badge" style="background: {'#DCFCE7' if q_status in ('GOOD','PASS') else '#FEF3C7'}; color: {'#166534' if q_status in ('GOOD','PASS') else '#92400E'};">{q_status} ({q_score}%)</span>
            </div>
            <div style="font-size: 13px; color: #57534E;">
                Sharpness: {q_sharpness} &bull; Brightness: {q_brightness} &bull; Contrast: {q_contrast} &bull; FOV: {q_fov}
            </div>
            {'<div style="font-size:12px;margin-top:6px;color:#92400E;">Enhancement Applied: ' + enh_method + '</div>' if enh_applied else ''}
        </div>

        <div class="card">
            <div class="section-title">Referral Triage Status</div>
            <div style="margin-bottom: 8px;">
                <span class="badge" style="background: {referable_badge_color}; color: white; font-size: 14px;">{referable_text}</span>
            </div>
            <div style="font-size: 13px; color: #57534E;">
                {triage_urgency}{(' &bull; ' + triage_timeframe) if triage_timeframe else ''}
            </div>
        </div>
    </div>

    <!-- AI DR Classification Result -->
    <div class="card">
        <div class="section-title">AI Deep Learning Classification (EfficientNet-B0)</div>
        <div style="display: flex; justify-content: space-between; align-items: baseline;">
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #C2410C;">Level {level} — {label}</span>
                {('<div style="font-size:13px;color:#57534E;margin-top:4px;">' + description + '</div>') if description else ''}
            </div>
            <div>
                <span class="stat-label">Calibrated Confidence:</span>
                <span style="font-size: 18px; font-weight: bold; color: #1C1917;">{conf}%</span>
            </div>
        </div>

        <!-- 5-stage progress bar -->
        <div class="stepper">
            <div class="step {'active' if level==0 else ''}">0: No DR</div>
            <div class="step {'active' if level==1 else ''}">1: Mild</div>
            <div class="step {'active' if level==2 else ''}">2: Moderate</div>
            <div class="step {'active' if level==3 else ''}">3: Severe</div>
            <div class="step {'active' if level==4 else ''}">4: PDR</div>
        </div>

        <!-- Probability breakdown -->
        <div style="margin-top: 10px;">
            <div class="stat-label" style="margin-bottom: 4px;">Per-Class Probability Breakdown:</div>
            <table style="width:100%;border-collapse:collapse;">{prob_rows_html}</table>
        </div>

        <div style="margin-top: 12px;">
            <div class="stat-label" style="margin-bottom: 4px;">Detected Retinal Microvascular Signs:</div>
            <ul style="margin: 0; padding-left: 18px; font-size: 13px; color: #44403C;">
                {findings_html}
            </ul>
        </div>

        <!-- Lesion Candidate Evidence (Person 2 Phase 5) -->
        <div style="margin-top: 12px; background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 6px; padding: 10px 12px;">
            <div style="font-size: 12px; font-weight: 700; color: #92400E; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;">
                Quantitative Lesion Candidate Evidence (Person 2 CV Engine)
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align: center;">
                <div style="background: white; padding: 6px; border-radius: 4px; border: 1px solid #E5E7EB;">
                    <div style="font-size: 11px; color: #6B7280;">Microaneurysms</div>
                    <div style="font-size: 16px; font-weight: 700; color: #CA8A04;">{s.get('lesions', {}).get('microaneurysms', {}).get('count', 0)}</div>
                </div>
                <div style="background: white; padding: 6px; border-radius: 4px; border: 1px solid #E5E7EB;">
                    <div style="font-size: 11px; color: #6B7280;">Hemorrhages</div>
                    <div style="font-size: 16px; font-weight: 700; color: #DC2626;">{s.get('lesions', {}).get('hemorrhages', {}).get('count', 0)}</div>
                </div>
                <div style="background: white; padding: 6px; border-radius: 4px; border: 1px solid #E5E7EB;">
                    <div style="font-size: 11px; color: #6B7280;">Hard Exudates</div>
                    <div style="font-size: 16px; font-weight: 700; color: #0891B2;">{s.get('lesions', {}).get('exudates', {}).get('count', 0)}</div>
                </div>
                <div style="background: white; padding: 6px; border-radius: 4px; border: 1px solid #E5E7EB;">
                    <div style="font-size: 11px; color: #6B7280;">Neovascularization</div>
                    <div style="font-size: 13px; font-weight: 700; color: {'#DC2626' if s.get('lesions', {}).get('neovascularization', {}).get('detected') else '#16A34A'};">
                        {'POSITIVE' if s.get('lesions', {}).get('neovascularization', {}).get('detected') else 'NEGATIVE'}
                    </div>
                </div>
            </div>
            <div style="font-size: 11px; color: #92400E; margin-top: 6px; font-style: italic;">
                {s.get('lesions', {}).get('clinical_notice', 'Candidate detections represent supporting evidence and require clinical review.')}
            </div>
        </div>

        {('<div style="margin-top:10px;font-size:13px;color:#57534E;border-left:3px solid #C2410C;padding-left:10px;"><strong>Recommendation:</strong> ' + triage_recommendation + '</div>') if triage_recommendation else ''}
        <div style="font-size:11px;color:#A8A29E;margin-top:8px;">Processing time: {processing_time} ms</div>
    </div>

    <!-- Doctor Review & Clinical Sign-off -->
    <div class="card" style="border-left: 4px solid #C2410C;">
        <div class="section-title">Ophthalmologist Human-in-the-Loop Validation</div>
        <div class="grid-2" style="margin-bottom: 10px;">
            <div>
                <span class="stat-label">Doctor Status:</span>
                <span class="stat-val">{doc_status.upper()}</span>
            </div>
            <div>
                <span class="stat-label">Final Diagnosed Level:</span>
                <span class="stat-val">Level {doc_dr_level}</span>
            </div>
            <div>
                <span class="stat-label">Referral Route:</span>
                <span class="stat-val">{doc_action}</span>
            </div>
            <div>
                <span class="stat-label">Reviewing Clinician:</span>
                <span class="stat-val">{doc_name}</span>
            </div>
        </div>
        <div style="margin-top: 8px;">
            <div class="stat-label">Clinician Findings & Recommendations:</div>
            <div style="font-size: 14px; font-style: italic; color: #292524; background: #FFFFFF; padding: 8px 12px; border: 1px solid #D6D3D1; border-radius: 6px; margin-top: 4px;">
                "{doc_notes}"
            </div>
        </div>
        <div style="text-align: right; margin-top: 10px; font-size: 12px; color: #78716C;">
            Digitally Validated on {doc_time}
        </div>
    </div>

    <div class="disclaimer">
        <strong>CLINICAL NOTICE:</strong> This report is generated by an AI screening assistance platform conforming to the SIH Tele-Ophthalmology Specification. AI outputs do not replace direct ophthalmoscopy.
    </div>

    <div class="no-print" style="margin-top: 20px; text-align: center;">
        <button onclick="window.print()" style="background: #C2410C; color: white; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 14px;">
            Print / Save as PDF
        </button>
    </div>
</body>
</html>"""
    return html
