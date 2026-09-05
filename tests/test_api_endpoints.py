"""
tests/test_api_endpoints.py - Automated Integration Test Suite
"""
import urllib.request
import json
import os

BASE_URL = 'http://localhost:8000'

def test_health_get():
    req = urllib.request.Request(f'{BASE_URL}/api/health')
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode('utf-8'))
        assert data['status'] == 'healthy'
        assert data['cdsco_compliant'] is True
        print(f"✓ GET /api/health: {data['service']} v{data['version']} is operational.")

def test_screenings_get():
    req = urllib.request.Request(f'{BASE_URL}/api/screenings')
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode('utf-8'))
        assert 'stats' in data
        assert 'screenings' in data
        print(f"✓ GET /api/screenings: {len(data['screenings'])} screenings retrieved.")

def test_sample_screening_post():
    payload = {
        "sample_id": "sample_level2_moderate",
        "patient_meta": {
            "patient_id": "TEST-INT-01",
            "patient_name": "Deepa Sundaram",
            "patient_age": 60,
            "patient_gender": "Female",
            "diabetes_duration": 11,
            "hba1c": 8.1,
            "eye": "OD",
            "sample_hint": "moderate"
        }
    }
    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(f'{BASE_URL}/api/screen', data=body, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        res = json.loads(resp.read().decode('utf-8'))
        assert res['patient_id'] == 'TEST-INT-01'
        assert res['prediction']['stage'] == 2
        assert res['triage']['is_referable'] is True
        print(f"✓ POST /api/screen: Screening {res['id']} created for Stage {res['prediction']['stage']} ({res['prediction']['label']}).")
        return res['id']

def test_doctor_review_post(screening_id):
    payload = {
        "screening_id": screening_id,
        "doctor_status": "accepted",
        "doctor_dr_level": 2,
        "doctor_referral_action": "Urgent referral to ophthalmologist within 2 weeks",
        "doctor_notes": "Automated integration test validation: Blot hemorrhages and microvascular changes confirmed.",
        "doctor_name": "Dr. Test Reviewer, MD"
    }
    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(f'{BASE_URL}/api/review', data=body, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        res = json.loads(resp.read().decode('utf-8'))
        assert res['success'] is True
        assert res['screening']['doctor_status'] == 'accepted'
        print(f"✓ POST /api/review: Doctor validation recorded for {screening_id}.")

def test_simulation_post():
    payload = {"scenario": "scenario_c", "overrides": {}}
    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(f'{BASE_URL}/api/simulate', data=body, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        res = json.loads(resp.read().decode('utf-8'))
        assert res['scenario_key'] == 'scenario_c'
        print(f"✓ POST /api/simulate: Simulated throughput = {res['results']['total_throughput_annual']} pts/yr.")

if __name__ == '__main__':
    print("Running integration tests against localhost:8000 ...")
    test_health_get()
    test_screenings_get()
    s_id = test_sample_screening_post()
    test_doctor_review_post(s_id)
    test_simulation_post()
    print("All integration tests PASSED successfully!")
