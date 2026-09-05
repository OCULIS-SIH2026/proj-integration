# ai/train.py
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score
import numpy as np
from collections import Counter

def compute_class_weights(labels, num_classes=5):
    """Compute inverse-frequency class weights for CrossEntropyLoss."""
    counts = Counter(labels)
    total = sum(counts.values())
    weights = []
    for c in range(num_classes):
        weights.append(total / (num_classes * counts.get(c, 1)))
    return torch.tensor(weights, dtype=torch.float32)

def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    all_preds = []
    all_labels = []

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, preds = torch.max(outputs, 1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

    epoch_loss = running_loss / len(loader.dataset)
    epoch_acc = accuracy_score(all_labels, all_preds)
    return epoch_loss, epoch_acc

def validate(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    all_preds = []
    all_labels = []
    all_probs = []

    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)
            probs = torch.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())

    epoch_loss = running_loss / len(loader.dataset)
    epoch_acc = accuracy_score(all_labels, all_preds)
    return epoch_loss, epoch_acc, all_preds, all_labels, all_probs

def train(model, device, train_loader, val_loader, config):
    """
    Two-stage training:
    Stage 1: Frozen backbone, train classifier only
    Stage 2: Unfreeze last N blocks, fine-tune with lower LR
    """
    results = {}

    # --- Stage 1: Train classifier only ---
    print("\n" + "="*50)
    print("STAGE 1: Training classifier (frozen backbone)")
    print("="*50)

    # Compute class weights from training data
    all_train_labels = []
    for _, labels in train_loader:
        all_train_labels.extend(labels.numpy())
    class_weights = compute_class_weights(all_train_labels).to(device)

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=config['stage1_lr'],
        weight_decay=config['weight_decay']
    )

    best_val_acc = 0.0
    stage1_history = []

    for epoch in range(config['stage1_epochs']):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc, _, _, _ = validate(model, val_loader, criterion, device)

        stage1_history.append({
            'epoch': epoch + 1,
            'train_loss': train_loss,
            'train_acc': train_acc,
            'val_loss': val_loss,
            'val_acc': val_acc
        })

        print(f"Epoch {epoch+1}/{config['stage1_epochs']} | "
              f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
              f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), config['model_save_path'])
            print(f"  [OK] Saved best model (val_acc={val_acc:.4f})")

    results['stage1'] = {'history': stage1_history, 'best_val_acc': best_val_acc}

    # --- Stage 2: Fine-tune with unfrozen layers ---
    print("\n" + "="*50)
    print("STAGE 2: Fine-tuning (partially unfrozen backbone)")
    print("="*50)

    # Unfreeze last 3 blocks
    from ai.model import unfreeze_layers
    unfreeze_layers(model, num_blocks_to_unfreeze=3)

    optimizer = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=config['stage2_lr'],
        weight_decay=config['weight_decay']
    )

    stage2_history = []

    for epoch in range(config['stage2_epochs']):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc, _, _, _ = validate(model, val_loader, criterion, device)

        stage2_history.append({
            'epoch': epoch + 1,
            'train_loss': train_loss,
            'train_acc': train_acc,
            'val_loss': val_loss,
            'val_acc': val_acc
        })

        print(f"Epoch {epoch+1}/{config['stage2_epochs']} | "
              f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
              f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), config['model_save_path'])
            print(f"  [OK] Saved best model (val_acc={val_acc:.4f})")

    results['stage2'] = {'history': stage2_history, 'best_val_acc': best_val_acc}

    # Load best model
    model.load_state_dict(torch.load(config['model_save_path']))

    return model, results