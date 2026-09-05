"""
backend/database.py - Thread-safe SQLite screening store and audit trail
Schema updated to support mock_response.json contract fields.
"""
import sqlite3
import json
import os
import threading
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'retina_screenings.db')
_lock = threading.Lock()

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

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _lock:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS screenings (
            id TEXT PRIMARY KEY,
            status TEXT DEFAULT 'success',
            patient_id TEXT NOT NULL,
            patient_name TEXT,
            patient_age INTEGER,
            patient_gender TEXT,
            diabetes_duration INTEGER,
            hba1c REAL,
            eye TEXT,
            timestamp TEXT NOT NULL,
            processing_time_ms REAL,
            -- Quality fields (new schema: quality.*)
            quality_status TEXT,
            quality_score REAL,
            quality_json TEXT,          -- Full quality object as JSON
            -- Prediction fields (new schema: prediction.*)
            dr_level INTEGER,           -- prediction.stage / level
            dr_label TEXT,              -- prediction.label
            confidence REAL,            -- prediction.confidence
            probabilities TEXT,         -- prediction.probabilities JSON
            referable INTEGER,          -- triage.is_referable
            -- Triage (new schema: triage.*)
            triage_json TEXT,
            -- Findings
            findings TEXT,
            -- Visuals (new schema: visuals.*)
            visuals_json TEXT,
            -- Enhancement
            enhancement_json TEXT,
            -- Doctor review
            doctor_status TEXT DEFAULT 'pending',
            doctor_dr_level INTEGER,
            doctor_referral_action TEXT,
            doctor_notes TEXT,
            doctor_name TEXT,
            doctor_review_time TEXT,
            -- Legacy columns for backward compat (kept to avoid migrating existing rows)
            image_quality_status TEXT,
            image_quality_score REAL,
            quality_details TEXT,
            scores TEXT,
            gradcam_data TEXT,
            vessel_data TEXT
        )
        """)
        # Migration: add new columns if they don't exist yet (for existing DBs)
        existing_cols = {row[1] for row in cursor.execute("PRAGMA table_info(screenings)").fetchall()}
        new_cols = [
            ("status", "TEXT DEFAULT 'success'"),
            ("processing_time_ms", "REAL"),
            ("quality_status", "TEXT"),
            ("quality_score", "REAL"),
            ("quality_json", "TEXT"),
            ("probabilities", "TEXT"),
            ("triage_json", "TEXT"),
            ("visuals_json", "TEXT"),
            ("enhancement_json", "TEXT"),
        ]
        for col_name, col_type in new_cols:
            if col_name not in existing_cols:
                cursor.execute(f"ALTER TABLE screenings ADD COLUMN {col_name} {col_type}")
        conn.commit()
        conn.close()

init_db()

def save_screening(data):
    """Save a full pipeline result dict to the database."""
    quality = data.get('quality') or {}
    prediction = data.get('prediction') or data.get('dr_prediction') or {}
    triage = data.get('triage') or {}
    visuals = data.get('visuals') or {}
    enhancement = data.get('enhancement') or {}

    # Resolve level from new or legacy field
    level = prediction.get('stage', prediction.get('level', data.get('dr_prediction', {}).get('level', 0)))
    label = prediction.get('label', data.get('dr_prediction', {}).get('label', 'No DR'))
    conf = prediction.get('confidence', data.get('dr_prediction', {}).get('confidence', 0.9))
    is_referable = triage.get('is_referable', data.get('referable_dr', False))

    with _lock:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO screenings (
            id, status, patient_id, patient_name, patient_age, patient_gender,
            diabetes_duration, hba1c, eye, timestamp, processing_time_ms,
            quality_status, quality_score, quality_json,
            dr_level, dr_label, confidence, probabilities, referable,
            triage_json, findings, visuals_json, enhancement_json,
            doctor_status, doctor_dr_level, doctor_referral_action,
            doctor_notes, doctor_name, doctor_review_time,
            image_quality_status, image_quality_score, quality_details,
            scores, gradcam_data, vessel_data
        ) VALUES (
            ?, ?, ?, ?, ?,  ?, ?, ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?,  ?, ?, ?,
            ?, ?, ?,  ?, ?, ?
        )
        """, (
            data.get('id'),
            data.get('status', 'success'),
            data.get('patient_id') or 'UNKNOWN',
            data.get('patient_name') or 'Anonymous Patient',
            _safe_int(data.get('patient_age'), 55),
            data.get('patient_gender') or 'Unspecified',
            _safe_int(data.get('diabetes_duration'), 5),
            _safe_float(data.get('hba1c'), 7.5),
            data.get('eye') or 'OD',
            data.get('timestamp', datetime.now().isoformat()),
            _safe_float(data.get('processing_time_ms'), 0.0),
            # New quality fields
            quality.get('status', 'Pass'),
            quality.get('overall_score', 0.9),
            json.dumps(quality),
            # Prediction fields
            level, label, conf,
            json.dumps(prediction.get('probabilities', {})),
            1 if is_referable else 0,
            # Triage + findings + visuals + enhancement
            json.dumps(triage),
            json.dumps(data.get('findings', [])),
            json.dumps({k: v for k, v in visuals.items() if not k.startswith('_')}),  # strip private keys with large base64
            json.dumps(enhancement),
            # Doctor review
            data.get('doctor_status', 'pending'),
            data.get('doctor_dr_level'),
            data.get('doctor_referral_action', 'Pending Review'),
            data.get('doctor_notes', ''),
            data.get('doctor_name', ''),
            data.get('doctor_review_time', ''),
            # Legacy compat columns
            quality.get('status', 'Pass'),
            quality.get('overall_score', 0.9),
            json.dumps(quality.get('_detail', {})),
            json.dumps(prediction.get('probabilities', {})),
            json.dumps(visuals.get('_attention_regions', [])),
            json.dumps(visuals.get('_structures', {}))
        ))
        conn.commit()
        conn.close()
        return data.get('id')

def update_doctor_review(screening_id, review_data):
    with _lock:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE screenings SET
            doctor_status = ?,
            doctor_dr_level = ?,
            doctor_referral_action = ?,
            doctor_notes = ?,
            doctor_name = ?,
            doctor_review_time = ?
        WHERE id = ?
        """, (
            review_data.get('doctor_status', 'accepted'),
            review_data.get('doctor_dr_level'),
            review_data.get('doctor_referral_action', 'routine'),
            review_data.get('doctor_notes', ''),
            review_data.get('doctor_name', 'Dr. Ophthalmologist'),
            datetime.now().isoformat(),
            screening_id
        ))
        conn.commit()
        conn.close()
        return True

def get_screening_by_id(screening_id):
    with _lock:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM screenings WHERE id = ?", (screening_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return _row_to_dict(row)

def get_all_screenings(limit=100):
    with _lock:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM screenings ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [_row_to_dict(row) for row in rows]

def get_dashboard_stats():
    with _lock:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM screenings")
        total = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as referable FROM screenings WHERE referable = 1")
        referable = cursor.fetchone()['referable']

        cursor.execute("SELECT COUNT(*) as pending FROM screenings WHERE doctor_status = 'pending'")
        pending = cursor.fetchone()['pending']

        cursor.execute("SELECT COUNT(*) as reviewed FROM screenings WHERE doctor_status != 'pending'")
        reviewed = cursor.fetchone()['reviewed']

        conn.close()
        return {
            "total_screenings": total,
            "referable_cases": referable,
            "pending_review": pending,
            "reviewed_cases": reviewed,
            "referable_percentage": round((referable / total * 100) if total > 0 else 0, 1),
            "avg_review_seconds": 24.8
        }

def _row_to_dict(row):
    """Convert a SQLite row to a full dict matching the mock_response.json schema."""
    d = dict(row)

    # Parse JSON columns
    for col in ('quality_json', 'triage_json', 'visuals_json', 'enhancement_json',
                'probabilities', 'findings', 'gradcam_data', 'vessel_data',
                'quality_details', 'scores'):
        if col in d and d[col]:
            try:
                d[col] = json.loads(d[col])
            except Exception:
                pass

    # Build mock_response.json compatible top-level structure
    quality_obj = d.get('quality_json') or {}
    if not quality_obj:
        # Reconstruct from legacy columns for old rows
        quality_obj = {
            "status": d.get('image_quality_status') or d.get('quality_status', 'Pass'),
            "overall_score": d.get('image_quality_score') or d.get('quality_score', 0.9),
            "metrics": {},
            "rejection_reasons": [],
            "is_acceptable": True
        }

    triage_obj = d.get('triage_json') or {
        "is_referable": bool(d.get('referable')),
        "referral_category": "Referable Diabetic Retinopathy" if d.get('referable') else "Non-Referable",
        "urgency": "Routine Ophthalmology",
        "timeframe": "Schedule within 4–6 weeks",
        "recommendation": "",
        "confidence_score": d.get('confidence', 0.0)
    }

    prediction_obj = {
        "stage": d.get('dr_level', 0),
        "level": d.get('dr_level', 0),
        "label": d.get('dr_label', 'No DR'),
        "confidence": d.get('confidence', 0.0),
        "probabilities": d.get('probabilities') or {}
    }

    visuals_obj = d.get('visuals_json') or {}
    if not isinstance(visuals_obj, dict):
        visuals_obj = {}

    # Restore attention regions from gradcam_data if stripped in visuals_json
    if '_attention_regions' not in visuals_obj and d.get('gradcam_data'):
        visuals_obj['_attention_regions'] = d.get('gradcam_data')

    # Restore vessel mask from vessel_data if stripped in visuals_json
    if '_vessel_mask' not in visuals_obj and d.get('vessel_data'):
        structures = d.get('vessel_data')
        if isinstance(structures, dict):
            visuals_obj['_vessel_mask'] = structures.get('vessel_mask_base64', '')
            visuals_obj['_structures'] = structures

    enhancement_obj = d.get('enhancement_json') or {"applied": False, "method": "None"}

    # Resolve status & recapture
    is_acceptable = quality_obj.get('is_acceptable')
    if is_acceptable is None:
        is_acceptable = quality_obj.get('status', '').lower() in ('pass', 'good', 'borderline')

    status_val = d.get('status')
    if not status_val:
        status_val = "rejected" if (d.get('quality_status') == 'Fail' or not is_acceptable) else "success"

    recapture_needed = not is_acceptable if quality_obj else (status_val == 'rejected')

    # Build canonical response dict
    result = {
        "id": d.get('id'),
        "status": status_val,
        "recapture_needed": recapture_needed,
        "patient_id": d.get('patient_id'),
        "patient_name": d.get('patient_name'),
        "patient_age": d.get('patient_age'),
        "patient_gender": d.get('patient_gender'),
        "diabetes_duration": d.get('diabetes_duration'),
        "hba1c": d.get('hba1c'),
        "eye": d.get('eye'),
        "timestamp": d.get('timestamp'),
        "processing_time_ms": d.get('processing_time_ms', 0.0),
        "quality": quality_obj,
        "prediction": prediction_obj,
        "triage": triage_obj,
        "enhancement": enhancement_obj,
        "findings": d.get('findings') or [],
        "visuals": visuals_obj,
        "referable_dr": bool(d.get('referable')),
        # Legacy fields for backward compat with frontend components not yet updated
        "dr_prediction": {
            "level": d.get('dr_level', 0),
            "label": d.get('dr_label', 'No DR'),
            "confidence": d.get('confidence', 0.0),
            "scores": d.get('scores') or {}
        },
        "image_quality": {
            "status": quality_obj.get('status', 'Pass'),
            "score": quality_obj.get('overall_score', 0.9),
            "metrics": quality_obj.get('_detail', {}) or {}
        },
        "doctor_status": d.get('doctor_status', 'pending'),
        "doctor_dr_level": d.get('doctor_dr_level'),
        "doctor_referral_action": d.get('doctor_referral_action'),
        "doctor_notes": d.get('doctor_notes'),
        "doctor_name": d.get('doctor_name'),
        "doctor_review_time": d.get('doctor_review_time'),
    }
    return result
