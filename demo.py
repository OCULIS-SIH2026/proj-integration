"""
OCULIS — Interactive Local Demo
Run this script to test DR screening and Grad-CAM on any fundus image.

Usage:
    python demo.py
    python demo.py path/to/your_fundus_image.jpg
"""
import sys
import os
import json
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import numpy as np
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

from ai.predict import predict
from vision.gradcam import generate_gradcam

def main():
    # 1. Determine image path
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        sample_cand = os.path.join("sample_data", "images", "sample_moderate_level2.bmp")
        if os.path.exists(sample_cand):
            image_path = sample_cand
        else:
            image_path = "test_fundus.jpg"
            if not os.path.exists(image_path) and PIL_AVAILABLE and CV2_AVAILABLE:
                img = np.ones((512, 512, 3), dtype=np.uint8) * 120
                cv2.circle(img, (256, 256), 200, (60, 40, 20), -1)  # fundus disc
                cv2.circle(img, (200, 256), 30, (180, 200, 220), -1)  # optic disc
                Image.fromarray(img).save(image_path)
                print(f"Created sample image: {image_path}")

    print("\n" + "=" * 60)
    print(f"  OCULIS AI RETINAL SCREENING - DEMO")
    print(f"  Input Image: {image_path}")
    print("=" * 60)

    # 2. Run Inference
    print("\n[1/2] Running Deep Learning Inference...")
    result = predict(image_path)

    print("\n" + "-" * 40)
    print(f"  DIAGNOSIS:    {result['label'].upper()} (Level {result['level']})")
    print(f"  REFERABLE:    {'YES - Ophthalmologist Review Needed' if result['referable'] else 'NO - Normal / Non-Referable'}")
    print("-" * 40)
    print("\n  Class Probabilities:")
    for cls_name, prob in result['scores'].items():
        bar = "#" * int(prob * 30)
        print(f"    {cls_name:<18} : {prob*100:>5.1f}%  {bar}")

    # 3. Generate Grad-CAM Heatmap
    print("\n[2/2] Generating Grad-CAM Explainability Heatmap...")
    os.makedirs("artifacts", exist_ok=True)
    gradcam_output = os.path.join("artifacts", "gradcam_output.png")
    generate_gradcam("models/best_model.pth", image_path, save_path=gradcam_output)

    print("\n" + "=" * 60)
    print(f"  [SUCCESS] Results saved!")
    print(f"  Heatmap Overlay : {gradcam_output}")
    print(f"  Confusion Matrix: artifacts/confusion_matrix.png")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
