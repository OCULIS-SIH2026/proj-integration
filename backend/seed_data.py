"""
backend/seed_data.py - Seeds initial clinical screenings for demo presentation
"""
import os
import random
from datetime import datetime, timedelta
from backend.database import save_screening, init_db
from backend.pipeline import run_screening_pipeline

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'sample_data')

def seed():
    init_db()
    patients = [
        {"id": "PAT-8041", "name": "Rajesh Sharma", "age": 62, "gender": "Male", "duration": 12, "hba1c": 8.6, "eye": "OD", "file": "sample_moderate_level2.bmp"},
        {"id": "PAT-7922", "name": "Sunita Verma", "age": 54, "gender": "Female", "duration": 6, "hba1c": 7.1, "eye": "OS", "file": "sample_normal_level0.bmp"},
        {"id": "PAT-6519", "name": "Mohammed Farooq", "age": 68, "gender": "Male", "duration": 18, "hba1c": 9.4, "eye": "OD", "file": "sample_severe_level3.bmp"},
        {"id": "PAT-4180", "name": "Ananya Mukherjee", "age": 47, "gender": "Female", "duration": 4, "hba1c": 6.8, "eye": "OD", "file": "sample_mild_level1.bmp"},
        {"id": "PAT-9203", "name": "Harpreet Singh", "age": 71, "gender": "Male", "duration": 22, "hba1c": 10.2, "eye": "OS", "file": "sample_pdr_level4.bmp"},
        {"id": "PAT-3315", "name": "Kavita Nair", "age": 59, "gender": "Female", "duration": 9, "hba1c": 7.9, "eye": "OD", "file": "sample_moderate_level2.bmp"},
        {"id": "PAT-1194", "name": "Balaram Das", "age": 65, "gender": "Male", "duration": 14, "hba1c": 8.9, "eye": "OS", "file": "sample_moderate_level2.bmp"}
    ]

    print("Seeding demo clinical screenings...")
    for idx, p in enumerate(patients):
        img_path = os.path.join(SAMPLES_DIR, 'images', p['file'])
        if os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                img_data = f.read()

            time_offset = timedelta(hours=(len(patients) - idx) * 1.5)
            past_time = (datetime.now() - time_offset).isoformat()

            meta = {
                'patient_id': p['id'],
                'patient_name': p['name'],
                'patient_age': p['age'],
                'patient_gender': p['gender'],
                'diabetes_duration': p['duration'],
                'hba1c': p['hba1c'],
                'eye': p['eye'],
                'sample_file': p['file']
            }

            res = run_screening_pipeline(img_data, meta)
            res['timestamp'] = past_time

            # Pre-validate some cases so we have reviewed and pending statuses
            if idx in (0, 2):
                res['doctor_status'] = 'accepted'
                res['doctor_dr_level'] = res['dr_prediction']['level']
                res['doctor_referral_action'] = 'Urgent vitreoretinal referral within 2 weeks'
                res['doctor_notes'] = 'Multiple blot hemorrhages and hard exudates confirmed. Patient advised strict glycemic control and retinal evaluation.'
                res['doctor_name'] = 'Dr. S. Ramanathan, MD'
                res['doctor_review_time'] = (datetime.now() - time_offset + timedelta(minutes=15)).isoformat()
            elif idx == 1:
                res['doctor_status'] = 'accepted'
                res['doctor_dr_level'] = 0
                res['doctor_referral_action'] = 'Routine annual screening'
                res['doctor_notes'] = 'Clear fundus. No diabetic retinopathy visible. Re-screen in 12 months.'
                res['doctor_name'] = 'Dr. Priya Desai, DO'
                res['doctor_review_time'] = (datetime.now() - time_offset + timedelta(minutes=8)).isoformat()

            save_screening(res)
            print(f"Seeded: {p['name']} ({p['id']}) - {res['dr_prediction']['label']}")

    print("Seeding complete.")

if __name__ == '__main__':
    seed()
