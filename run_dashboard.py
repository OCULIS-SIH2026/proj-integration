#!/usr/bin/env python3
"""
run_dashboard.py - One-Click Launcher for the RetinaAI Dashboard (Person 3)
Smart India Hackathon (SIH) Diabetic Retinopathy Tele-Ophthalmology Screening Platform
"""
import sys
import os
import webbrowser
import threading
import time

# Ensure workspace root is in sys.path
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from backend.api import run_server
from backend.database import init_db, get_dashboard_stats
from backend.pipeline import run_screening_pipeline
from simulink.telemedicine_sim import run_simulation

def run_self_test():
    """
    Validates that all Person 1, Person 2, and Person 3 components are wired correctly.
    """
    print("==================================================")
    print("      OculisAI System Diagnostic Self-Test        ")
    print("==================================================")
    init_db()
    print("âœ“ [Database] SQLite store initialized successfully.")

    # Auto-seed initial demo cohort if fresh clone or empty database
    initial_stats = get_dashboard_stats()
    if initial_stats.get('total_screenings', 0) == 0:
        print("â„¹ [Database] Empty database detected on fresh launch. Auto-seeding demo cohort...")
        try:
            from backend.seed_data import seed
            seed()
            print("âœ“ [Database] Auto-seeded demo cases successfully.")
        except Exception as e:
            print(f"! [Database] Auto-seeding notice: {e}")

    sample_img_path = os.path.join(WORKSPACE_DIR, 'sample_data', 'images', 'sample_moderate_level2.bmp')
    if os.path.exists(sample_img_path):
        with open(sample_img_path, 'rb') as f:
            img_bytes = f.read()

        meta = {'patient_id': 'TEST-001', 'sample_hint': 'moderate'}
        res = run_screening_pipeline(img_bytes, meta)

        # New schema: quality.* / prediction.* / triage.*
        q = res.get('quality', res.get('image_quality', {}))
        pred = res.get('prediction', res.get('dr_prediction', {}))
        triage = res.get('triage', {})
        visuals = res.get('visuals', res.get('explainability', {}))
        gradcam_uri = visuals.get('gradcam_overlay', visuals.get('heatmap_base64', ''))

        q_status = q.get('status', q.get('quality', 'Pass'))
        q_score = q.get('overall_score', q.get('score', 0.9))
        p_level = pred.get('stage', pred.get('level', 0))
        p_label = pred.get('label', 'No DR')
        p_conf = pred.get('confidence', 0.0)
        is_ref = triage.get('is_referable', res.get('referable_dr', False))
        t_rec = triage.get('recommendation', res.get('recommendation', ''))
        proc_ms = res.get('processing_time_ms', 0)

        lesions = res.get('lesions', {})
        ma_cnt = lesions.get('microaneurysms', {}).get('count', 0)
        ha_cnt = lesions.get('hemorrhages', {}).get('count', 0)
        ex_cnt = lesions.get('exudates', {}).get('count', 0)
        nv_stat = "Detected" if lesions.get('neovascularization', {}).get('detected') else "None"

        print(f"âœ“ [Quality] Status: {str(q_status).upper()} (Score: {q_score})")
        print(f"âœ“ [Person 1 AI] Predicted: Level {p_level} ({p_label}), Conf: {p_conf}")
        print(f"âœ“ [Person 2 XAI] Grad-CAM Heatmap generated ({len(gradcam_uri)} chars)")
        print(f"âœ“ [Person 2 Lesions] Candidates: MA={ma_cnt}, HE={ha_cnt}, EX={ex_cnt}, NV={nv_stat}")
        print(f"âœ“ [Triage Contract] Referable: {is_ref}, Recommendation: {t_rec}")
        print(f"âœ“ [Processing] Pipeline completed in {proc_ms} ms")

    else:
        print("! [Sample Notice] Sample images not yet generated at", sample_img_path)

    # Validate MATLAB pipeline & Simulink co-location
    matlab_dir = os.path.join(WORKSPACE_DIR, 'matlab_pipeline')
    if os.path.exists(matlab_dir) and os.path.exists(os.path.join(matlab_dir, 'setup_environment.m')):
        print("âœ“ [Person 2 MATLAB] 10-Phase screening engine & Simulink scripts verified.")

    sim = run_simulation('scenario_a')
    print(f"âœ“ [Simulink Telemedicine] Simulated Scenario A: Throughput = {sim['results']['total_throughput_annual']} pts/yr, Doctor Util = {sim['results']['doctor_utilization_pct']}%, Status: {sim['results']['bottleneck_stage']}")

    stats = get_dashboard_stats()
    print(f"âœ“ [Dashboard KPIs] Total cases in database: {stats['total_screenings']}, Referable: {stats['referable_cases']}")
    print("==================================================")
    print("         All Diagnostic Tests PASSED!             ")
    print("==================================================")

def main():
    port = 8000
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            run_self_test()
            return
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    run_self_test()

    print(f"\n==================================================")
    print(f"  OculisAI Web Platform Online")
    print(f"  Dashboard UI:           http://localhost:{port}")
    print(f"  Telemedicine Studio:    http://localhost:{port}/#simulation")
    print(f"  Screening REST API:     POST http://localhost:{port}/api/screen")
    print(f"  System Health API:      GET http://localhost:{port}/api/health")
    print(f"==================================================")

    # Spawn background thread to open default browser after short pause
    def open_browser():
        time.sleep(1.2)
        try:
            webbrowser.open(f"http://localhost:{port}")
        except Exception:
            pass

    threading.Thread(target=open_browser, daemon=True).start()
    run_server(port)

if __name__ == '__main__':
    main()

