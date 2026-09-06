"""
backend/api.py - High-Performance Native Python REST API Server & Frontend Host (Person 3)
Serves REST endpoints for AI screening, quality assessment, doctor reviews,
report generation, and Telemedicine Simulink queuing simulation.
"""
import http.server
import socketserver
import json
import os
import sys
import base64
import re
import urllib.parse
from datetime import datetime

from backend.pipeline import run_screening_pipeline
from backend.database import save_screening, get_screening_by_id, get_all_screenings, update_doctor_review, get_dashboard_stats
from reports.report_generator import generate_report_html
from simulink.telemedicine_sim import run_simulation, get_all_scenarios_comparison, SCENARIOS

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'sample_data')

def _safe_int(val, default=55):
    """Safely converts input to int, falling back to default on empty or invalid input."""
    if val is None or val == '':
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

def _safe_float(val, default=7.2):
    """Safely converts input to float, falling back to default on empty or invalid input."""
    if val is None or val == '':
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def _parse_multipart(rfile, content_type, content_length):
    """
    Pure-stdlib multipart/form-data parser (replaces deprecated cgi.FieldStorage).
    Returns dict of {field_name: value_str_or_bytes}. File fields are bytes, text fields are str.
    """
    # Extract boundary from Content-Type header
    match = re.search(r'boundary=([^\s;]+)', content_type)
    if not match:
        return {}
    boundary = match.group(1).encode('utf-8')

    raw_body = rfile.read(content_length)
    delimiter = b'--' + boundary
    parts = raw_body.split(delimiter)

    fields = {}
    for part in parts:
        # Skip preamble, epilogue, and closing delimiter
        if not part or part.strip() in (b'', b'--', b'--\r\n'):
            continue

        # Split headers from body (separated by \r\n\r\n)
        if b'\r\n\r\n' in part:
            header_block, body = part.split(b'\r\n\r\n', 1)
        elif b'\n\n' in part:
            header_block, body = part.split(b'\n\n', 1)
        else:
            continue

        # Strip trailing \r\n from body
        if body.endswith(b'\r\n'):
            body = body[:-2]
        elif body.endswith(b'\n'):
            body = body[:-1]

        headers_text = header_block.decode('utf-8', errors='replace')

        # Extract field name
        name_match = re.search(r'name="([^"]+)"', headers_text)
        if not name_match:
            continue
        field_name = name_match.group(1)

        # Check if it's a file upload (has filename= in Content-Disposition)
        fn_match = re.search(r'filename="([^"]+)"', headers_text)
        is_file = bool(fn_match) or ('filename="' in headers_text)

        if is_file:
            fields[field_name] = body  # Keep as bytes
            if fn_match:
                fields[f'{field_name}_filename'] = fn_match.group(1)
        else:
            fields[field_name] = body.decode('utf-8', errors='replace')

    return fields

class RetinaAPIHandler(http.server.SimpleHTTPRequestHandler):
    """
    Handles API requests (/api/...) and serves static dashboard files.
    """
    # Ensure correct MIME types across platforms
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        '.js': 'application/javascript',
        '.mjs': 'application/javascript',
        '.css': 'text/css',
        '.json': 'application/json',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.bmp': 'image/bmp',
        '.wasm': 'application/wasm'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html_str, status=200):
        body = html_str.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 0. API: Health Check
        if path == '/api/health':
            self._send_json({
                "status": "healthy",
                "service": "OculisAI Tele-Ophthalmology Engine",
                "version": "2.4.0",
                "cdsco_compliant": True,
                "timestamp": datetime.now().isoformat()
            })
            return

        # 1. API: List Screenings & KPIs
        elif path == '/api/screenings':
            screenings = get_all_screenings(limit=50)
            stats = get_dashboard_stats()
            self._send_json({"stats": stats, "screenings": screenings})
            return

        # 2. API: Single Screening detail
        elif path.startswith('/api/screenings/'):
            s_id = path.replace('/api/screenings/', '').strip()
            item = get_screening_by_id(s_id)
            if item:
                self._send_json(item)
            else:
                self._send_json({"error": "Screening not found"}, 404)
            return

        # 3. API: Render Clinical Report HTML
        elif path.startswith('/api/report/'):
            s_id = path.replace('/api/report/', '').strip()
            item = get_screening_by_id(s_id)
            if item:
                html = generate_report_html(item)
                self._send_html(html)
            else:
                err_html = f"""<!DOCTYPE html><html><body style="font-family:sans-serif;text-align:center;padding:48px;color:#78716C;">
                <h2 style="color:#C2410C;">Report Not Found</h2>
                <p>No clinical report exists for Screening ID <code>{s_id}</code>.</p>
                </body></html>"""
                self._send_html(err_html, 404)
            return

        # 4. API: Telemedicine simulation comparison
        elif path == '/api/simulate/comparison':
            data = get_all_scenarios_comparison()
            self._send_json(data)
            return

        # 5. API: Preloaded sample fundus images
        elif path == '/api/samples':
            meta_path = os.path.join(SAMPLES_DIR, 'metadata.json')
            samples = []
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    samples_meta = json.load(f)

                for item in samples_meta:
                    img_path = os.path.join(SAMPLES_DIR, 'images', item['filename'])
                    img_b64 = ""
                    if os.path.exists(img_path):
                        with open(img_path, 'rb') as img_f:
                            img_b64 = "data:image/bmp;base64," + base64.b64encode(img_f.read()).decode('utf-8')
                    samples.append({
                        **item,
                        "image_data": img_b64
                    })
            self._send_json(samples)
            return

        # 6. Favicon
        elif path == '/favicon.ico':
            svg_icon = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="46" fill="#C2410C"/><circle cx="50" cy="50" r="20" fill="#FFF"/><circle cx="50" cy="50" r="10" fill="#C2410C"/></svg>'
            self.send_response(200)
            self.send_header('Content-Type', 'image/svg+xml')
            self.send_header('Content-Length', str(len(svg_icon)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(svg_icon)
            return

        # 7. Fallback: serve static frontend files
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        content_type = self.headers.get('Content-Type', '')

        # 1. API: Screen image (Multipart or JSON)
        if path == '/api/screen':
            patient_meta = {}
            image_bytes = None

            if 'multipart/form-data' in content_type:
                # Parse multipart (pure-stdlib, works on Python 3.8–3.14+)
                length = int(self.headers.get('Content-Length', 0))
                form = _parse_multipart(self.rfile, content_type, length)

                if 'file' in form and isinstance(form['file'], bytes):
                    image_bytes = form['file']

                upload_fname = form.get('file_filename') or form.get('filename') or ''
                patient_meta = {
                    'patient_id': form.get('patient_id') or 'PAT-NEW',
                    'patient_name': form.get('patient_name') or 'Walk-in Patient',
                    'patient_age': _safe_int(form.get('patient_age'), 55),
                    'patient_gender': form.get('patient_gender') or 'Female',
                    'diabetes_duration': _safe_int(form.get('diabetes_duration'), 6),
                    'hba1c': _safe_float(form.get('hba1c'), 7.2),
                    'eye': form.get('eye') or 'OD',
                    'filename': upload_fname,
                    'sample_hint': form.get('sample_hint') or upload_fname,
                    'sample_file': upload_fname
                }
                if 'target_level' in form and form['target_level'] not in (None, ''):
                    patient_meta['target_level'] = _safe_int(form['target_level'], None)
            else:
                # JSON with base64 image or sample_id
                length = int(self.headers.get('Content-Length', 0))
                raw_data = self.rfile.read(length)
                try:
                    payload = json.loads(raw_data.decode('utf-8'))
                    patient_meta = payload.get('patient_meta', {})
                    if not patient_meta:
                        # Allow flat patient fields in the JSON root
                        patient_meta = {
                            'patient_id': payload.get('patient_id') or 'PAT-NEW',
                            'patient_name': payload.get('patient_name') or 'Walk-in Patient',
                            'patient_age': _safe_int(payload.get('patient_age'), 55),
                            'patient_gender': payload.get('patient_gender') or 'Female',
                            'diabetes_duration': _safe_int(payload.get('diabetes_duration'), 6),
                            'hba1c': _safe_float(payload.get('hba1c'), 7.2),
                            'eye': payload.get('eye') or 'OD'
                        }
                    else:
                        patient_meta['patient_age'] = _safe_int(patient_meta.get('patient_age'), 55)
                        patient_meta['diabetes_duration'] = _safe_int(patient_meta.get('diabetes_duration'), 6)
                        patient_meta['hba1c'] = _safe_float(patient_meta.get('hba1c'), 7.2)

                    # Always resolve sample_id metadata when provided
                    sample_id = payload.get('sample_id') or patient_meta.get('sample_hint')
                    matched_sample = None
                    if sample_id:
                        sample_id_str = str(sample_id).strip()
                        meta_path = os.path.join(SAMPLES_DIR, 'metadata.json')
                        if os.path.exists(meta_path):
                            with open(meta_path, 'r') as f:
                                sm = json.load(f)

                            # 1. Exact ID match
                            matched_sample = next((s for s in sm if s['id'] == sample_id_str), None)

                            # 2. Match by level or digit if like "sample-002", "sample-2", "2"
                            if not matched_sample:
                                digits = re.findall(r'\d+', sample_id_str)
                                if digits:
                                    target_level = int(digits[-1])
                                    matched_sample = next((s for s in sm if s.get('dr_level') == target_level), None)

                            # 3. Substring match
                            if not matched_sample:
                                matched_sample = next((s for s in sm if sample_id_str.lower() in s['id'].lower() or sample_id_str.lower() in s['filename'].lower()), None)

                    if matched_sample:
                        patient_meta['sample_hint'] = f"{matched_sample.get('id', '')} {matched_sample.get('label', '')} {matched_sample.get('filename', '')}"
                        patient_meta['sample_file'] = matched_sample['filename']
                        patient_meta['filename'] = matched_sample['filename']
                        if matched_sample.get('dr_level') is not None:
                            patient_meta['target_level'] = matched_sample['dr_level']
                        patient_meta.setdefault('patient_id', f"PAT-{matched_sample['id'][:14].upper()}")
                        patient_meta.setdefault('patient_name', f"Demo Patient ({matched_sample.get('label', 'Fundus')})")

                    if payload.get('image_base64'):
                        b64_str = payload['image_base64']
                        if ',' in b64_str:
                            b64_str = b64_str.split(',', 1)[1]
                        image_bytes = base64.b64decode(b64_str)
                    elif matched_sample:
                        s_path = os.path.join(SAMPLES_DIR, 'images', matched_sample['filename'])
                        if os.path.exists(s_path):
                            with open(s_path, 'rb') as sf:
                                image_bytes = sf.read()
                except Exception as e:
                    self._send_json({"error": f"Invalid JSON payload: {e}"}, 400)
                    return

            if not image_bytes:
                self._send_json({"error": "No image provided for screening"}, 400)
                return

            # Execute pipeline
            try:
                result = run_screening_pipeline(image_bytes, patient_meta)
                save_screening(result)
                self._send_json(result)
            except Exception as e:
                self._send_json({"error": f"Pipeline processing failed: {str(e)}"}, 500)
            return

        # 2. API: Doctor review update
        elif path == '/api/review':
            length = int(self.headers.get('Content-Length', 0))
            raw_data = self.rfile.read(length)
            try:
                payload = json.loads(raw_data.decode('utf-8'))
                s_id = payload.get('screening_id')
                if not s_id:
                    self._send_json({"error": "screening_id required"}, 400)
                    return

                existing = get_screening_by_id(s_id)
                if not existing:
                    self._send_json({"error": f"Screening '{s_id}' not found"}, 404)
                    return

                update_doctor_review(s_id, payload)
                updated = get_screening_by_id(s_id)
                self._send_json({"success": True, "screening": updated})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # 3. API: Telemedicine Simulation run
        elif path == '/api/simulate':
            length = int(self.headers.get('Content-Length', 0))
            raw_data = self.rfile.read(length)
            scenario = "scenario_a"
            overrides = {}
            if length > 0:
                try:
                    payload = json.loads(raw_data.decode('utf-8'))
                    scenario = payload.get('scenario', 'scenario_a')
                    overrides = payload.get('overrides', {})
                except Exception:
                    pass

            sim_result = run_simulation(scenario, overrides)
            self._send_json(sim_result)
            return

        # 4. Unknown endpoint
        self._send_json({"error": "Endpoint not found"}, 404)

def run_server(port=8000):
    server_address = ('', port)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(server_address, RetinaAPIHandler) as httpd:
        print(f"==================================================")
        print(f"  RetinaAI Web Dashboard & Orchestration Server   ")
        print(f"  Listening on: http://localhost:{port}           ")
        print(f"  Precision Clinical Design System Active         ")
        print(f"==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server gracefully...")
            httpd.shutdown()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
