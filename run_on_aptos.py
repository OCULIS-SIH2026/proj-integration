#!/usr/bin/env python3
"""
Run inference on APTOS sample images + generate Grad-CAM attention maps.
Usage:
    python run_on_aptos.py                    # all images
    python run_on_aptos.py --class 2          # only class 2 (Moderate)
    python run_on_aptos.py --limit 5          # first 5 images
"""
import os
import sys
import json
import argparse
from pathlib import Path

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from PIL import Image
    import numpy as np
    import cv2
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ai.predict import predict
from vision.gradcam import generate_gradcam


def find_images(root_dir):
    """Find all PNG/JPG/BMP images recursively."""
    root = Path(root_dir)
    exts = ('.png', '.jpg', '.jpeg', '.bmp', '.PNG', '.JPG', '.JPEG', '.BMP')
    return sorted([p for p in root.rglob('*') if p.suffix.lower() in exts])


def parse_class_from_filename(fname):
    """Extract class from filename like 'class2_000c1434d8d7.png' or 'sample_moderate_level2.bmp' -> 2"""
    import re
    match = re.search(r'(?:class|level|stage)[-_ ]*([0-4])', fname.lower())
    if match:
        return int(match.group(1))
    return None


def main():
    parser = argparse.ArgumentParser(description='Run DR inference + Grad-CAM on APTOS/sample images')
    parser.add_argument('--input', default='sample_data/images', help='Input directory')
    parser.add_argument('--output', default='artifacts/aptos_results', help='Output directory')
    parser.add_argument('--class', type=int, dest='class_filter', help='Filter by class (0-4)')
    parser.add_argument('--limit', type=int, help='Limit number of images')
    parser.add_argument('--no-gradcam', action='store_true', help='Skip Grad-CAM generation')
    args = parser.parse_args()

    # Setup
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'gradcam').mkdir(exist_ok=True)
    (output_dir / 'predictions.json').write_text('')  # create empty

    # Find images
    images = find_images(input_dir)
    if not images:
        print(f"No images found in {input_dir}")
        return

    # Filter by class if specified
    if args.class_filter is not None:
        images = [p for p in images if parse_class_from_filename(p.name) == args.class_filter]
        print(f"Filtered to class {args.class_filter}: {len(images)} images")

    if args.limit:
        images = images[:args.limit]

    print(f"Processing {len(images)} images...")
    print("-" * 60)

    results = []
    class_names = ['No DR', 'Mild NPDR', 'Moderate NPDR', 'Severe NPDR', 'Proliferative DR']

    for i, img_path in enumerate(images):
        try:
            # Load image
            if PIL_AVAILABLE:
                pil_img = Image.open(img_path).convert('RGB')
                cam_input = pil_img
            else:
                cam_input = str(img_path)
            
            # Predict
            result = predict(str(img_path))
            
            # Extract true class from filename
            true_class = parse_class_from_filename(img_path.name)
            
            # Print result
            match = "✓" if true_class is not None and result['level'] == true_class else "✗"
            print(f"[{i+1}/{len(images)}] {img_path.name}")
            print(f"  True: {class_names[true_class] if true_class is not None else 'Unknown'}")
            print(f"  Pred: {result['label']} (level {result['level']}) {match}")
            print(f"  Referable: {result['referable']}")
            conf_score = result.get('confidence', result.get('scores', {}).get(result['label'], 0.8))
            print(f"  Confidence: {conf_score:.3f}")
            
            # Generate Grad-CAM
            if not args.no_gradcam:
                gradcam_path = output_dir / 'gradcam' / f"{img_path.stem}_gradcam.jpg"
                overlay = generate_gradcam(
                    "models/best_model.pth",
                    cam_input,
                    save_path=str(gradcam_path),
                    class_idx=result['level']
                )
                print(f"  Grad-CAM: {gradcam_path.name}")
            
            # Store result
            result['file'] = img_path.name
            result['true_class'] = true_class
            result['correct'] = (true_class is not None and result['level'] == true_class)
            results.append(result)
            
        except Exception as e:
            print(f"  ERROR: {e}")
        
        print()

    # Save predictions JSON
    with open(output_dir / 'predictions.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Summary
    if results:
        correct = sum(1 for r in results if r['correct'])
        total = len(results)
        print("-" * 60)
        print(f"SUMMARY: {correct}/{total} correct ({100*correct/total:.1f}%)")
        
        # Per-class breakdown
        for c in range(5):
            class_results = [r for r in results if r['true_class'] == c]
            if class_results:
                class_correct = sum(1 for r in class_results if r['correct'])
                print(f"  Class {c} ({class_names[c]}): {class_correct}/{len(class_results)} correct")
        
        referable = sum(1 for r in results if r['referable'])
        print(f"  Referable predicted: {referable}/{total}")

    print(f"\nResults saved to: {output_dir}")
    print(f"  predictions.json")
    if not args.no_gradcam:
        print(f"  gradcam/*.jpg")


if __name__ == '__main__':
    main()