"""
ai/model.py - Model Architecture Definition for Person 1 (Diabetic Retinopathy Classification)
"""
import os
import json

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

def load_class_names():
    class_names_path = os.path.join(MODEL_DIR, 'class_names.json')
    if not os.path.exists(class_names_path):
        # Fallback to deliverable_person3 if run from another dir
        alt_path = os.path.join(os.path.dirname(__file__), '..', 'deliverable_person3', 'class_names.json')
        if os.path.exists(alt_path):
            class_names_path = alt_path
    if os.path.exists(class_names_path):
        with open(class_names_path, 'r') as f:
            data = json.load(f)
            return {int(k): v for k, v in data.items()}
    return {
        0: "No DR",
        1: "Mild NPDR",
        2: "Moderate NPDR",
        3: "Severe NPDR",
        4: "Proliferative DR"
    }

CLASS_NAMES = load_class_names()

def build_model(num_classes=5, freeze_backbone=True):
    """
    Build EfficientNet-B0 for 5-class DR classification (Person 1 Training Engine).
    Args:
        num_classes: Number of DR severity levels (5)
        freeze_backbone: If True, freeze all backbone layers (Stage 1)
    Returns:
        model, device
    """
    import torch
    import torch.nn as nn
    from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    weights = EfficientNet_B0_Weights.IMAGENET1K_V1
    model = efficientnet_b0(weights=weights)

    # Replace classifier head: 1000 -> 5 classes
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)

    if freeze_backbone:
        for name, param in model.named_parameters():
            if 'classifier' not in name:
                param.requires_grad = False

    model = model.to(device)
    return model, device

def unfreeze_layers(model, num_blocks_to_unfreeze=3):
    """
    Stage 2: Unfreeze the last `num_blocks_to_unfreeze` blocks for fine-tuning.
    EfficientNet-B0 feature blocks 0-6. Unfreeze from the end.
    """
    blocks_to_unfreeze = ['6', '5', '4'][:num_blocks_to_unfreeze]
    for name, param in model.named_parameters():
        if any(f'features.{b}' in name for b in blocks_to_unfreeze):
            param.requires_grad = True

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"Trainable params: {trainable:,} / {total:,} ({100*trainable/total:.1f}%)")
    return model

def get_efficientnet_model(model_path=None, device="cpu"):
    """
    Loads Person 1's trained EfficientNet-B0 PyTorch model if torch is available.
    """
    try:
        import torch
        import torch.nn as nn
        from torchvision.models import efficientnet_b0

        if model_path is None:
            model_path = os.path.join(MODEL_DIR, 'best_model.pth')
            if not os.path.exists(model_path):
                alt_path = os.path.join(os.path.dirname(__file__), '..', 'deliverable_person3', 'best_model.pth')
                if os.path.exists(alt_path):
                    model_path = alt_path

        model = efficientnet_b0(weights=None)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, 5)

        if os.path.exists(model_path):
            state_dict = torch.load(model_path, map_location=device)
            model.load_state_dict(state_dict)
            model.to(device)
            model.eval()
            return model
        else:
            print(f"[Model Warning] Weights not found at {model_path}")
            return None
    except ImportError:
        return None
