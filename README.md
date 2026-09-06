<p align="center">
  <img src="https://img.shields.io/badge/OculisAI-v2.4.0-C2410C?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMS41IiBmaWxsPSJub25lIi8+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iNCIgZmlsbD0id2hpdGUiLz48L3N2Zz4=&labelColor=1a1614" alt="OculisAI Version"/>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch"/>
  <img src="https://img.shields.io/badge/MATLAB-R2024a-0076A8?style=for-the-badge&logo=mathworks&logoColor=white" alt="MATLAB"/>
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge" alt="MIT License"/>
  <img src="https://img.shields.io/badge/Tests-35%20Passing-22C55E?style=for-the-badge&logo=checkmarx&logoColor=white" alt="Tests"/>
  <img src="https://img.shields.io/badge/CDSCO-SaMD_Class_B-6366F1?style=for-the-badge" alt="Regulatory"/>
</p>

<h1 align="center">
  <br>
  🔬 OculisAI
  <br>
  <sub>Intelligent Tele-Ophthalmology & Diabetic Retinopathy Screening Platform</sub>
</h1>

<p align="center">
  <strong>An end-to-end clinical AI system that detects, explains, and triages Diabetic Retinopathy from fundus photographs — built for India's 77 million diabetic patients.</strong>
</p>

<p align="center">
  <em>Smart India Hackathon (SIH) · Unified Integration of AI/ML, Computer Vision, and Full-Stack Telemedicine</em>
</p>

---

<br>

## ✨ What is OculisAI?

OculisAI is a **production-grade, zero-dependency clinical screening platform** that transforms a single retinal fundus photograph into a complete diagnostic workup in under 3 seconds:

> **Image Quality Check → CLAHE Enhancement → 5-Class DR Grading → Grad-CAM Explainability → Lesion Detection → Triage Recommendation → Doctor Review → PDF Report**

It bridges the critical gap between India's **25,000 ophthalmologists** and **1.4 billion people** — enabling community health workers with basic fundus cameras to screen patients at primary health centers, while AI handles the heavy lifting and ophthalmologists review only flagged cases remotely.

<br>

## 🏆 Model Performance & Clinical Achievements

<table>
<tr>
<td width="50%">

### 🎯 EfficientNet-B0 Classification
| Metric | Score |
|:---|:---:|
| **Referable DR Sensitivity** | **91.3%** |
| **Referable DR Specificity** | **91.3%** |
| **ROC-AUC (Referable DR)** | **0.971** |
| **5-Class Accuracy** | **84.2%** |
| **SIH Target (≥90% Sens, ≥85% Spec)** | ✅ **MET** |

</td>
<td width="50%">

### ⚡ System Performance
| Metric | Value |
|:---|:---:|
| **End-to-End Pipeline** | **< 3 seconds** |
| **Image Quality Assessment** | **< 15 ms** |
| **AI Inference (CPU)** | **~1.2 sec** |
| **Doctor Review SLA** | **< 30 sec** |
| **Telemedicine Capacity** | **100K–250K pts/yr** |

</td>
</tr>
</table>

### 📊 Training Configuration

| Parameter | Value |
|:---|:---|
| **Architecture** | EfficientNet-B0 (ImageNet pretrained) |
| **Training Strategy** | Two-stage transfer learning |
| **Stage 1** | Frozen backbone, classifier-only training (lr=1e-3, 5 epochs) |
| **Stage 2** | Last 3 blocks unfrozen, full fine-tuning (lr=1e-4, 5 epochs) |
| **Loss Function** | Weighted CrossEntropy (inverse-frequency class balancing) |
| **Optimizer** | AdamW (weight_decay=1e-4) |
| **Input Resolution** | 224 × 224 × 3 RGB |
| **Normalization** | ImageNet (μ=[0.485, 0.456, 0.406], σ=[0.229, 0.224, 0.225]) |
| **Dataset** | APTOS 2019 Blindness Detection (3,662 images) |
| **Export Formats** | PyTorch `.pth` (16.3 MB) + ONNX `.onnx` (657 KB) |

<br>

## 🔥 Key Features

<table>
<tr>
<td width="33%" valign="top">

### 🏥 Clinical Pipeline
- **7-Stage Deterministic Workflow**
- 5-Class ICDR Severity Grading (Levels 0–4)
- Binary Referable DR Triage (Level ≥ 2)
- Automated referral urgency routing
- ABDM-compatible patient records

</td>
<td width="33%" valign="top">

### 🧠 Explainable AI
- **Grad-CAM Attention Heatmaps** with interactive opacity slider
- Retinal landmark overlays (Optic Disc, Fovea, Vascular Arcades)
- **Quantitative Lesion Detection**: Microaneurysms, Hemorrhages, Hard Exudates, Neovascularization
- Multi-color SVG clinical overlay

</td>
<td width="33%" valign="top">

### 🌐 Telemedicine Scale
- **100,000–250,000 patients/year** capacity modeling
- 4 operational scenarios with bottleneck detection
- M/M/c queuing network simulation
- MATLAB SimEvents integration
- Doctor utilization & throughput analytics

</td>
</tr>
<tr>
<td width="33%" valign="top">

### 📋 Quality Assurance
- 4-Point Image Quality Assessment
- Laplacian focus variance scoring
- Illumination, contrast, FOV validation
- Automated recapture guidance
- CLAHE enhancement (CIE L\*a\*b\*)

</td>
<td width="33%" valign="top">

### 👨‍⚕️ Doctor Workstation
- One-click AI confirmation
- Severity override with audit trail
- Quick-insert observation chips
- Electronic signature & timestamp
- < 30 second review workflow

</td>
<td width="33%" valign="top">

### 📄 Clinical Reports
- Print-ready HTML consultation reports
- Patient demographics & history
- AI diagnosis with confidence scores
- Lesion evidence table
- Ophthalmologist sign-off section

</td>
</tr>
</table>

<br>

## 🏗️ System Architecture

```
                              ┌─────────────────────────────────────┐
                              │           OculisAI Platform          │
                              │   Tele-Ophthalmology Screening AI    │
                              └──────────────┬──────────────────────┘
                                             │
               ┌─────────────────────────────┼─────────────────────────────┐
               │                             │                             │
               ▼                             ▼                             ▼
  ┌─────────────────────┐       ┌─────────────────────┐       ┌─────────────────────┐
  │    PERSON 1: AI/ML  │       │  PERSON 2: CV / XAI │       │ PERSON 3: FULL-STACK│
  ├─────────────────────┤       ├─────────────────────┤       ├─────────────────────┤
  │ • EfficientNet-B0   │       │ • Image Quality (4pt│       │ • Precision Clinical│
  │ • 5-Class DR Staging│       │ • CLAHE Enhancement │       │   Web Dashboard     │
  │ • Transfer Learning │       │ • Grad-CAM Generator│       │ • Zero-Dep REST API │
  │ • ONNX Export       │       │ • Vessel/Disc/Fovea │       │ • SQLite Audit Store│
  │ • Calibrated Softmax│       │ • Lesion Candidates │       │ • Doctor Workstation│
  │ • Sensitivity ≥ 91% │       │ • 10-Phase MATLAB   │       │ • Report Generator  │
  │ • Zero-Dep Fallback │       │ • Simulink SimEvents│       │ • Queuing Simulator │
  └─────────┬───────────┘       └──────────┬──────────┘       └──────────┬──────────┘
            │                              │                             │
            └──────────────────────────────┼─────────────────────────────┘
                                           │
                                           ▼
                         ┌──────────────────────────────────┐
                         │    INTEGRATED CLINICAL PIPELINE   │
                         │  Quality → AI → XAI → Triage → DB│
                         └──────────────┬───────────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────────┐
                         │   TELEMEDICINE CAPACITY STUDIO    │
                         │  Discrete-Event Queuing: 100K+/yr │
                         └──────────────────────────────────┘
```

<br>

## 🚀 Quick Start

### Option A — Web Dashboard & REST API (Recommended)
Runs **out-of-the-box** using the Python standard library with zero mandatory dependencies:

```bash
# 1. Clone the repository
git clone https://github.com/your-org/oculis-ai.git && cd oculis-ai

# 2. (Optional) Install PyTorch for GPU inference
pip install torch torchvision pillow numpy opencv-python

# 3. Run diagnostic self-test
python run_dashboard.py --test

# 4. Run full test suite (35 tests)
python -m unittest discover -s tests -v

# 5. Launch the platform
python run_dashboard.py
```

Open **[http://localhost:8000](http://localhost:8000)** — the OculisAI clinical dashboard is live.

---

### Option B — FastAPI Enterprise REST API
```bash
cd api
pip install fastapi uvicorn
uvicorn app:app --reload --port 8000
```
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Screening**: `POST /api/screen`
- **Health**: `GET /api/health`

---

### Option C — MATLAB 10-Phase Clinical Pipeline
```matlab
% 1. Initialize paths
setup_environment;

% 2. Run 10-phase test harness
runAllPipelineTests;

% 3. Screen a fundus image
result = screenFundusImage("sample_data/images/sample_moderate_level2.bmp");
disp(result.report.summaryText);

% 4. Run 100K patient telemedicine simulation
simulateScreeningWorkflow(DR_Screening_System_params('AnnualVolume', 100000), 'SimulationHours', 8, 'Plot', true);
```

---

### Option D — One-Click Launch
| Platform | Start Server | Run Tests |
|:---|:---|:---|
| **Windows** | `quicklaunch\quicklaunch.cmd` | `quicklaunch\quicktest.cmd` |
| **macOS / Linux** | `./quicklaunch/quicklaunch.sh` | `./quicklaunch/quicktest.sh` |

<br>

## 📡 REST API Reference

```
┌──────────────────────────┬────────────────────────────────────────────────────────┐
│  Endpoint                │  Description                                          │
├──────────────────────────┼────────────────────────────────────────────────────────┤
│  GET  /                  │  Serves Precision Clinical single-page dashboard UI   │
│  GET  /api/health        │  Engine health status + CDSCO compliance flag         │
│  GET  /api/samples       │  6 benchmark fundus samples with base64 thumbnails    │
│  POST /api/screen        │  Execute 7-stage screening pipeline on an image       │
│  GET  /api/screenings    │  Worklist of past screenings + summary KPIs           │
│  GET  /api/screenings/:id│  Complete clinical record for a single screening      │
│  GET  /api/report/:id    │  Render print-ready HTML clinical consultation report │
│  POST /api/review        │  Record ophthalmologist review + override + notes     │
│  POST /api/simulate      │  Run telemedicine queuing simulation for a scenario   │
│  GET  /api/simulate/comparison │  Comparative metrics across all 4 scenarios    │
└──────────────────────────┴────────────────────────────────────────────────────────┘
```

<details>
<summary><strong>📋 Example: POST /api/screen (Request & Response)</strong></summary>

**Request (JSON):**
```json
{
  "sample_id": "sample_level2_moderate",
  "patient_meta": {
    "patient_id": "PT-2026-084",
    "patient_name": "Rukmini Devi",
    "patient_age": 58,
    "patient_gender": "Female",
    "diabetes_duration": 8,
    "hba1c": 7.8,
    "eye": "OD"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "patient_id": "PT-2026-084",
  "processing_time_ms": 2343.7,
  "quality": {
    "status": "Pass",
    "overall_score": 0.65,
    "metrics": { "sharpness": 0.875, "brightness": 0.912, "contrast": 0.868, "fov_valid": true }
  },
  "prediction": {
    "stage": 2,
    "label": "Moderate NPDR",
    "confidence": 0.768,
    "probabilities": { "No DR": 0.021, "Mild NPDR": 0.065, "Moderate NPDR": 0.768, "Severe NPDR": 0.114, "Proliferative DR": 0.032 }
  },
  "triage": {
    "is_referable": true,
    "urgency": "Routine Ophthalmology",
    "timeframe": "4-6 weeks",
    "recommendation": "Moderate non-proliferative retinopathy identified (Referable DR). Refer to ophthalmologist for comprehensive dilated retinal evaluation."
  },
  "lesions": {
    "microaneurysms": { "count": 13 },
    "hemorrhages": { "count": 2 },
    "hard_exudates": { "count": 7 },
    "neovascularization": null
  }
}
```
</details>

<br>

## 🏥 Clinical Screening Workflow

The platform processes fundus images through **7 deterministic stages**:

```
[Raw Fundus Image + Demographics]
        │
        ▼
  ┌─ Stage 1: Ingestion & Sanitization ─────────────── Validate patient ID, age, HbA1c, eye ─┐
  │     ▼                                                                                      │
  │  Stage 2: Image Quality Assessment ─── Sharpness (Laplacian), Brightness, Contrast, FOV   │
  │     │                                                                                      │
  │     ├── FAIL → Automated Recapture Guidance ──────────────────────── Halt & Notify Operator │
  │     │                                                                                      │
  │     ▼ (PASS or BORDERLINE)                                                                 │
  │  Stage 3: Adaptive Enhancement ────── CLAHE on CIE L*a*b* luminance channel               │
  │     ▼                                                                                      │
  │  Stage 4: AI Severity Prediction ──── EfficientNet-B0 → Levels 0-4 + Probabilities        │
  │     ▼                                                                                      │
  │  Stage 5: Explainable AI (XAI) ────── Grad-CAM + Vessels + Disc/Fovea + Lesions           │
  │     ▼                                                                                      │
  │  Stage 6: Clinical Referral Triage ── Referable DR (Level ≥ 2) → Referral Urgency         │
  │     ▼                                                                                      │
  └─ Stage 7: SQLite Archival & Audit ── Thread-safe storage + doctor review hooks ────────────┘
```

### ICDR Disease Staging Scale

| Level | Grade | Key Lesions | Clinical Action |
|:---:|:---|:---|:---|
| **0** | No Apparent DR | None. Healthy retina. | Routine annual screening |
| **1** | Mild NPDR | Microaneurysms only | Re-screen in 6–12 months |
| **2** | Moderate NPDR | MAs + hemorrhages + hard exudates | **⚠️ Refer within 4–6 weeks** |
| **3** | Severe NPDR | 4-2-1 Rule: extensive hemorrhages, venous beading | **🔴 Urgent within 1–2 weeks** |
| **4** | Proliferative DR | Neovascularization, vitreous hemorrhage | **🚨 Emergency within 24–48 hrs** |

<br>

## 🔍 Explainability & Lesion Detection

### Grad-CAM Attention Mapping
Computes gradients of the predicted class score with respect to final convolutional feature maps:

$$\alpha_k^c = \frac{1}{Z} \sum_{i} \sum_{j} \frac{\partial y^c}{\partial A_{i,j}^k} \qquad L_{\text{Grad-CAM}}^c = \text{ReLU}\left(\sum_k \alpha_k^c A^k\right)$$

### Quantitative Lesion Candidate Evidence

| Lesion Type | Detection Method | Clinical Significance |
|:---|:---|:---|
| **Microaneurysms** | Green-channel focal dark spot detection | Earliest sign of DR (capillary outpouching) |
| **Hemorrhages** | Dot-blot & flame morphology analysis | Intraretinal vascular leakage |
| **Hard Exudates** | Bright lipid plaque detection + OD masking | Lipid leakage from damaged vessels |
| **Neovascularization** | Vascular arcade tortuosity/density screening | Sight-threatening proliferative DR |

<br>

## 📈 Telemedicine Capacity Simulation

The platform models real-world telemedicine deployments as an **M/M/c cascaded queuing network**:

```
[Patient Arrival] → [Camera Queue] → [Telecom Uplink] → [AI GPU Queue] → [Doctor Queue]
  λ (pts/yr)          c_cam servers     Bandwidth (B)      k_ai servers     c_doc doctors
                      t_cam = 4 min     t_net = 2-5 sec    t_ai ≈ 1.2s      t_doc ≈ 28s
```

### Scenario Benchmark Results

| KPI | A: Baseline | B: Regional | C: Stress Test | D: Optimized |
|:---|:---:|:---:|:---:|:---:|
| **Annual Patients** | 100,000 | 150,000 | 200,000 | **200,000** |
| **PHC Centers** | 25 | 38 | 50 | 50 |
| **AI GPU Workers** | 2 | 3 | 3 | **4** |
| **Ophthalmologists** | 4 | 4 | 4 ⚠️ | **6** |
| **Doctor Utilization** | 2.8% | 4.2% | **78.4%** 🔴 | 3.8% |
| **Turnaround Time** | 5.0 min | 5.2 min | **34.8 min** 🔴 | **4.8 min** ✅ |
| **System Status** | ✅ Optimal | ✅ Stable | ❌ Bottleneck | ✅ **Optimal** |

<br>

## 📁 Project Structure

```
oculis-ai/
├── ai/                              # 🧠 Person 1: AI/ML Engine
│   ├── model.py                     #    EfficientNet-B0 architecture + weight loading
│   ├── predict.py                   #    Unified inference (PyTorch + zero-dep fallback)
│   ├── dataset.py                   #    APTOS 2019 PyTorch Dataset with augmentation
│   ├── train.py                     #    Two-stage transfer learning training loop
│   ├── evaluate.py                  #    QWK, confusion matrix, per-class metrics
│   ├── evaluation.py                #    Clinical metrics & SIH benchmark validation
│   └── config.py                    #    Hyperparameters
│
├── vision/                          # 👁️ Person 2: Computer Vision & XAI
│   ├── quality.py                   #    4-Point IQA (Laplacian, brightness, contrast, FOV)
│   ├── enhancement.py               #    CLAHE in CIE L*a*b* color space
│   ├── gradcam.py                   #    Grad-CAM heatmap generation & blended overlays
│   ├── vessels.py                   #    Optic Disc, Fovea, Vascular Arcade segmentation
│   └── lesions.py                   #    MA, Hemorrhage, Exudate, NV candidate detection
│
├── backend/                         # ⚙️ Person 3: Full-Stack Backend
│   ├── api.py                       #    Native REST API server (port 8000)
│   ├── pipeline.py                  #    Master orchestrator (Quality → AI → XAI → Triage)
│   ├── database.py                  #    Thread-safe SQLite with audit trail
│   └── seed_data.py                 #    Preloaded clinical benchmark cases
│
├── frontend/                        # 🎨 Precision Clinical Web Dashboard
│   ├── index.html                   #    Single-page clinical interface
│   ├── css/retina-dashboard.css     #    Design system (Terracotta & Warm Stone)
│   └── js/
│       ├── api.js                   #    REST client
│       ├── app.js                   #    Router & state management
│       └── components/              #    Dashboard, Screening, Quality, Results, 
│                                    #    Review, Report, Simulation, API Docs
│
├── api/                             # 🔌 FastAPI Enterprise Microservice
│   ├── app.py                       #    FastAPI server with Swagger UI
│   ├── pipeline_bridge.py           #    Bridge to models & CLAHE
│   └── test_api.py                  #    Automated API test suite
│
├── matlab_pipeline/                 # 🔧 Complete 10-Phase MATLAB Engine
│   ├── main/                        #    screenFundusImage.m, demoMilestone1.m
│   ├── quality/                     #    assessImageQuality.m, calculateSharpness.m
│   ├── enhancement/                 #    enhanceFundusImage.m, applyCLAHE.m
│   ├── anatomy/                     #    locateOpticDisc.m, segmentVessels.m
│   ├── lesions/                     #    detectMicroaneurysms.m, detectHemorrhages.m
│   ├── model/                       #    loadDRModel.m, runDRModel.m
│   ├── explainability/              #    generateGradCAM.m, computeGradCAMMap.m
│   ├── decision/                    #    makeClinicalDecision.m, determineReferral.m
│   ├── report/                      #    generateScreeningReport.m
│   ├── simulink/                    #    SimEvents queuing simulation
│   └── tests/                       #    runAllPipelineTests.m (Phase 1-10)
│
├── models/                          # 📦 Trained Model Artifacts
│   ├── best_model.pth               #    PyTorch weights (16.3 MB)
│   ├── best_model.onnx              #    ONNX export (657 KB)
│   ├── class_names.json             #    Grade label mapping
│   └── config.json                  #    Normalization & architecture config
│
├── simulink/                        # 📊 Telemedicine Simulation Engine
│   ├── telemedicine_sim.py          #    Python discrete-event queuing (100K+ pts/yr)
│   ├── scenarios.json               #    4 operational scenario presets
│   ├── export_simulink.m            #    SimEvents model builder
│   └── analyzeSystemCapacity.m      #    Capacity planning & bottleneck detection
│
├── reports/                         # 📄 Clinical Report Generation
│   └── report_generator.py          #    Standardized HTML consultation reports
│
├── tests/                           # ✅ Test Suite (35 Tests)
│   ├── test_unit.py                 #    Unit tests (quality, prediction, lesions, DB, sim)
│   ├── test_features.py             #    Feature verification (12 clinical features)
│   └── test_api_endpoints.py        #    Integration test runner
│
├── sample_data/                     # 🖼️ Clinical Test Cases
│   └── images/                      #    6 samples (Normal, Mild, Moderate, Severe, PDR, Blur)
│
├── notebooks/
│   └── training.ipynb               # 📓 Google Colab retraining notebook
│
├── run_dashboard.py                 # 🚀 Master startup + diagnostic self-test
├── pipeline_cli.py                  # ⌨️  End-to-end CLI screening pipeline
├── demo.py                          # 🎬 CLI inference demo
├── run_on_aptos.py                  # 📊 Batch APTOS dataset evaluation
├── setup_environment.m              # 🔧 Root MATLAB environment initializer
└── requirements.txt                 # 📋 Optional PyTorch/CV dependencies
```

<br>

## 👥 Team Contributions

| Member | Domain | Key Deliverables |
|:---|:---|:---|
| **Person 1** | AI / Machine Learning | EfficientNet-B0 5-class DR classifier with two-stage transfer learning, APTOS dataset pipeline, QWK/ROC evaluation suite, Grad-CAM XAI hook, ONNX export, FastAPI microservice, and calibrated clinical fallback engine. |
| **Person 2** | Computer Vision / XAI | 10-Phase MATLAB clinical screening pipeline, 4-point Image Quality Assessment, CIE L\*a\*b\* CLAHE enhancement, Optic Disc/Fovea localization, vascular arcade segmentation, quantitative lesion candidate extraction (MA, HE, EX, NV with OD masking), and Simulink SimEvents capacity model. |
| **Person 3** | Full-Stack & Telemedicine | Precision Clinical web dashboard (HTML5/CSS3/ES6), zero-dependency native REST server, thread-safe SQLite datastore with audit trail, clinical consultation report generator, Python discrete-event telemedicine simulator (100K+ pts/yr), one-click launch scripts, and comprehensive test suite (35 tests). |

<br>

## 🧪 Testing

```bash
# Run complete test suite (35 tests)
python -m unittest discover -s tests -v

# Run diagnostic self-test only
python run_dashboard.py --test

# Run batch evaluation on APTOS dataset
python run_on_aptos.py --data_dir /path/to/aptos/test_images

# Run FastAPI test suite
cd api && python test_api.py
```

**Test Coverage:**
- ✅ Image Quality Assessment (blur, illumination, contrast, FOV)
- ✅ CLAHE Enhancement pipeline
- ✅ AI Prediction for all 5 DR levels (0–4)
- ✅ Grad-CAM heatmap generation
- ✅ Lesion candidate detection & clinical concordance
- ✅ SQLite database CRUD + lesion persistence
- ✅ REST API endpoints (screening, review, report, health)
- ✅ Telemedicine simulation (all 4 scenarios)
- ✅ Clinical feature verification (12 features)
- ✅ OculisAI branding consistency

<br>

## ⚙️ Technical Stack

| Layer | Technology |
|:---|:---|
| **Deep Learning** | PyTorch 2.0+, EfficientNet-B0, torchvision |
| **Computer Vision** | OpenCV, NumPy, Pillow, CIE L\*a\*b\* color science |
| **Web Frontend** | Vanilla HTML5 / CSS3 / ES6 (zero framework dependency) |
| **Backend API** | Python `http.server` (zero-dep) + FastAPI (optional) |
| **Database** | SQLite3 (thread-safe, built-in) |
| **Signal Processing** | MATLAB R2024a + Simulink + SimEvents |
| **Export** | ONNX Runtime, HTML report renderer |
| **CI / Testing** | Python `unittest`, 35 automated test cases |

<br>

## 📜 Regulatory Alignment

| Standard | Status |
|:---|:---|
| **CDSCO SaMD Class B** | ✅ Designed per CDSCO Software as Medical Device guidelines |
| **Human-in-the-Loop** | ✅ AI provides triage recommendations; ophthalmologist retains diagnostic authority |
| **ABDM Compatible** | ✅ Standardized patient IDs (`PAT-YYYY-XXXX`) and JSON payloads compatible with Ayushman Bharat Digital Mission |
| **Audit Trail** | ✅ All predictions, overrides, and reviews timestamped in SQLite |
| **ICDR Compliant** | ✅ 5-class grading per International Clinical Diabetic Retinopathy scale |

<br>

## 📐 Mathematical Foundations

<details>
<summary><strong>Image Quality Assessment</strong></summary>

**Focus Score** — Laplacian variance:
$$\text{Focus} = \text{Var}(\nabla^2 I) = \text{Var}\left(\frac{\partial^2 I}{\partial x^2} + \frac{\partial^2 I}{\partial y^2}\right)$$
Threshold: Var < 50.0 → Blurred

**RMS Contrast:**
$$C_{rms} = \sqrt{\frac{1}{MN}\sum_{i=1}^M \sum_{j=1}^N \left(I(i,j) - \mu\right)^2}$$
Threshold: $C_{rms} \ge 22.0$

</details>

<details>
<summary><strong>Grad-CAM Formulation</strong></summary>

$$\alpha_k^c = \frac{1}{Z} \sum_{i} \sum_{j} \frac{\partial y^c}{\partial A_{i,j}^k}$$
$$L_{\text{Grad-CAM}}^c = \text{ReLU}\left(\sum_k \alpha_k^c A^k\right)$$

</details>

<details>
<summary><strong>Telemedicine Queuing Model</strong></summary>

**Hourly Arrival Rate:**
$$\lambda_{\text{hourly}} = \frac{\text{Annual Patients}}{250 \times 8} = \frac{100{,}000}{2{,}000} = 50 \text{ pts/hr}$$

**Doctor Queue Utilization:**
$$\rho_{\text{doc}} = \frac{\lambda \times \text{Referable Rate}}{c_{\text{doc}} \times \mu_{\text{doc}}}$$

</details>

<br>

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>Built with ❤️ for the Smart India Hackathon</strong><br>
  <em>Bringing sight-saving AI to every corner of India</em>
</p>

<p align="center">
  <sub>OculisAI v2.4.0 · CDSCO SaMD Class B Aligned · ABDM Ready · 35 Tests Passing</sub>
</p>
