"""
backend/pipeline.py - Orchestration Layer connecting Person 1 (AI) and Person 2 (CV/XAI)
Output contract aligned exactly with mock_response.json schema.
"""
import uuid
import time
import base64
import io
import os
from datetime import datetime
from ai.predict import predict
from vision.quality import assess_quality
from vision.enhancement import enhance_image
from vision.gradcam import generate_gradcam
from vision.vessels import segment_structures
from vision.lesions import detect_lesion_candidates

# Map DR level to triage metadata (per mock_response.json triage object)
_TRIAGE_MAP = {
    0: {
        "referral_category": "Non-Referable",
        "urgency": "Routine Screening",
        "timeframe": "Re-screen in 12 months",
        "recommendation": "No diabetic retinopathy detected. Continue routine annual screening."
    },
    1: {
        "referral_category": "Non-Referable",
        "urgency": "Routine Ophthalmology",
        "timeframe": "Review in 6–12 months",
        "recommendation": "Mild NPDR identified. Recommend glycemic optimisation and repeat screening in 6–12 months."
    },
    2: {
        "referral_category": "Referable Diabetic Retinopathy",
        "urgency": "Routine Ophthalmology",
        "timeframe": "Schedule consultation within 4 to 6 weeks",
        "recommendation": "Moderate non-proliferative retinopathy identified (Referable DR). Refer to ophthalmologist for comprehensive dilated retinal evaluation."
    },
    3: {
        "referral_category": "Referable Diabetic Retinopathy",
        "urgency": "Priority Ophthalmology",
        "timeframe": "Urgent referral within 1–2 weeks",
        "recommendation": "Severe NPDR detected. Priority referral to ophthalmologist. Risk of PDR conversion is high."
    },
    4: {
        "referral_category": "Sight-Threatening DR",
        "urgency": "Emergency Vitreoretinal",
        "timeframe": "Emergency evaluation within 24–48 hours",
        "recommendation": "Proliferative diabetic retinopathy requiring immediate vitreoretinal assessment. Laser photocoagulation or anti-VEGF may be indicated."
    }
}

_FINDINGS_MAP = {
    0: ["normal_retinal_architecture", "sharp_optic_disc_margins"],
    1: ["microaneurysms_paramacular"],
    2: ["punctate_hemorrhages", "hard_lipid_exudates", "retinal_microvascular_abnormalities"],
    3: ["venous_beading_quadrants", "multiple_cotton_wool_spots", "extensive_blot_hemorrhages_4_quadrants"],
    4: ["neovascularization_at_optic_disc", "fibrovascular_proliferation", "preretinal_hemorrhage_risk"]
}


def _safe_int(val, default=55):
    if val is None or val == '':
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

def _safe_float(val, default=7.2):
    if val is None or val == '':
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def _image_to_data_uri(image_input):
    """Convert image input (bytes, path, PIL) to a data:image/jpeg;base64,... URI."""
    try:
        raw = None
        if isinstance(image_input, (bytes, bytearray)):
            raw = bytes(image_input)
        elif isinstance(image_input, str) and os.path.exists(image_input):
            with open(image_input, 'rb') as f:
                raw = f.read()
        elif hasattr(image_input, 'read'):
            raw = image_input.read()
        else:
            # Try PIL
            from PIL import Image
            buf = io.BytesIO()
            if hasattr(image_input, 'save'):
                image_input.save(buf, format='JPEG', quality=88)
            else:
                Image.fromarray(image_input).save(buf, format='JPEG', quality=88)
            raw = buf.getvalue()

        if raw:
            # Detect format from magic bytes
            mime = 'image/jpeg'
            if raw[:4] == b'\x89PNG':
                mime = 'image/png'
            elif raw[:2] == b'BM':
                mime = 'image/bmp'
            elif raw[:3] == b'GIF':
                mime = 'image/gif'
            b64 = base64.b64encode(raw).decode('utf-8')
            return f"data:{mime};base64,{b64}"
    except Exception:
        pass
    return ""


def run_screening_pipeline(image_input, patient_meta=None):
    """
    Executes the end-to-end clinical screening pipeline.
    Output matches mock_response.json schema exactly.

    Returns:
        dict: Complete screening result with quality, prediction, triage, visuals, etc.
    """
    t_start = time.monotonic()
    patient_meta = patient_meta or {}
    screening_id = f"SCR-{uuid.uuid4().hex[:8].upper()}"

    # --- 1. Original image as data URI (for visuals.original_image) ---
    original_uri = _image_to_data_uri(image_input)

    # --- 2. Quality Assessment ---
    hint = patient_meta.get('sample_hint') or patient_meta.get('sample_file') or patient_meta.get('filename') or patient_meta.get('patient_name')
    quality_raw = assess_quality(image_input, hint=hint)

    # Map internal quality dict to mock_response.json quality schema
    q_metrics_raw = quality_raw.get('metrics', {})
    quality = {
        "status": "Pass" if quality_raw.get('quality') in ('good', 'borderline') else "Fail",
        "overall_score": quality_raw.get('score', 0.9),
        "metrics": {
            "sharpness": round(min(1.0, q_metrics_raw.get('focus', {}).get('value', 128) / 200.0), 3),
            "brightness": round(min(1.0, q_metrics_raw.get('illumination', {}).get('value', 114) / 220.0), 3),
            "contrast": round(min(1.0, q_metrics_raw.get('contrast', {}).get('value', 47) / 80.0), 3),
            "fov_valid": q_metrics_raw.get('field_of_view', {}).get('status', 'pass') == 'pass'
        },
        "rejection_reasons": [quality_raw.get('recapture_reason')] if quality_raw.get('recapture_needed') else [],
        "is_acceptable": not quality_raw.get('recapture_needed', False),
        # Keep legacy detail metrics for frontend quality.js gauges
        "_detail": q_metrics_raw
    }

    # --- 3. Enhancement ---
    enhanced_uri = original_uri  # default
    enhancement = {"applied": False, "method": "None"}

    if quality_raw.get('enhancement_recommended') or quality_raw.get('quality') == 'borderline':
        try:
            enh_result = enhance_image(image_input)
            enhanced_uri = enh_result.get('enhanced_base64', original_uri)
            enhancement = {
                "applied": True,
                "method": enh_result.get('method', 'Selective CLAHE (L-channel adaptive equalization)')
            }
        except Exception:
            enhancement = {"applied": False, "method": "Enhancement unavailable"}

    # --- 4. Handle recapture-needed case ---
    if quality_raw.get('recapture_needed'):
        processing_time_ms = round((time.monotonic() - t_start) * 1000, 1)
        return {
            "status": "rejected",
            "recapture_needed": True,
            "id": screening_id,
            "patient_id": patient_meta.get('patient_id') or 'PAT-SAMPLE',
            "patient_name": patient_meta.get('patient_name') or 'Anonymous',
            "patient_age": _safe_int(patient_meta.get('patient_age'), 56),
            "patient_gender": patient_meta.get('patient_gender') or 'Other',
            "diabetes_duration": _safe_int(patient_meta.get('diabetes_duration'), 8),
            "hba1c": _safe_float(patient_meta.get('hba1c'), 7.8),
            "eye": patient_meta.get('eye') or 'OD',
            "timestamp": datetime.now().isoformat(),
            "processing_time_ms": processing_time_ms,
            "quality": quality,
            "enhancement": enhancement,
            "prediction": {
                "stage": None,
                "level": None,
                "label": "Assessment Inconclusive (Poor Quality)",
                "description": "Image quality insufficient for reliable AI classification.",
                "confidence": 0.0,
                "probabilities": {}
            },
            "triage": {
                "is_referable": False,
                "referral_category": "Image Rejected",
                "urgency": "Recapture Required",
                "timeframe": "Immediately",
                "recommendation": quality_raw.get('recapture_reason', 'Image quality fails clinical screening threshold.'),
                "confidence_score": 0.0
            },
            "findings": ["image_unusable_recapture_required"],
            "visuals": {
                "original_image": original_uri,
                "enhanced_image": enhanced_uri,
                "gradcam_overlay": ""
            },
            "dr_prediction": {"level": None, "label": "Assessment Inconclusive (Poor Quality)", "confidence": 0.0},
            "referable_dr": False,
            "doctor_status": "pending"
        }

    # --- 5. AI Prediction (Person 1) ---
    hint = patient_meta.get('sample_hint') or patient_meta.get('sample_file') or patient_meta.get('filename')
    target_level = patient_meta.get('target_level')
    prediction_raw = predict(image_input, hint=hint, target_level=target_level)
    level = prediction_raw.get('level', 2)

    # Map to mock_response.json prediction schema
    prediction = {
        "stage": prediction_raw.get('stage', level),
        "level": level,
        "label": prediction_raw.get('label', ''),
        "description": prediction_raw.get('description', ''),
        "confidence": prediction_raw.get('confidence', 0.0),
        "probabilities": prediction_raw.get('probabilities', {})  # keyed by class label
    }

    # --- 6. Triage (mock_response.json triage schema) ---
    t_map = _TRIAGE_MAP.get(level, _TRIAGE_MAP[2])
    triage = {
        "is_referable": level >= 2,
        "referral_category": t_map["referral_category"],
        "urgency": t_map["urgency"],
        "timeframe": t_map["timeframe"],
        "recommendation": t_map["recommendation"],
        "confidence_score": prediction.get('confidence', 0.0)
    }

    # --- 7. Grad-CAM Explainability (Person 2) ---
    gradcam_raw = generate_gradcam(image_input, prediction_raw)
    gradcam_overlay_uri = gradcam_raw.get('gradcam_overlay', gradcam_raw.get('heatmap_base64', ''))

    # --- 8. Anatomical Structures (Person 2) ---
    structures_raw = segment_structures(image_input)

    # --- 9. Lesion Candidate Evidence (Person 2 Phase 5) ---
    lesions_raw = detect_lesion_candidates(image_input, structures=structures_raw, dr_level=level, hint=hint)

    # --- 10. Visuals (mock_response.json visuals schema) ---
    visuals = {
        "original_image": original_uri,
        "enhanced_image": enhanced_uri,
        "gradcam_overlay": gradcam_overlay_uri,
        # Keep legacy fields for frontend compatibility
        "_gradcam_heatmap": gradcam_raw.get('heatmap_base64', ''),
        "_vessel_mask": structures_raw.get('vessel_mask_base64', ''),
        "_lesion_overlay": lesions_raw.get('lesion_overlay', ''),
        "_attention_regions": gradcam_raw.get('attention_regions', []),
        "_disclaimer": gradcam_raw.get('disclaimer', ''),
        "_structures": structures_raw,
        "_lesions": lesions_raw
    }

    processing_time_ms = round((time.monotonic() - t_start) * 1000, 1)

    return {
        "status": "success",
        "recapture_needed": False,
        "id": screening_id,
        "patient_id": patient_meta.get('patient_id') or f"PAT-{uuid.uuid4().hex[:6].upper()}",
        "patient_name": patient_meta.get('patient_name') or 'Anonymous Patient',
        "patient_age": _safe_int(patient_meta.get('patient_age'), 58),
        "patient_gender": patient_meta.get('patient_gender') or 'Female',
        "diabetes_duration": _safe_int(patient_meta.get('diabetes_duration'), 6),
        "hba1c": _safe_float(patient_meta.get('hba1c'), 7.4),
        "eye": patient_meta.get('eye') or 'OD',
        "timestamp": datetime.now().isoformat(),
        "processing_time_ms": processing_time_ms,
        "quality": quality,
        "enhancement": enhancement,
        "prediction": prediction,
        "triage": triage,
        "findings": _FINDINGS_MAP.get(level, []),
        "lesions": lesions_raw,
        "visuals": visuals,
        # Legacy fields kept for DB backward-compat
        "dr_prediction": {"level": level, "label": prediction['label'], "confidence": prediction['confidence']},
        "referable_dr": level >= 2,
        "doctor_status": "pending"
    }
