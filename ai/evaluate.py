# ai/evaluate.py
import torch
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score
)
import matplotlib.pyplot as plt
import seaborn as sns
import json

CLASS_NAMES = ['No DR', 'Mild NPDR', 'Moderate NPDR', 'Severe NPDR', 'Proliferative DR']

def evaluate_model(model, val_loader, device):
    """Full evaluation: confusion matrix, per-class metrics, referable DR metrics."""
    model.eval()
    all_preds = []
    all_labels = []
    all_probs = []

    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)

    # --- 5-class metrics ---
    results = {
        'accuracy': float(accuracy_score(all_labels, all_preds)),
        'macro_f1': float(f1_score(all_labels, all_preds, average='macro')),
        'weighted_f1': float(f1_score(all_labels, all_preds, average='weighted')),
        'confusion_matrix': confusion_matrix(all_labels, all_preds).tolist(),
        'per_class': {},
        'referable_dr': {}
    }

    for i in range(5):
        tp = np.sum((all_preds == i) & (all_labels == i))
        fp = np.sum((all_preds == i) & (all_labels != i))
        fn = np.sum((all_preds != i) & (all_labels == i))
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        rec  = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2*prec*rec/(prec+rec) if (prec+rec) > 0 else 0

        results['per_class'][f'class_{i}'] = {
            'name': CLASS_NAMES[i],
            'precision': float(prec),
            'recall': float(rec),
            'f1': float(f1),
            'support': int(np.sum(all_labels == i))
        }

    # --- Referable DR metrics (0,1 → Non-referable; 2,3,4 → Referable) ---
    y_true_ref = (all_labels >= 2).astype(int)
    y_pred_ref = (all_preds >= 2).astype(int)
    ref_prob = all_probs[:, 2:].sum(axis=1)  # Sum of class 2,3,4 probabilities

    tn = np.sum((y_true_ref == 0) & (y_pred_ref == 0))
    fp = np.sum((y_true_ref == 0) & (y_pred_ref == 1))
    fn = np.sum((y_true_ref == 1) & (y_pred_ref == 0))
    tp = np.sum((y_true_ref == 1) & (y_pred_ref == 1))

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

    results['referable_dr'] = {
        'sensitivity': float(sensitivity),
        'specificity': float(specificity),
        'precision': float(precision_score(y_true_ref, y_pred_ref, zero_division=0)),
        'recall': float(recall_score(y_true_ref, y_pred_ref)),
        'f1': float(f1_score(y_true_ref, y_pred_ref)),
        'roc_auc': float(roc_auc_score(y_true_ref, ref_prob)),
    }

    return results, all_labels, all_preds, all_probs

def plot_confusion_matrix(cm, save_path='artifacts/confusion_matrix.png'):
    """Plot and save confusion matrix."""
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix - DR Classification')
    plt.tight_layout()
    import os
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"[OK] Confusion matrix saved to {save_path}")

def print_report(results):
    """Print formatted evaluation report."""
    print("\n" + "="*60)
    print("EVALUATION REPORT")
    print("="*60)
    print(f"\n5-Class Accuracy:     {results['accuracy']:.4f}")
    print(f"5-Class Macro F1:     {results['macro_f1']:.4f}")
    print(f"5-Class Weighted F1:  {results['weighted_f1']:.4f}")

    print(f"\n{'-'*60}")
    print("REFERABLE DR (>= Level 2)")
    print(f"{'-'*60}")
    rd = results['referable_dr']
    print(f"Sensitivity (Recall): {rd['sensitivity']:.4f}")
    print(f"Specificity:          {rd['specificity']:.4f}")
    print(f"Precision:            {rd['precision']:.4f}")
    print(f"F1 Score:             {rd['f1']:.4f}")
    print(f"ROC-AUC:              {rd['roc_auc']:.4f}")

    print(f"\n{'-'*60}")
    print("PER-CLASS METRICS")
    print(f"{'-'*60}")
    print(f"{'Class':<22} {'Precision':>10} {'Recall':>10} {'F1':>10} {'Support':>10}")
    for i in range(5):
        pc = results['per_class'][f'class_{i}']
        print(f"{CLASS_NAMES[i]:<22} {pc['precision']:>10.4f} {pc['recall']:>10.4f} {pc['f1']:>10.4f} {pc['support']:>10}")

    # Target check
    print(f"\n{'-'*60}")
    if rd['sensitivity'] >= 0.90 and rd['specificity'] >= 0.85:
        print("[OK] MEETS SIH target: Sensitivity >= 90%, Specificity >= 85%")
    else:
        print("[!] BELOW SIH target - needs improvement")
    print("="*60)