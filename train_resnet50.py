"""
Fine-tuning de ResNet-50 (pré-entraîné ImageNet) sur le Kaggle Oral Image Dataset (6 classes).

Usage :
    python train_resnet50.py                      # entraînement + évaluation sur le test
    python train_resnet50.py predict photo.jpg    # top-3 + carte Grad-CAM pour une image

Prérequis :
    pip install torch torchvision scikit-learn matplotlib pillow grad-cam   (torch >= 2.3)

Structure attendue du dataset (un dossier par classe) :
    DATA_DIR/
        Calculus/        *.jpg
        Caries/          *.jpg
        Hypodontia/      *.jpg
        Mouth Ulcer/     *.jpg
        Normal/          *.jpg
        Tooth Discoloration/ *.jpg
Si le dataset téléchargé contient déjà des sous-dossiers train/test, fusionnez-les d'abord :
le script refait lui-même un split stratifié train / val / test.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, models, transforms

# ----------------------------- Configuration -----------------------------
DATA_DIR = Path("data/oral_images")      # <-- à adapter
OUT_DIR = Path("outputs")
IMG_SIZE = 224
BATCH_SIZE = 32                           # descendre à 16 si "CUDA out of memory"
NUM_WORKERS = 2                           # mettre 0 en cas de problème sous Windows
SEED = 42
EPOCHS_HEAD = 5                           # phase 1 : seule la dernière couche est entraînée
EPOCHS_FINETUNE = 15                      # phase 2 : tout le réseau est entraîné
LR_HEAD = 1e-3
LR_BACKBONE = 1e-4
MODEL_PATH = OUT_DIR / "resnet50_dental.pt"
CLASSES_PATH = OUT_DIR / "classes.json"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]  # normalisation ImageNet


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


# ----------------------------- Données -----------------------------
def get_transforms():
    train_tf = transforms.Compose([
        transforms.RandomResizedCrop(IMG_SIZE, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])
    eval_tf = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])
    return train_tf, eval_tf


def file_hash(path: str) -> str:
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


def make_splits(full_ds):
    """Split stratifié 70/15/15 + retrait des doublons exacts qui fuiraient du train vers val/test."""
    targets = np.array(full_ds.targets)
    idx = np.arange(len(targets))
    train_idx, tmp_idx = train_test_split(idx, test_size=0.30, stratify=targets, random_state=SEED)
    val_idx, test_idx = train_test_split(
        tmp_idx, test_size=0.50, stratify=targets[tmp_idx], random_state=SEED
    )

    # Détection de fuites : mêmes fichiers (octets identiques) dans train et val/test
    hashes = {i: file_hash(full_ds.samples[i][0]) for i in idx}
    eval_hashes = {hashes[i] for i in np.concatenate([val_idx, test_idx])}
    leaked = [i for i in train_idx if hashes[i] in eval_hashes]
    if leaked:
        print(f"[ATTENTION] {len(leaked)} images du train sont des doublons exacts de val/test : retirées du train.")
        leaked_set = set(leaked)
        train_idx = np.array([i for i in train_idx if i not in leaked_set])
    else:
        print("Aucun doublon exact entre train et val/test.")
    print("Note : seuls les doublons exacts sont détectés ; vérifiez aussi les quasi-doublons (ex. imagehash).")
    return train_idx, val_idx, test_idx


def build_loaders():
    train_tf, eval_tf = get_transforms()
    ds_train = datasets.ImageFolder(DATA_DIR, transform=train_tf)
    ds_eval = datasets.ImageFolder(DATA_DIR, transform=eval_tf)
    classes = ds_train.classes
    print("Classes :", classes)

    train_idx, val_idx, test_idx = make_splits(ds_train)
    counts = np.bincount(np.array(ds_train.targets)[train_idx], minlength=len(classes))
    print("Images par classe (train) :", dict(zip(classes, counts.tolist())))

    pin = DEVICE.type == "cuda"
    train_loader = DataLoader(Subset(ds_train, train_idx), batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=NUM_WORKERS, pin_memory=pin)
    val_loader = DataLoader(Subset(ds_eval, val_idx), batch_size=BATCH_SIZE, shuffle=False,
                            num_workers=NUM_WORKERS, pin_memory=pin)
    test_loader = DataLoader(Subset(ds_eval, test_idx), batch_size=BATCH_SIZE, shuffle=False,
                             num_workers=NUM_WORKERS, pin_memory=pin)
    return train_loader, val_loader, test_loader, classes, counts


# ----------------------------- Modèle -----------------------------
def build_model(num_classes: int) -> nn.Module:
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
    model.fc = nn.Sequential(nn.Dropout(0.3), nn.Linear(model.fc.in_features, num_classes))
    return model.to(DEVICE)


def set_backbone_trainable(model: nn.Module, trainable: bool) -> None:
    for name, p in model.named_parameters():
        if not name.startswith("fc."):
            p.requires_grad = trainable


# ----------------------------- Entraînement -----------------------------
def run_epoch(model, loader, criterion, optimizer=None, scaler=None):
    train = optimizer is not None
    model.train(train)
    total_loss, preds_all, labels_all = 0.0, [], []
    for x, y in loader:
        x, y = x.to(DEVICE, non_blocking=True), y.to(DEVICE, non_blocking=True)
        with torch.set_grad_enabled(train):
            with torch.autocast(device_type=DEVICE.type, enabled=DEVICE.type == "cuda"):
                out = model(x)
                loss = criterion(out, y)
            if train:
                optimizer.zero_grad(set_to_none=True)
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
        total_loss += loss.item() * x.size(0)
        preds_all.extend(out.argmax(1).cpu().tolist())
        labels_all.extend(y.cpu().tolist())
    n = len(labels_all)
    acc = float(np.mean(np.array(preds_all) == np.array(labels_all)))
    f1 = f1_score(labels_all, preds_all, average="macro")
    return total_loss / n, acc, f1


def train():
    set_seed(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    train_loader, val_loader, test_loader, classes, counts = build_loaders()
    CLASSES_PATH.write_text(json.dumps(classes))

    model = build_model(len(classes))
    # Poids inversement proportionnels à la fréquence : compense le déséquilibre (Caries, Ulcer...)
    weights = torch.tensor(counts.sum() / (len(classes) * counts), dtype=torch.float32).to(DEVICE)
    criterion = nn.CrossEntropyLoss(weight=weights)
    scaler = torch.amp.GradScaler("cuda", enabled=DEVICE.type == "cuda")

    best_f1, history = 0.0, []

    def fit(epochs, optimizer, scheduler, phase):
        nonlocal best_f1
        for ep in range(1, epochs + 1):
            tr_loss, tr_acc, tr_f1 = run_epoch(model, train_loader, criterion, optimizer, scaler)
            va_loss, va_acc, va_f1 = run_epoch(model, val_loader, criterion)
            if scheduler:
                scheduler.step()
            history.append((phase, ep, tr_loss, va_loss, tr_f1, va_f1))
            print(f"[{phase}] epoch {ep:02d}/{epochs} | train loss {tr_loss:.3f} F1 {tr_f1:.3f} "
                  f"| val loss {va_loss:.3f} acc {va_acc:.3f} macro-F1 {va_f1:.3f}")
            if va_f1 > best_f1:  # le meilleur modèle est choisi sur le macro-F1 de validation
                best_f1 = va_f1
                torch.save(model.state_dict(), MODEL_PATH)

    # Phase 1 : on n'entraîne que la tête de classification
    set_backbone_trainable(model, False)
    opt = torch.optim.AdamW(model.fc.parameters(), lr=LR_HEAD, weight_decay=1e-4)
    fit(EPOCHS_HEAD, opt, None, "tête")

    # Phase 2 : fine-tuning complet avec un learning rate plus faible pour le corps du réseau
    set_backbone_trainable(model, True)
    backbone = [p for n, p in model.named_parameters() if not n.startswith("fc.")]
    opt = torch.optim.AdamW([
        {"params": backbone, "lr": LR_BACKBONE},
        {"params": model.fc.parameters(), "lr": LR_HEAD / 10},
    ], weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS_FINETUNE)
    fit(EPOCHS_FINETUNE, opt, sched, "fine-tuning")

    plot_history(history)
    evaluate_test(model, test_loader, classes)


# ----------------------------- Évaluation -----------------------------
def plot_history(history):
    f1_val = [h[5] for h in history]
    loss_tr, loss_va = [h[2] for h in history], [h[3] for h in history]
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(loss_tr, label="train"); ax[0].plot(loss_va, label="val"); ax[0].set_title("Loss"); ax[0].legend()
    ax[1].plot(f1_val); ax[1].set_title("Macro-F1 (validation)")
    for a in ax:
        a.set_xlabel("epoch (phases 1 + 2 cumulées)")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "training_curves.png", dpi=150)
    plt.close(fig)


def evaluate_test(model, test_loader, classes):
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()
    preds, labels = [], []
    with torch.no_grad():
        for x, y in test_loader:
            out = model(x.to(DEVICE))
            preds.extend(out.argmax(1).cpu().tolist())
            labels.extend(y.tolist())

    print("\n=== Résultats sur le jeu de TEST ===")
    report = classification_report(labels, preds, target_names=classes, digits=3)
    print(report)
    (OUT_DIR / "classification_report.txt").write_text(report)

    cm = confusion_matrix(labels, preds)
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(classes))); ax.set_xticklabels(classes, rotation=45, ha="right")
    ax.set_yticks(range(len(classes))); ax.set_yticklabels(classes)
    ax.set_xlabel("Prédit"); ax.set_ylabel("Réel"); ax.set_title("Matrice de confusion (test)")
    for i in range(len(classes)):
        for j in range(len(classes)):
            ax.text(j, i, cm[i, j], ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.colorbar(im)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "confusion_matrix.png", dpi=150)
    plt.close(fig)


# ----------------------------- Inférence + Grad-CAM -----------------------------
def predict(image_path: str):
    from PIL import Image
    from pytorch_grad_cam import GradCAM
    from pytorch_grad_cam.utils.image import show_cam_on_image

    classes = json.loads(CLASSES_PATH.read_text())
    model = build_model(len(classes))
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()

    _, eval_tf = get_transforms()
    img = Image.open(image_path).convert("RGB")
    x = eval_tf(img).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        probs = torch.softmax(model(x), dim=1)[0].cpu()
    top3 = torch.topk(probs, k=min(3, len(classes)))
    print("Top-3 :")
    for p, i in zip(top3.values.tolist(), top3.indices.tolist()):
        print(f"  {classes[i]:<22} {p:.1%}")

    # Grad-CAM sur la dernière couche convolutive de ResNet-50
    cam = GradCAM(model=model, target_layers=[model.layer4[-1]])
    heat = cam(input_tensor=x, targets=None)[0]            # cible = classe prédite
    rgb = np.asarray(img.resize((IMG_SIZE, IMG_SIZE)), dtype=np.float32) / 255.0
    overlay = show_cam_on_image(rgb, heat, use_rgb=True)
    out_path = OUT_DIR / "gradcam_result.png"
    Image.fromarray(overlay).save(out_path)
    print(f"Carte Grad-CAM enregistrée : {out_path}")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "predict":
        predict(sys.argv[2])
    else:
        print(f"Appareil utilisé : {DEVICE}")
        train()
