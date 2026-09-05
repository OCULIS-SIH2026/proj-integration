# RetinaAI — Unified Diabetic Retinopathy Screening & Tele-Ophthalmology System

**Smart India Hackathon (SIH) Master Integration Deliverable**  
**Unified Integration of Person 1 (AI/ML), Person 2 (CV/XAI & MATLAB), and Person 3 (Full-Stack UI & Telemedicine)**

An end-to-end clinical tele-ophthalmology screening platform that checks fundus image quality, classifies diabetic retinopathy (Level 0–4) using EfficientNet-B0 with >91% sensitivity, provides multi-layer explainability through Grad-CAM heatmaps, retinal landmark segmentation, and quantitative lesion candidate detection (Microaneurysms, Hemorrhages, Hard Exudates, Neovascularization), facilitates rapid human-in-the-loop ophthalmologist review (<30s), generates standardized clinical consultation reports, and models large-scale telemedicine queuing capacity (100,000+ patients/year) via both Python simulation and MATLAB SimEvents.

The platform provides a dual-server architecture:
1. **Zero-Dependency Native Server (`python3 run_dashboard.py`)**: Runs out-of-the-box using the Python standard library on port 8000 serving both the REST API and the Precision Clinical web dashboard.
2. **FastAPI Enterprise REST Backend (`uvicorn api.app:app --port 8000`)**: OpenAPI/Swagger documented microservice (`/docs`) for programmatic REST integration.
3. **Full 10-Phase MATLAB Clinical Engine (`setup_environment.m`)**: Complete MATLAB and Simulink pipeline under `matlab_pipeline/`.

---

## 1. Quick Start

### Option A: Standard Web Dashboard & Zero-Dep REST API (Recommended)
Runs out-of-the-box using the Python standard library with zero mandatory external dependencies:

```bash
# 1. Run diagnostic self-test
python3 run_dashboard.py --test

# 2. Run all unit & feature tests (33 tests)
python3 -m unittest discover -s tests -v

# 3. Start the web server and dashboard
python3 run_dashboard.py
```
Open your browser at **`http://localhost:8000`**.

### Option B: FastAPI REST Service (Person 1 & 2 Microservice)
```bash
cd api
python -m uvicorn app:app --reload --port 8000
```
- Interactive Swagger UI Documentation: **`http://localhost:8000/docs`**
- Screening endpoint: `POST /api/screen`
- Health check: `GET /api/health`
- Mock contract endpoint: `GET /api/mock`

### Option C: Complete 10-Phase MATLAB & Simulink Engine
In MATLAB Desktop or MATLAB Online:
```matlab
% 1. Initialize all pipeline paths
setup_environment;

% 2. Run complete 10-phase unit test harness
runAllPipelineTests;

% 3. Single-command patient screening
sample = screenFundusImage("sample_data/images/sample_moderate_level2.bmp");
disp(sample.report.summaryText);

% 4. Run 100k patient telemedicine queuing simulation
simulateScreeningWorkflow(DR_Screening_System_params('AnnualVolume', 100000), 'SimulationHours', 8, 'Plot', true);
```

### Option D: One-Click Launch Scripts
- **macOS / Linux**: `./quicklaunch/quicklaunch.sh` (or `./quicklaunch/quicktest.sh`)
- **Windows**: `quicklaunch\quicklaunch.cmd` (or `quicklaunch\quicktest.cmd`)

---

## 2. Team Division & Integrated Deliverables

```text
                                  +-------------------------------------------------------+
                                  |              OCULIS / RetinaAI Master                 |
                                  +-------------------------------------------------------+
                                                              |
                  +-------------------------------------------+-------------------------------------------+
                  |                                           |                                           |
                  v                                           v                                           v
     +--------------------------+               +----------------------------+              +---------------------------+
     |   PERSON 1: AI / ML      |               |   PERSON 2: CV / XAI       |              |   PERSON 3: FULL STACK    |
     | (DR-prediction-engine)   |               | (DR-Screening-Pipeline)    |              | (SIH-Retina-Dashboard)    |
     +--------------------------+               +----------------------------+              +---------------------------+
     | • EfficientNet-B0 Model  |               | • 10-Phase MATLAB Engine   |              | • Precision Clinical UI   |
     | • APTOS Dataset & Train  |               | • Retinal Anatomy (OD/Fov) |              | • Zero-dep REST API       |
     | • Evaluation (QWK, ROC)  |               | • Lesion Candidates (MA/HE)|              | • SQLite Worklist & Store |
     | • PyTorch Grad-CAM XAI   |               | • IQA (Sharpness/Illum/FOV)|              | • Telemedicine Simulation |
     | • FastAPI REST Service   |               | • Simulink System Sizing   |              | • Printable Reports       |
     +--------------------------+               +----------------------------+              +---------------------------+
                  |                                           |                                           |
                  +-------------------------------------------+-------------------------------------------+
                                                              |
                                                              v
                                  +-------------------------------------------------------+
                                  |              UNIFIED PRODUCTION SYSTEM                |
                                  +-------------------------------------------------------+
```

| Member | Role | Deliverables Integrated |
|---|---|---|
| **Person 1** | AI / ML Engineer | PyTorch EfficientNet-B0 (`models/best_model.pth`, `best_model.onnx`), 5-class DR classifier, two-stage transfer learning (`ai/train.py`, `ai/dataset.py`), QWK / ROC evaluation (`ai/evaluate.py`), Grad-CAM hook (`vision/gradcam.py`), CLI tools (`demo.py`, `run_on_aptos.py`, `pipeline_cli.py`), and FastAPI REST microservice (`api/app.py`). |
| **Person 2** | Computer Vision / Clinical XAI | 10-Phase clinical screening pipeline in MATLAB (`matlab_pipeline/`), Image Quality Assessment (sharpness via Laplacian variance on retinal mask, illumination, contrast, FOV ratio), selective CIE L*a*b* CLAHE enhancement, Optic Disc and Fovea localization, vascular arborization segmentation, quantitative lesion candidate extraction (Microaneurysms, Hemorrhages, Hard Exudates with OD masking, Neovascularization) in both Python (`vision/lesions.py`) and MATLAB (`lesions/`), SimEvents capacity model. |
| **Person 3** | Full-Stack & Telemedicine Systems | Precision Clinical web dashboard (`frontend/`), high-performance native REST API server (`backend/api.py`), thread-safe SQLite database (`backend/database.py`), clinical consultation report generator (`reports/report_generator.py`), Python discrete-event queuing simulator (`simulink/telemedicine_sim.py`), seed datasets, test suites (`tests/`), and one-click launch scripts. |

---

## 3. Directory Structure

```text
SIH-Retina-Dashboard/
├── ai/
│   ├── model.py                # EfficientNet-B0 architecture, weights loader & unfreeze
│   ├── predict.py              # Unified inference engine (PyTorch + calibrated fallback)
│   ├── dataset.py              # APTOS 2019 PyTorch Dataset with data augmentations
│   ├── train.py                # Two-stage transfer learning training script
│   ├── evaluate.py             # Full evaluation: QWK, confusion matrix, per-class metrics
│   ├── evaluation.py           # Clinical metrics & SIH benchmark metrics
│   └── config.py               # Hyperparameters for model training
├── vision/
│   ├── quality.py              # IQA: Blur (Laplacian variance), illumination, contrast, FOV
│   ├── enhancement.py          # CLAHE in CIE L*a*b* color space
│   ├── gradcam.py              # PyTorch Grad-CAM hook and blended heatmap overlays
│   ├── vessels.py              # Retinal vascular tree, Optic Disc, and Fovea landmarks
│   └── lesions.py              # Lesion candidates: Microaneurysms, Hemorrhages, Exudates, NV
├── backend/
│   ├── api.py                  # High-performance native REST API server on port 8000
│   ├── pipeline.py             # Master orchestrator: Quality -> Enhancement -> AI -> XAI -> Lesions
│   ├── database.py             # Thread-safe SQLite store with audit trail
│   ├── seed_data.py            # Preloaded clinical benchmark cases
│   └── retina_screenings.db    # SQLite database file
├── api/                        # FastAPI REST microservice (Person 1 & 2 deliverable)
│   ├── app.py                  # FastAPI server (/api/screen, /api/mock, /api/health)
│   ├── pipeline_bridge.py      # Bridge to models/best_model.pth and CLAHE
│   ├── test_api.py             # FastAPI automated test suite
│   ├── run_api.bat             # Windows launcher for FastAPI
│   └── README_FRONTEND.md      # API contract and React examples
├── matlab_pipeline/            # Complete 10-Phase MATLAB Clinical Engine (Person 2)
│   ├── setup_environment.m     # Environment path loader
│   ├── main/                   # screenFundusImage.m, demoMilestone1.m
│   ├── input/                  # loadFundusImage.m, createSampleStruct.m
│   ├── quality/                # assessImageQuality.m, calculateSharpness.m, assessFOV.m
│   ├── enhancement/            # enhanceFundusImage.m, applyCLAHE.m, denoiseFundus.m
│   ├── anatomy/                # analyzeRetinalStructures.m, locateOpticDisc.m, segmentVessels.m
│   ├── lesions/                # detectMicroaneurysms.m, detectHemorrhages.m, detectExudates.m
│   ├── model/                  # loadDRModel.m, runDRModel.m, preprocessForModel.m
│   ├── explainability/         # generateGradCAM.m, computeGradCAMMap.m, overlayHeatmap.m
│   ├── decision/               # makeClinicalDecision.m, determineReferral.m, applyClinicalGate.m
│   ├── report/                 # generateScreeningReport.m, formatReportText.m
│   ├── simulink/               # simulateScreeningWorkflow.m, DR_Screening_System_params.m
│   ├── tests/                  # runAllPipelineTests.m, testPhase1.m - testPhase10.m
│   └── utils/                  # getConfig.m, loadEnv.m
├── frontend/                   # Precision Clinical HTML5/CSS3/ES6 Web Dashboard
│   ├── index.html              # Single-page clinical interface
│   ├── css/retina-dashboard.css# Precision Clinical design tokens (Terracotta, Stone)
│   └── js/
│       ├── api.js              # REST client
│       ├── app.js              # Router, state management, notifications
│       └── components/         # Dashboard, Screening, Quality, Results, Review, Report, Simulation
├── models/
│   ├── best_model.pth          # Trained EfficientNet-B0 PyTorch weights (16.3 MB)
│   ├── best_model.onnx         # Exported ONNX model (657 KB)
│   ├── class_names.json        # Grade index to label mapping
│   └── config.json             # Normalization stats and architecture config
├── reports/
│   └── report_generator.py     # Standardized clinical consultation report with lesion table
├── simulink/
│   ├── telemedicine_sim.py     # Python discrete-event queuing simulator (100k+ pts/yr)
│   ├── scenarios.json          # Scenarios A, B, C, D presets
│   ├── export_simulink.m       # SimEvents programmatic model builder
│   ├── DR_Screening_System_params.m # Sizing parameters
│   └── analyzeSystemCapacity.m # Capacity planning & bottleneck detection
├── sample_data/
│   ├── images/                 # 6 clinical test cases (Normal, Mild, Moderate, Severe, PDR, Blur)
│   ├── generate_samples.py     # Synthetic fundus generator
│   └── metadata.json           # Sample registry
├── tests/
│   ├── test_unit.py            # Unit test suite (quality, prediction, lesions, database, sim)
│   ├── test_features.py        # Feature verification (12 clinical features)
│   └── test_api_endpoints.py   # Integration test runner
├── notebooks/
│   └── training.ipynb          # Google Colab retraining notebook
├── quicklaunch/
│   ├── quicklaunch.sh / .cmd   # 1-click startup script
│   └── quicktest.sh / .cmd     # 1-click test runner
├── demo.py                     # CLI inference tool
├── pipeline_cli.py             # End-to-end command-line screening pipeline
├── run_on_aptos.py             # Batch evaluation runner on APTOS fundus datasets
├── run_dashboard.py            # Master startup runner and self-diagnostic tester
├── setup_environment.m         # Root MATLAB environment loader
├── INTERFACE.md                # Data contract specifications
├── decision.md                 # Architecture & Engineering Decisions Record (ADR)
├── progress.md                 # Project milestone & integration progress tracker
└── docs.md                     # Comprehensive technical & clinical documentation
```

---

## 4. Key Clinical Features for SIH Demonstration

1. **Complete 7-Stage Screening Workflow**:
   - Ingestion with full metadata (Age, Diabetes duration, HbA1c, Eye OD/OS).
   - Image Quality Assessment (Laplacian focus score, brightness, contrast, FOV validation).
   - CLAHE preview for borderline captures with automated recapture feedback for unusable images.
   - 5-Class DR Severity Classification (Level 0–4) with prominent Referable DR triage badge (Level ≥ 2).
   - Multi-layer explainability: Grad-CAM attention map with opacity slider, anatomical landmarks (Optic Disc, Fovea, Vascular Arcades), and quantitative lesion candidate evidence.
2. **Quantitative Lesion Candidate Evidence (Person 2)**:
   - Microaneurysms: Focal dark capillary outpouching count & coordinates.
   - Hemorrhages: Blot and flame hemorrhage candidate count and quadrant involvement.
   - Hard Exudates: Bright lipid leakage plaques with optic disc automatically masked out to eliminate false positives.
   - Neovascularization: Screening for abnormal disc (NVD) or arcade (NVE) vessel proliferation.
3. **Ophthalmologist Review Station (<30s SLA)**:
   - Rapid one-click confirmation or severity override.
   - Standardized referral routing (Routine, Ophthalmology within 4-6 weeks, Priority within 1-2 weeks, Emergency within 48h).
   - Clinician digital signature, timestamp, and audit trail recorded in SQLite.
4. **Printable Standardized Consultation Report**:
   - Professional print-ready layout containing patient history, quality metrics, AI diagnosis, calibrated confidence, lesion table, Grad-CAM, and reviewing ophthalmologist sign-off.
5. **Telemedicine Capacity Queuing Studio (100,000+ Patients/Year)**:
   - Evaluates system-wide throughput, doctor utilization, and queue delays across 4 operational scenarios.
   - Identifies bottlenecks across camera acquisition, network transmission, cloud GPU inference, and ophthalmologist review.
