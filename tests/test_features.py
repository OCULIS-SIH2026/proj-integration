"""
tests/test_features.py - Feature & Integration Test Suite for RetinaAI Platform
Validates end-to-end API workflows, schema adherence against mock_response.json,
and human-in-the-loop clinical auditing using in-memory request simulation.
Can be run via:
    python3 -m unittest tests/test_features.py -v
    or
    python3 -m unittest discover -s tests -v
"""
import unittest
import os
import sys
import io
import json

# Ensure workspace root is in sys.path
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from backend.api import RetinaAPIHandler
from backend.database import init_db


class MockSocket:
    """In-memory duplex stream mock for socket operations."""
    def __init__(self, data=b''):
        self.rfile = io.BytesIO(data)
        self.wfile = io.BytesIO()

    def makefile(self, mode, *args, **kwargs):
        if 'b' in mode:
            if 'r' in mode:
                return self.rfile
            elif 'w' in mode:
                return self.wfile
        raise ValueError(f"Unsupported mock socket mode: {mode}")

    def sendall(self, data):
        self.wfile.write(data)


def simulate_request(method, path, body=None, headers=None):
    """
    Executes an HTTP request directly through the RetinaAPIHandler pipeline.
    Returns:
        tuple: (status_code: int, response_body: bytes, content_type: str)
    """
    if headers is None:
        headers = {}

    body_bytes = b''
    if body is not None:
        if isinstance(body, dict):
            body_bytes = json.dumps(body).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        elif isinstance(body, bytes):
            body_bytes = body
        elif isinstance(body, str):
            body_bytes = body.encode('utf-8')
        headers['Content-Length'] = str(len(body_bytes))

    req_lines = [f"{method} {path} HTTP/1.1", "Host: localhost"]
    for k, v in headers.items():
        req_lines.append(f"{k}: {v}")
    raw_request = "\r\n".join(req_lines).encode('utf-8') + b"\r\n\r\n" + body_bytes

    sock = MockSocket(raw_request)

    # Suppress standard handler logging during unit test execution
    class SilentHandler(RetinaAPIHandler):
        def log_message(self, format, *args):
            pass

    SilentHandler(sock, ('127.0.0.1', 8000), None)

    response_bytes = sock.wfile.getvalue()
    header_part, _, resp_body = response_bytes.partition(b"\r\n\r\n")

    lines = header_part.split(b"\r\n")
    status_line = lines[0].decode('utf-8', errors='replace')
    status_code = int(status_line.split(' ')[1])

    content_type = ""
    for line in lines[1:]:
        header_text = line.decode('utf-8', errors='replace')
        if header_text.lower().startswith("content-type:"):
            content_type = header_text.split(":", 1)[1].strip()
            break

    return status_code, resp_body, content_type


class TestRetinaAIFeatures(unittest.TestCase):
    """End-to-end feature test suite testing HTTP endpoints and contract conformance."""

    @classmethod
    def setUpClass(cls):
        init_db()

    def test_feature_01_static_ui_hosting(self):
        """Feature 1: Precision Clinical frontend UI is served at GET /."""
        status, body, ctype = simulate_request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"RetinaAI", body)
        self.assertIn("text/html", ctype)

    def test_feature_02_health_endpoint(self):
        """Feature 2: Health API reports service status and CDSCO compliance."""
        status, body, ctype = simulate_request("GET", "/api/health")
        self.assertEqual(status, 200)
        data = json.loads(body.decode('utf-8'))
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data.get("cdsco_compliant", False))

    def test_feature_03_benchmark_samples(self):
        """Feature 3: Sample gallery endpoint returns pre-loaded clinical cases."""
        status, body, ctype = simulate_request("GET", "/api/samples")
        self.assertEqual(status, 200)
        samples = json.loads(body.decode('utf-8'))
        self.assertGreaterEqual(len(samples), 5)
        sample_keys = [s["id"] for s in samples]
        self.assertIn("sample_level0_normal", sample_keys)
        self.assertIn("sample_level2_moderate", sample_keys)

    def test_feature_04_full_screening_contract_conformance(self):
        """Feature 4: Screening API executes pipeline and conforms to mock_response.json schema."""
        status, body, ctype = simulate_request("POST", "/api/screen", {
            "sample_id": "sample_level2_moderate",
            "patient_meta": {
                "patient_id": "PT-2026-FEAT-001",
                "patient_name": "Kavitha Rangarajan",
                "patient_age": 59,
                "patient_gender": "Female",
                "diabetes_duration": 9,
                "hba1c": 8.0,
                "eye": "OD",
                "sample_hint": "sample_level2_moderate"
            }
        })
        self.assertEqual(status, 200)
        res = json.loads(body.decode('utf-8'))

        # Top-level contract validation against mock_response.json
        expected_top = ["status", "patient_id", "processing_time_ms", "quality", "prediction", "triage", "enhancement", "visuals"]
        for k in expected_top:
            self.assertIn(k, res, f"Missing contract key: {k}")

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["patient_id"], "PT-2026-FEAT-001")

        # Quality contract
        q = res["quality"]
        for qk in ["status", "overall_score", "metrics", "rejection_reasons", "is_acceptable"]:
            self.assertIn(qk, q)
        for qm in ["sharpness", "brightness", "contrast", "fov_valid"]:
            self.assertIn(qm, q["metrics"])
        self.assertTrue(q["is_acceptable"])

        # Prediction contract
        p = res["prediction"]
        for pk in ["stage", "label", "confidence", "probabilities"]:
            self.assertIn(pk, p)
        self.assertEqual(p["stage"], 2)
        self.assertEqual(p["label"], "Moderate NPDR")
        self.assertIsInstance(p["confidence"], float)
        self.assertEqual(len(p["probabilities"]), 5)

        # Triage contract
        tr = res["triage"]
        for tk in ["is_referable", "referral_category", "urgency", "timeframe", "recommendation", "confidence_score"]:
            self.assertIn(tk, tr)
        self.assertTrue(tr["is_referable"])
        self.assertEqual(tr["referral_category"], "Referable Diabetic Retinopathy")

        # Visuals contract
        v = res["visuals"]
        for vk in ["original_image", "enhanced_image", "gradcam_overlay"]:
            self.assertIn(vk, v)
            self.assertTrue(v[vk].startswith("data:image/"))

    def test_feature_05_fuzzy_sample_alias(self):
        """Feature 5: Screening endpoint supports friendly alias matching (e.g. sample-002)."""
        status, body, ctype = simulate_request("POST", "/api/screen", {
            "sample_id": "sample-002",
            "patient_id": "PT-ALIAS-002"
        })
        self.assertEqual(status, 200)
        res = json.loads(body.decode('utf-8'))
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["prediction"]["stage"], 2)

    def test_feature_06_quality_rejection_flow(self):
        """Feature 6: Poor quality images trigger automated rejection with recapture advice."""
        status, body, ctype = simulate_request("POST", "/api/screen", {
            "sample_id": "sample_poor_quality_blur",
            "patient_id": "PT-POOR-003"
        })
        self.assertEqual(status, 200)
        res = json.loads(body.decode('utf-8'))
        self.assertEqual(res["status"], "rejected")
        self.assertFalse(res["quality"]["is_acceptable"])
        self.assertGreater(len(res["quality"]["rejection_reasons"]), 0)
        self.assertEqual(res["triage"]["urgency"], "Recapture Required")

    def test_feature_07_worklist_and_stats(self):
        """Feature 7: Worklist API retrieves persistent screenings and aggregate KPIs."""
        status, body, ctype = simulate_request("GET", "/api/screenings")
        self.assertEqual(status, 200)
        data = json.loads(body.decode('utf-8'))
        self.assertIn("screenings", data)
        self.assertIn("stats", data)
        self.assertGreater(len(data["screenings"]), 0)
        self.assertIn("total_screenings", data["stats"])
        self.assertIn("referable_cases", data["stats"])

    def test_feature_08_single_screening_lookup(self):
        """Feature 8: Specific screening detail lookup by UUID."""
        status, body, _ = simulate_request("POST", "/api/screen", {
            "sample_id": "sample_level1_mild",
            "patient_meta": {"sample_hint": "sample_level1_mild"}
        })
        created = json.loads(body.decode('utf-8'))
        screening_id = created["id"]

        status, body, ctype = simulate_request("GET", f"/api/screenings/{screening_id}")
        self.assertEqual(status, 200)
        retrieved = json.loads(body.decode('utf-8'))
        self.assertEqual(retrieved["id"], screening_id)
        self.assertEqual(retrieved["prediction"]["stage"], 1)

    def test_feature_09_html_report_generation(self):
        """Feature 9: Clinical report endpoint generates valid print-ready HTML."""
        status, body, _ = simulate_request("POST", "/api/screen", {
            "sample_id": "sample_level2_moderate",
            "patient_meta": {"sample_hint": "sample_level2_moderate"}
        })
        created = json.loads(body.decode('utf-8'))
        screening_id = created["id"]

        status, body, ctype = simulate_request("GET", f"/api/report/{screening_id}")
        self.assertEqual(status, 200)
        self.assertIn("text/html", ctype)
        self.assertIn(b"<!DOCTYPE html>", body)
        self.assertIn(b"RetinaAI Screening Report", body)
        self.assertIn(screening_id.encode('utf-8'), body)

    def test_feature_10_doctor_review_workflow(self):
        """Feature 10: Doctor review records clinician validation, overrides, and notes."""
        status, body, _ = simulate_request("POST", "/api/screen", {
            "sample_id": "sample_level2_moderate",
            "patient_meta": {"sample_hint": "sample_level2_moderate"}
        })
        created = json.loads(body.decode('utf-8'))
        screening_id = created["id"]

        review_payload = {
            "screening_id": screening_id,
            "doctor_status": "accepted",
            "doctor_dr_level": 2,
            "doctor_referral_action": "Refer to Vitreoretinal Specialist within 2 weeks",
            "doctor_notes": "Concur with AI grading. Microvascular changes verified.",
            "doctor_name": "Dr. S. Ramanathan, MD (Ophthalmology)"
        }
        status, body, ctype = simulate_request("POST", "/api/review", review_payload)
        self.assertEqual(status, 200)
        res = json.loads(body.decode('utf-8'))
        self.assertTrue(res["success"])
        self.assertEqual(res["screening"]["doctor_status"], "accepted")
        self.assertEqual(res["screening"]["doctor_dr_level"], 2)
        self.assertIn("Microvascular", res["screening"]["doctor_notes"])

    def test_feature_11_telemedicine_simulation(self):
        """Feature 11: Simulink telemedicine queuing simulation API executes scenarios."""
        sim_payload = {
            "scenario": "scenario_b",
            "overrides": {}
        }
        status, body, ctype = simulate_request("POST", "/api/simulate", sim_payload)
        self.assertEqual(status, 200)
        sim_res = json.loads(body.decode('utf-8'))
        self.assertEqual(sim_res["scenario_id"], "scenario_b")
        self.assertIn("results", sim_res)
        self.assertEqual(sim_res["results"]["total_throughput_annual"], 150000)

    def test_feature_12_telemedicine_scenario_comparison(self):
        """Feature 12: Simulation comparison API delivers multi-scenario benchmark matrix."""
        status, body, ctype = simulate_request("GET", "/api/simulate/comparison")
        self.assertEqual(status, 200)
        comp = json.loads(body.decode('utf-8'))
        self.assertEqual(len(comp), 4)
        for sc in ["scenario_a", "scenario_b", "scenario_c", "scenario_d"]:
            self.assertIn(sc, comp)
    def test_feature_13_all_dr_stages_with_frontend_payload(self):
        """Feature 13: Replicating frontend payload (both sample_id & image_base64) yields distinct stages 0-4."""
        samples_meta_path = os.path.join(WORKSPACE_DIR, 'sample_data', 'metadata.json')
        with open(samples_meta_path, 'r') as f:
            samples = json.load(f)

        for s in samples:
            if s.get('quality') == 'poor':
                continue
            expected_level = s['dr_level']
            img_path = os.path.join(WORKSPACE_DIR, 'sample_data', 'images', s['filename'])
            import base64
            with open(img_path, 'rb') as imf:
                b64 = "data:image/bmp;base64," + base64.b64encode(imf.read()).decode('utf-8')

            # Replicate frontend screening.js payload exactly
            payload = {
                "sample_id": s['id'],
                "image_base64": b64,
                "patient_meta": {
                    "patient_id": f"PT-{s['id']}",
                    "patient_name": "Test Patient",
                    "sample_hint": s['id'],
                    "filename": s['filename'],
                    "target_level": expected_level
                }
            }
            status, body, _ = simulate_request("POST", "/api/screen", payload)
            self.assertEqual(status, 200)
            res = json.loads(body.decode('utf-8'))
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["prediction"]["stage"], expected_level,
                             f"Sample {s['id']} expected stage {expected_level}, got {res['prediction']['stage']}")

    def test_feature_14_unhinted_raw_image_prediction(self):
        """Feature 14: Pure unhinted image inputs correctly classify without defaulting to Level 2."""
        cases = [
            ("sample_normal_level0.bmp", 0),
            ("sample_mild_level1.bmp", 1),
            ("sample_moderate_level2.bmp", 2),
            ("sample_severe_level3.bmp", 3),
            ("sample_pdr_level4.bmp", 4),
        ]
        import base64
        for fname, expected_stage in cases:
            img_path = os.path.join(WORKSPACE_DIR, 'sample_data', 'images', fname)
            with open(img_path, 'rb') as imf:
                b64 = base64.b64encode(imf.read()).decode('utf-8')

            # Payload with ZERO hint, zero sample_id, neutral name
            payload = {
                "image_base64": b64,
                "patient_meta": {
                    "patient_id": "PT-UNHINTED-99",
                    "patient_name": "Anonymous",
                    "patient_age": 55
                }
            }
            status, body, _ = simulate_request("POST", "/api/screen", payload)
            self.assertEqual(status, 200)
            res = json.loads(body.decode('utf-8'))
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["prediction"]["stage"], expected_stage,
                             f"Unhinted image {fname} expected stage {expected_stage}, got {res['prediction']['stage']}")


if __name__ == '__main__':
    unittest.main()
