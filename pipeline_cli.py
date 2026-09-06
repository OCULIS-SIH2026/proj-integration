"""
pipeline.py - Integrated End-to-End Fundus Analysis Pipeline

Flow:
  Raw Fundus Image
        │
        ▼
  [Person 2] Quality Check (assess_image_quality: blur, contrast, exposure, FOV)
        │
        ├─► If Failed: Early exit with "Recapture recommended"
        ▼
  [Person 2] Image Enhancement (enhance_fundus_image: Selective CLAHE, 224x224 RGB)
        │
        ▼
  [Person 1] DR Prediction Model (EfficientNet-B0 inference on models/best_model.pth)
        │
        ▼
  [Person 2 / Vision] Grad-CAM Explainability Heatmap
        │
        ▼
  [Person 2] Clinical Triage & Urgency Assessment (make_clinical_triage)
"""

import os
import sys

try:
    import numpy as np
    import cv2
    from PIL import Image
    CV_STACK_AVAILABLE = True
except ImportError:
    CV_STACK_AVAILABLE = False

from ai.predict import DRPredictor, CLASS_NAMES
from vision.gradcam import generate_gradcam

try:
    from api.pipeline_bridge import (
        assess_image_quality,
        enhance_fundus_image,
        make_clinical_triage,
        CLASS_DESCRIPTIONS
    )
except ImportError:
    CLASS_DESCRIPTIONS = {
        0: "No diabetic retinopathy detected.",
        1: "Mild NPDR: Microaneurysms only.",
        2: "Moderate NPDR: Hemorrhages, microaneurysms, hard exudates.",
        3: "Severe NPDR: 4-quadrant hemorrhages, venous beading.",
        4: "Proliferative DR: Neovascularization present."
    }

# ---------------------------------------------------------------------------
# Person 2 Contract Adapters
# ---------------------------------------------------------------------------

def check_quality(image) -> dict:
    """
    Person 2 Quality Check:
    Evaluates Sharpness, Brightness, Contrast, and FOV.
    Contract: returns {"passed": bool, "score": float, "issues": list}
    """
    res = assess_image_quality(image)
    return {
        "passed": res["is_acceptable"],
        "score": res["overall_score"],
        "issues": res["rejection_reasons"],
        "status": res["status"],
        "metrics": res["metrics"]
    }


def enhance_image(image, quality_status: str = "Borderline"):
    """
    Person 2 Image Enhancement:
    Applies selective CLAHE in LAB space and formats to (224, 224) RGB.
    """
    return enhance_fundus_image(image, quality_status=quality_status)


# ---------------------------------------------------------------------------
# Integrated Pipeline Class
# ---------------------------------------------------------------------------

class RetinaPipeline:
    def __init__(self, check_quality_fn=None, enhance_image_fn=None, model_path=None):
        """
        Initialize the complete integrated screening pipeline.

        Args:
            check_quality_fn: Function (image: PIL.Image) -> dict
            enhance_image_fn: Function (image: PIL.Image, status: str) -> PIL.Image (224x224)
            model_path: Path to best_model.pth (defaults to models/best_model.pth)
        """
        self.check_quality = check_quality_fn or check_quality
        self.enhance_image = enhance_image_fn or enhance_image
        self.predictor = DRPredictor(model_path=model_path)

    def run(self, image_input, generate_cam=True, save_cam_path=None):
        """
        Execute the full pipeline on a raw fundus image.

        Args:
            image_input: File path string or PIL.Image
            generate_cam: Whether to compute Grad-CAM overlay
            save_cam_path: Optional path to save Grad-CAM image

        Returns:
            dict with full diagnostics, clinical triage, and results
        """
        # Load raw image
        if isinstance(image_input, str):
            raw_image = Image.open(image_input).convert('RGB')
        elif isinstance(image_input, Image.Image):
            raw_image = image_input.convert('RGB')
        else:
            raw_image = Image.fromarray(image_input).convert('RGB')

        # Step 1: Person 2 Quality Check
        quality = self.check_quality(raw_image)

        if not quality.get("passed", False):
            return {
                "status": "rejected",
                "reason": "Recapture recommended",
                "quality": quality,
                "prediction": None,
                "triage": None,
                "enhanced_image": None,
                "gradcam_overlay": None
            }

        # Step 2: Person 2 Selective CLAHE Enhancement (224x224 RGB)
        enhanced_image = self.enhance_image(raw_image, quality_status=quality.get("status", "Borderline"))

        # Step 3: Person 1 DR Model Prediction (EfficientNet-B0)
        pred = self.predictor.predict(enhanced_image)

        # Step 4: Person 2 Clinical Triage Logic
        probs_list = [pred['scores'][CLASS_NAMES[i]] for i in range(5)]
        triage = make_clinical_triage(pred['level'], probs_list)

        # Step 5: Grad-CAM Explainability
        gradcam_overlay = None
        if generate_cam:
            gradcam_overlay = generate_gradcam(
                model=self.predictor.model,
                image=enhanced_image,
                save_path=save_cam_path,
                class_idx=pred['level']
            )

        return {
            "status": "success",
            "quality": quality,
            "prediction": {
                **pred,
                "description": CLASS_DESCRIPTIONS.get(pred['level'], "")
            },
            "triage": triage,
            "enhanced_image": enhanced_image,
            "gradcam_overlay": gradcam_overlay
        }


# Quick test runner
if __name__ == "__main__":
    if len(sys.argv) > 1:
        sample_img_path = sys.argv[1]
    else:
        sample_img_path = os.path.join("sample_data", "images", "sample_moderate_level2.bmp")

    print(f"\n==================================================")
    print(f"  OculisAI End-to-End Pipeline CLI Runner")
    print(f"  Target Image: {sample_img_path}")
    print(f"==================================================")

    if not os.path.exists(sample_img_path):
        print(f"[Error] Image file not found at {sample_img_path}")
        sys.exit(1)

    if CV_STACK_AVAILABLE:
        pipeline = RetinaPipeline()
        res = pipeline.run(sample_img_path, save_cam_path=os.path.join("artifacts", "integrated_pipeline_gradcam.png"))
        print(f"\nStatus:     {res['status'].upper()}")
        print(f"Quality:    {res['quality']['status']} (Score: {res['quality']['score']})")
        if res['status'] == 'success':
            pred = res['prediction']
            print(f"Diagnosis:  Level {pred['level']} ({pred['label']})")
            print(f"Referable:  {'YES - Review Needed' if pred['referable'] else 'NO - Routine'}")
            print(f"Triage:     {res['triage']['urgency']} -> {res['triage']['recommendation']}")
    else:
        from backend.pipeline import run_screening_pipeline
        res = run_screening_pipeline(sample_img_path, patient_meta={"filename": os.path.basename(sample_img_path)})
        print(f"\nStatus:     {res['status'].upper()}")
        print(f"Quality:    {res['quality']['status']} (Score: {res['quality']['overall_score']})")
        pred = res['prediction']
        print(f"Diagnosis:  Level {pred['stage']} ({pred['label']})")
        print(f"Confidence: {pred['confidence']*100:.1f}%")
        print(f"Referable:  {'YES - Review Needed' if res['triage']['is_referable'] else 'NO - Routine'}")
        print(f"Triage:     {res['triage']['urgency']} -> {res['triage']['recommendation']}")
        print(f"Lesions:    MA={res['lesions']['microaneurysms']['count']}, HE={res['lesions']['hemorrhages']['count']}, EX={res['lesions']['exudates']['count']}")

    print(f"==================================================\n")
