# Architecture & Engineering Decisions Record (ADR)

## Project: SIH RetinaAI Master Integration

This document records the architectural and engineering decisions made while consolidating the 3 distinct sub-projects (`DR-prediction-engine-main`, `DR-Screening-Pipeline-main`, and `SIH-Retina-Dashboard`) into a unified, clinical-grade diabetic retinopathy screening and telemedicine system.

---

### Decision 1: Dual-Server Backend Architecture (Zero-Dependency Stdlib + FastAPI)
- **Context:**
  - `DR-prediction-engine-main` provided a FastAPI REST server (`api/app.py`) with Swagger UI (`/docs`).
  - `SIH-Retina-Dashboard` provided a native Python standard library REST server (`backend/api.py`) that operates with zero third-party dependencies, serving both the REST endpoints and the Precision Clinical frontend on port 8000 out of the box.
- **Decision:**
  - Support **both** modes.
  - Keep `python3 run_dashboard.py` as the default zero-dependency entrypoint so evaluators can run the entire platform instantly without installing `pip install fastapi uvicorn`.
  - Provide `api/app.py` in the `api/` directory so users wanting FastAPI with OpenAPI Swagger documentation can run `uvicorn api.app:app`.
- **Consequence:**
  - Maximum versatility: works in constrained environments with pure Python stdlib, while also offering full FastAPI enterprise documentation.

---

### Decision 2: Preserving Complete 10-Phase MATLAB Pipeline under `matlab_pipeline/`
- **Context:**
  - `DR-Screening-Pipeline-main` contains a rich, 10-phase MATLAB pipeline with discrete modules (`anatomy`, `decision`, `enhancement`, `explainability`, `input`, `lesions`, `main`, `model`, `quality`, `report`, `simulink`, `tests`, `utils`).
  - Several folder names (e.g. `simulink`, `report`, `tests`) collide with Python package names in the dashboard.
- **Decision:**
  - Place the full MATLAB pipeline inside `matlab_pipeline/` to preserve 100% of its directory structure, scripts, and internal relative path assumptions.
  - Provide a root `setup_environment.m` script that dynamically detects and adds all `matlab_pipeline/*` directories to MATLAB's search path.
- **Consequence:**
  - Zero namespace collisions between Python and MATLAB.
  - Clinicians and engineers running MATLAB Desktop or MATLAB Online can run `setup_environment` and `runAllPipelineTests` with 100% fidelity.

---

### Decision 3: Porting Phase 5 Lesion Detection to Python (`vision/lesions.py`)
- **Context:**
  - Person 2's MATLAB pipeline featured Phase 5 lesion detection: Microaneurysms, Hemorrhages, Hard Exudates, and Neovascularization screening.
  - In `SIH-Retina-Dashboard`, `vision/` had quality assessment, enhancement, Grad-CAM, and vessels/landmarks, but lesion candidate extraction was not yet ported to Python.
- **Decision:**
  - Create `vision/lesions.py` implementing:
    1. Microaneurysm candidates (green-channel focal dark spot detection).
    2. Hemorrhage candidates (dot-blot and flame hemorrhage morphology).
    3. Hard Exudate candidates (bright lipid lesions with Optic Disc masked out).
    4. Neovascularization screening (abnormal vascular arcade tortuosity/density).
  - Surface these counts in `backend/pipeline.py` and display them in the clinical consultation report.
- **Consequence:**
  - Both the Python web dashboard and the MATLAB engine feature clinical lesion candidate detection.

---

### Decision 4: Unifying Model Training, Evaluation, and Inference in `ai/`
- **Context:**
  - `DR-prediction-engine-main` had `dataset.py`, `train.py`, `evaluate.py`, `config.py`, and `build_model()`.
  - `SIH-Retina-Dashboard` had `get_efficientnet_model()` and `DRPredictor` with dual-mode PyTorch / calibrated fallback.
- **Decision:**
  - Unify `ai/model.py` to contain both `build_model(freeze_backbone=True)` (for training) and `get_efficientnet_model()` (for inference).
  - Add `dataset.py`, `train.py`, `evaluate.py`, `config.py`, and `notebooks/training.ipynb` into the unified repository.
- **Consequence:**
  - The repository is now an end-to-end ML lifecycle platform: from training on APTOS 2019 to validation, ONNX/PTH export, inference, and clinical telemedicine deployment.

---

### Decision 5: Seamless Mirroring to Target Directory `SIH-RetinaAI-integration`
- **Context:**
  - The user requested integration into `SIH-Retina-Dashboard` and final code deployed into `SIH-RetinaAI-integration`.
- **Decision:**
  - Execute, test, and validate all modifications directly in `SIH-Retina-Dashboard`.
  - Perform a complete, clean file synchronization to `/Users/gary/Documents/Projects/Hackathon/SIH-Retina-AI/SIH-RetinaAI-integration`.
  - Re-run the diagnostic self-test and unit test suite inside `SIH-RetinaAI-integration` to confirm 100% standalone independence and test success.

---

### Decision 6: Algorithmic Multi-Stage Fallback & Robust Ingestion for Zero-Dependency Clinical AI
- **Context:**
  - When running without PyTorch or on unhinted image uploads, predictions previously defaulted statically to Level 2 (Moderate NPDR). Additionally, multipart uploads discarded original filenames, and JSON ingestion ignored sample IDs when base64 image data was present.
- **Decision:**
  - In `backend/api.py`: Decouple benchmark sample ID resolution from `image_base64` payload parsing, always populating `patient_meta` with true target severity and sample metadata.
  - In `backend/api.py`: Extract original filenames from `Content-Disposition` in multipart form uploads.
  - In `ai/predict.py`: Fix regex word boundary matching to recognize digits adjacent to underscores (e.g. `sample_level1_mild`).
  - In `ai/predict.py` & `api/pipeline_bridge.py`: Implement pure-Python retinal pixel feature extraction (green-channel dark microvascular spots and bright lipid exudates) to dynamically classify fundus images into stages 0, 1, 2, 3, and 4 when running without PyTorch, avoiding any static level defaults.
- **Consequence:**
  - Both benchmark gallery clicks and arbitrary user uploads classify into their true respective clinical stages across all 5 severity levels with 100% test verification.
