"""
tests/test_unit.py - Comprehensive Unit Test Suite for RetinaAI Platform
Tests individual system components without requiring an external HTTP server.
Can be run via:
    python3 -m unittest tests/test_unit.py -v
    or
    python3 -m unittest discover -s tests -v
"""
import unittest
import os
import sys
import json
import base64

# Ensure workspace root is in sys.path
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from ai.predict import predict, DRPredictor
from ai.model import CLASS_NAMES
from vision.quality import assess_quality
from vision.enhancement import enhance_image
from vision.vessels import segment_structures
from vision.lesions import detect_lesion_candidates
from backend.database import (
    init_db, save_screening, get_screening_by_id,
    get_all_screenings, update_doctor_review, get_dashboard_stats,
    _safe_int, _safe_float
)
from backend.pipeline import run_screening_pipeline
from reports.report_generator import generate_report_html
from simulink.telemedicine_sim import run_simulation, get_all_scenarios_comparison, SCENARIOS


class TestQualityAssessment(unittest.TestCase):
    """Unit tests for Person 2 Image Quality Assessment (vision/quality.py)."""

    def setUp(self):
        self.sample_dir = os.path.join(WORKSPACE_DIR, 'sample_data', 'images')
        self.good_sample = os.path.join(self.sample_dir, 'sample_moderate_level2.bmp')
        self.blur_sample = os.path.join(self.sample_dir, 'sample_poor_quality_blur.bmp')

    def test_acceptable_image_quality(self):
        if os.path.exists(self.good_sample):
            with open(self.good_sample, 'rb') as f:
                img_bytes = f.read()
            res = assess_quality(img_bytes, hint="sample_moderate_level2")
            self.assertIn("quality", res)
            self.assertIn("score", res)
            self.assertIn("metrics", res)
            self.assertFalse(res["recapture_needed"])
            self.assertIn("focus", res["metrics"])
            self.assertIn("illumination", res["metrics"])
            self.assertIn("contrast", res["metrics"])
            self.assertIn("field_of_view", res["metrics"])
            self.assertEqual(res["recapture_reason"], "")

    def test_blur_image_quality_rejection(self):
        if os.path.exists(self.blur_sample):
            with open(self.blur_sample, 'rb') as f:
                img_bytes = f.read()
            res = assess_quality(img_bytes, hint="sample_poor_quality_blur")
            self.assertTrue(res["recapture_needed"])
            self.assertIn(res["quality"].lower(), ["poor", "borderline", "fail"])
            self.assertNotEqual(res["recapture_reason"], "")

    def test_quality_with_file_path(self):
        if os.path.exists(self.good_sample):
            res = assess_quality(self.good_sample)
            self.assertIsNotNone(res)
            self.assertIn("score", res)


class TestAIPrediction(unittest.TestCase):
    """Unit tests for Person 1 Diabetic Retinopathy classification engine (ai/predict.py)."""

    def setUp(self):
        self.predictor = DRPredictor()

    def test_predict_schema(self):
        pred = predict(b"dummy_bytes", hint="sample-002")
        self.assertIn("stage", pred)
        self.assertIn("label", pred)
        self.assertIn("confidence", pred)
        self.assertIn("probabilities", pred)
        self.assertIsInstance(pred["stage"], int)
        self.assertIn(pred["stage"], [0, 1, 2, 3, 4])
        self.assertIsInstance(pred["confidence"], float)
        self.assertGreaterEqual(pred["confidence"], 0.0)
        self.assertLessEqual(pred["confidence"], 1.0)

    def test_probability_distribution(self):
        pred = predict(b"dummy_bytes", hint="sample-001")
        probs = pred["probabilities"]
        self.assertEqual(len(probs), 5)
        for class_name in CLASS_NAMES.values():
            self.assertIn(class_name, probs)
        total_prob = sum(probs.values())
        self.assertAlmostEqual(total_prob, 1.0, places=2)

    def test_calibrated_hint_mapping(self):
        hints_to_expected = {
            "sample-000": 0,
            "sample-0": 0,
            "sample_normal": 0,
            "sample-001": 1,
            "sample-1": 1,
            "mild": 1,
            "sample-002": 2,
            "moderate": 2,
            "sample-003": 3,
            "severe": 3,
            "stage 3": 3,
            "sample-004": 4,
            "level_4": 4,
            "pdr": 4,
        }
        for hint, expected_stage in hints_to_expected.items():
            res = predict(b"fake_bytes", hint=hint)
            self.assertEqual(res["stage"], expected_stage, f"Failed for hint '{hint}': expected {expected_stage}, got {res['stage']}")


class TestEnhancementAndVision(unittest.TestCase):
    """Unit tests for image enhancement and retinal structure segmentation."""

    def setUp(self):
        self.sample_path = os.path.join(WORKSPACE_DIR, 'sample_data', 'images', 'sample_moderate_level2.bmp')

    def test_enhance_image(self):
        if os.path.exists(self.sample_path):
            with open(self.sample_path, 'rb') as f:
                img_bytes = f.read()
            res = enhance_image(img_bytes)
            self.assertIn("enhanced_base64", res)
            self.assertTrue(res["enhanced_base64"].startswith("data:image/"))
            self.assertIn("method", res)
            self.assertIn("contrast_gain", res)

    def test_segment_structures(self):
        structures = segment_structures(b"dummy_bytes")
        self.assertIn("optic_disc", structures)
        self.assertIn("fovea", structures)
        self.assertIn("vessel_mask_base64", structures)
        self.assertIn("data:image/svg+xml;base64,", structures["vessel_mask_base64"])
        self.assertIn("center", structures["optic_disc"])
        self.assertIn("radius", structures["optic_disc"])

    def test_detect_lesion_candidates(self):
        # Test normal eye (no lesions)
        normal_lesions = detect_lesion_candidates(b"dummy_bytes", dr_level=0, hint="sample_normal")
        self.assertEqual(normal_lesions["microaneurysms"]["count"], 0)
        self.assertEqual(normal_lesions["hemorrhages"]["count"], 0)
        self.assertEqual(normal_lesions["exudates"]["count"], 0)
        self.assertFalse(normal_lesions["neovascularization"]["detected"])
        self.assertIn("data:image/svg+xml;base64,", normal_lesions["lesion_overlay"])

        # Test moderate NPDR eye (MA + HE + EX)
        mod_lesions = detect_lesion_candidates(b"dummy_bytes", dr_level=2, hint="sample_moderate")
        self.assertGreater(mod_lesions["microaneurysms"]["count"], 0)
        self.assertGreater(mod_lesions["hemorrhages"]["count"], 0)
        self.assertGreater(mod_lesions["exudates"]["count"], 0)
        self.assertIn("macular_threat", mod_lesions["exudates"])

        # Test proliferative DR eye (NVD/NVE positive)
        pdr_lesions = detect_lesion_candidates(b"dummy_bytes", dr_level=4, hint="sample_pdr")
        self.assertTrue(pdr_lesions["neovascularization"]["detected"])
        self.assertGreater(pdr_lesions["total_lesions"], 10)


class TestDatabase(unittest.TestCase):
    """Unit tests for SQLite storage, retrieval, and audit trail (backend/database.py)."""

    def setUp(self):
        init_db()

    def test_safe_type_helpers(self):
        self.assertEqual(_safe_int(42, 55), 42)
        self.assertEqual(_safe_int("60", 55), 60)
        self.assertEqual(_safe_int("", 55), 55)
        self.assertEqual(_safe_int(None, 55), 55)
        self.assertEqual(_safe_int("invalid", 55), 55)

        self.assertEqual(_safe_float(7.8, 7.2), 7.8)
        self.assertEqual(_safe_float("8.5", 7.2), 8.5)
        self.assertEqual(_safe_float("", 7.2), 7.2)
        self.assertEqual(_safe_float(None, 7.2), 7.2)
        self.assertEqual(_safe_float("bad_float", 7.2), 7.2)

    def test_save_and_retrieve_screening(self):
        test_screening = {
            "id": "SCR-UNIT-TEST-001",
            "status": "success",
            "patient_id": "PT-UNIT-001",
            "patient_name": "Test Patient",
            "patient_age": 62,
            "patient_gender": "Female",
            "diabetes_duration": 10,
            "hba1c": 8.2,
            "eye": "OS",
            "timestamp": "2026-09-05T12:00:00",
            "processing_time_ms": 115.0,
            "quality": {
                "status": "Pass",
                "overall_score": 0.92,
                "metrics": {"sharpness": 0.91, "brightness": 0.88, "contrast": 0.89, "fov_valid": True},
                "rejection_reasons": [],
                "is_acceptable": True
            },
            "prediction": {
                "stage": 2,
                "label": "Moderate NPDR",
                "confidence": 0.85,
                "probabilities": {"No DR": 0.02, "Mild NPDR": 0.08, "Moderate NPDR": 0.85, "Severe NPDR": 0.03, "Proliferative DR": 0.02}
            },
            "triage": {
                "is_referable": True,
                "referral_category": "Referable Diabetic Retinopathy",
                "urgency": "Routine Ophthalmology",
                "timeframe": "4-6 weeks",
                "recommendation": "Consult specialist"
            },
            "visuals": {
                "original_image": "data:image/jpeg;base64,abc",
                "enhanced_image": "data:image/jpeg;base64,def",
                "gradcam_overlay": "data:image/jpeg;base64,ghi",
                "_attention_regions": [{"region": "superior_temporal", "weight": 0.85}],
                "_structures": {"vessel_mask_base64": "data:image/svg+xml;base64,jkl"}
            }
        }
        saved_id = save_screening(test_screening)
        self.assertEqual(saved_id, test_screening["id"])

        retrieved = get_screening_by_id(saved_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["id"], saved_id)
        self.assertEqual(retrieved["patient_name"], "Test Patient")
        self.assertEqual(retrieved["prediction"]["stage"], 2)
        self.assertTrue(retrieved["triage"]["is_referable"])

        # Check deserialized private visuals
        self.assertIn("_attention_regions", retrieved["visuals"])
        self.assertEqual(len(retrieved["visuals"]["_attention_regions"]), 1)
        self.assertIn("_vessel_mask", retrieved["visuals"])

    def test_update_doctor_review(self):
        review_update = {
            "doctor_status": "accepted",
            "doctor_dr_level": 2,
            "doctor_referral_action": "Refer within 2 weeks",
            "doctor_notes": "Unit test verified notes.",
            "doctor_name": "Dr. Unit Reviewer, MD"
        }
        ok = update_doctor_review("SCR-UNIT-TEST-001", review_update)
        self.assertTrue(ok)

        updated = get_screening_by_id("SCR-UNIT-TEST-001")
        self.assertEqual(updated["doctor_status"], "accepted")
        self.assertEqual(updated["doctor_dr_level"], 2)
        self.assertEqual(updated["doctor_notes"], "Unit test verified notes.")

    def test_nonexistent_screening(self):
        result = get_screening_by_id("SCR-DOES-NOT-EXIST-404")
        self.assertIsNone(result)

    def test_dashboard_stats(self):
        stats = get_dashboard_stats()
        self.assertIn("total_screenings", stats)
        self.assertIn("referable_cases", stats)
        self.assertIn("reviewed_cases", stats)
        self.assertIn("pending_review", stats)
        self.assertGreaterEqual(stats["total_screenings"], 1)


class TestPipeline(unittest.TestCase):
    """Unit tests for the end-to-end screening orchestration pipeline (backend/pipeline.py)."""

    def setUp(self):
        self.sample_path = os.path.join(WORKSPACE_DIR, 'sample_data', 'images', 'sample_moderate_level2.bmp')
        self.blur_path = os.path.join(WORKSPACE_DIR, 'sample_data', 'images', 'sample_poor_quality_blur.bmp')

    def test_pipeline_normal_execution(self):
        if os.path.exists(self.sample_path):
            with open(self.sample_path, 'rb') as f:
                img_bytes = f.read()

            meta = {
                "patient_id": "PT-PIPE-001",
                "patient_name": "Saraswathi Ammal",
                "patient_age": 64,
                "patient_gender": "Female",
                "diabetes_duration": 12,
                "hba1c": 8.4,
                "eye": "OD",
                "sample_hint": "sample_moderate_level2"
            }
            res = run_screening_pipeline(img_bytes, meta)
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["patient_id"], "PT-PIPE-001")
            self.assertIn("processing_time_ms", res)
            self.assertIn("quality", res)
            self.assertIn("prediction", res)
            self.assertIn("triage", res)
            self.assertIn("visuals", res)
            self.assertEqual(res["prediction"]["stage"], 2)
            self.assertTrue(res["triage"]["is_referable"])

    def test_pipeline_safe_type_fallbacks(self):
        if os.path.exists(self.sample_path):
            with open(self.sample_path, 'rb') as f:
                img_bytes = f.read()

            malformed_meta = {
                "patient_id": "",
                "patient_name": "",
                "patient_age": "",          # empty string -> defaults to 58
                "diabetes_duration": None,   # None -> defaults to 6
                "hba1c": "invalid_number",   # invalid string -> defaults to 7.4
                "eye": "",                   # empty -> defaults to OD
                "sample_hint": "sample-002"
            }
            res = run_screening_pipeline(img_bytes, malformed_meta)
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["patient_age"], 58)
            self.assertEqual(res["diabetes_duration"], 6)
            self.assertEqual(res["hba1c"], 7.4)
            self.assertEqual(res["eye"], "OD")

    def test_pipeline_quality_rejection_flow(self):
        if os.path.exists(self.blur_path):
            with open(self.blur_path, 'rb') as f:
                img_bytes = f.read()

            res = run_screening_pipeline(img_bytes, {"sample_hint": "sample_poor_quality_blur"})
            self.assertEqual(res["status"], "rejected")
            self.assertFalse(res["quality"]["is_acceptable"])
            self.assertGreater(len(res["quality"]["rejection_reasons"]), 0)
            self.assertEqual(res["triage"]["urgency"], "Recapture Required")


class TestReportGenerator(unittest.TestCase):
    """Unit tests for clinical HTML report generation and score formatting (reports/report_generator.py)."""

    def test_report_generation_and_score_normalization(self):
        screening = {
            "id": "SCR-REPORT-001",
            "patient_id": "PT-REPORT-001",
            "patient_name": "Ramesh Kumar",
            "patient_age": 55,
            "patient_gender": "Male",
            "diabetes_duration": 8,
            "hba1c": 7.9,
            "eye": "OD",
            "timestamp": "2026-09-05T14:30:00",
            "quality": {
                "status": "Pass",
                "overall_score": 98.5,  # Percentage input
                "metrics": {"sharpness": 0.94, "brightness": 0.92, "contrast": 0.89, "fov_valid": True}
            },
            "prediction": {
                "stage": 2,
                "label": "Moderate NPDR",
                "confidence": 0.88,    # Fraction input (0.88 -> 88%)
                "probabilities": {"No DR": 0.01, "Mild NPDR": 0.05, "Moderate NPDR": 0.88, "Severe NPDR": 0.04, "Proliferative DR": 0.02}
            },
            "triage": {
                "is_referable": True,
                "referral_category": "Referable Diabetic Retinopathy",
                "urgency": "Routine Ophthalmology",
                "timeframe": "Schedule consultation within 4 to 6 weeks",
                "recommendation": "Moderate non-proliferative retinopathy identified."
            },
            "enhancement": {"applied": True, "method": "CLAHE"},
            "visuals": {
                "original_image": "data:image/jpeg;base64,xyz",
                "enhanced_image": "data:image/jpeg;base64,xyz",
                "gradcam_overlay": "data:image/jpeg;base64,xyz"
            },
            "doctor_status": "accepted",
            "doctor_dr_level": 2,
            "doctor_referral_action": "Refer to Vitreoretinal Specialist",
            "doctor_notes": "Blot hemorrhages confirmed.",
            "doctor_name": "Dr. S. Ramanathan, MD",
            "doctor_reviewed_at": "2026-09-05T14:45:00"
        }

        html = generate_report_html(screening)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("RetinaAI Screening Report", html)
        self.assertIn("PT-REPORT-001", html)
        self.assertIn("Ramesh Kumar", html)
        self.assertIn("Moderate NPDR", html)
        self.assertIn("98%", html, "Quality score should be formatted as 98%")
        self.assertIn("88%", html, "Confidence should be formatted as 88%")
        self.assertNotIn("9850%", html, "Bug test: quality score should not be multiplied by 100 twice")
        self.assertIn("Dr. S. Ramanathan, MD", html)
        self.assertIn("Blot hemorrhages confirmed.", html)


class TestTelemedicineSimulation(unittest.TestCase):
    """Unit tests for Telemedicine Queuing Simulation (simulink/telemedicine_sim.py)."""

    def test_scenario_a_execution(self):
        sim = run_simulation("scenario_a")
        self.assertEqual(sim["scenario_id"], "scenario_a")
        self.assertIn("results", sim)
        r = sim["results"]
        self.assertEqual(r["total_throughput_annual"], 100000)
        self.assertIn("doctor_utilization_pct", r)
        self.assertIn("ai_server_utilization_pct", r)
        self.assertIn("bottleneck_stage", r)
        self.assertIn("is_stable", r)

    def test_all_scenarios_comparison(self):
        comp = get_all_scenarios_comparison()
        self.assertEqual(len(comp), 4)
        for sc_key in ["scenario_a", "scenario_b", "scenario_c", "scenario_d"]:
            self.assertIn(sc_key, comp)
            self.assertIn("results", comp[sc_key])
            self.assertIn("parameters", comp[sc_key])

    def test_custom_overrides(self):
        overrides = {
            "annual_patients": 120000,
            "doctor_count": 5
        }
        sim = run_simulation("scenario_a", custom_overrides=overrides)
        self.assertEqual(sim["parameters"]["annual_patients"], 120000)
        self.assertEqual(sim["parameters"]["doctor_count"], 5)
        self.assertEqual(sim["results"]["total_throughput_annual"], 120000)


if __name__ == '__main__':
    unittest.main()
