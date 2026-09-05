# Integration Contract: Person 1 (Model Engine) & Person 2 (Preprocessing & Explainability)

This document defines the interface and data contracts connecting the retinal fundus image preprocessing, quality validation, AI prediction engine, and Grad-CAM explainability pipeline.

---

## 1. Architecture Flow

```text
Raw Fundus Image
       │
       ▼
┌─────────────────────────┐
│     PERSON 2 CODE       │
│     Quality Check       │ ──[failed]──► Return "Recapture recommended" + issues
└───────────┬─────────────┘
            │ [passed]
            ▼
┌─────────────────────────┐
│     PERSON 2 CODE       │
│     Enhancement         │ ──► Returns: 224x224 RGB PIL Image (CLAHE, etc.)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│     PERSON 1 (AI)       │
│     predict()           │ ──► Returns: {level, label, scores, referable}
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│     PERSON 2 / SHARED   │
│     generate_gradcam()  │ ──► Returns: Grad-CAM heatmap overlay (PIL Image / numpy)
└─────────────────────────┘
```

---

## 2. Component Specifications

### 2.1 Quality Check (`check_quality`)
- **Author**: Person 2
- **Input**: `image` (`PIL.Image.Image`) — Raw fundus photograph
- **Output**: `dict`
```python
{
    "passed": bool,        # True if image quality is clinically acceptable
    "score": float,        # 0.0 to 1.0 overall quality score
    "issues": list[str]    # e.g., ["blur_detected", "low_contrast", "underexposed"]
}
```

### 2.2 Image Enhancement (`enhance_image`)
- **Author**: Person 2
- **Input**: `image` (`PIL.Image.Image`) — Raw fundus photograph
- **Output**: `PIL.Image.Image` — Preprocessed, CLAHE enhanced, RGB, sized (224, 224)

### 2.3 DR Model Prediction (`predict`)
- **Author**: Person 1
- **Input**: `image` (`PIL.Image.Image` or path or numpy array)
- **Output**: `dict`
```python
{
    "level": int,          # 0: No DR, 1: Mild, 2: Moderate, 3: Severe, 4: Proliferative
    "label": str,          # e.g., "Moderate NPDR"
    "scores": dict,        # { "No DR": 0.02, "Mild NPDR": 0.15, ... }
    "referable": bool      # True if level >= 2
}
```

### 2.4 Grad-CAM Visualization (`generate_gradcam`)
- **Input**: `model` (PyTorch model or path to `best_model.pth`), `image` (enhanced PIL Image or path)
- **Output**: Heatmap overlay image (RGB numpy array / PIL Image)

---

## 3. Deliverables Provided by Person 1
- `models/best_model.pth`: Trained EfficientNet-B0 weights
- `models/class_names.json`: Grade index to label mapping
- `models/config.json`: Model configuration & normalization stats
- `ai/predict.py`: Inference engine & predictor class
- `vision/gradcam.py`: Grad-CAM extraction module
- `pipeline.py`: Unified end-to-end runner orchestrating Quality -> Enhancement -> Prediction -> Grad-CAM
