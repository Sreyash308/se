#!/usr/bin/env python3
"""
PlantCare AI - High-Accuracy Edge Vision Training & ONNX Export Pipeline
=========================================================================
Supports multi-dataset JSON manifests (produced by scripts/prepare_datasets.py)
as well as standard ImageFolder directories.

Features:
- Modern mobile/edge backbones via timm (MobileNetV4-Small, EfficientNet-B0,
  ConvNeXt-Atto, ConvNeXt-Femto) plus torchvision fallbacks
- Domain & class-balanced weighted sampling (boosts real-world field imagery)
- Agricultural field augmentations matching Inference 224x224 ImageNet normalization
- Linear warmup + Cosine Annealing LR + EMA weight averaging
- Dual evaluation on stratified Validation Set & held-out PlantDoc Real-World Field Test Set
- Single-file ONNX export (<25 MB) with PyTorch <-> ONNXRuntime logit parity verification

Usage:
    python scripts/train_model.py --manifest_dir data --arch mobilenetv4_conv_small --epochs 12
"""

import argparse
import copy
import json
import math
import os
import random
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import onnx
import onnxruntime as ort
import timm
import torch
import torch.nn as nn
from PIL import Image, ImageOps
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader, Dataset, Subset, WeightedRandomSampler
from torchvision import datasets, models, transforms

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

TIMM_MODEL_MAP: Dict[str, str] = {
    "mobilenetv4_conv_small": "mobilenetv4_conv_small.e2400_r224_in1k",
    "efficientnet_b0": "efficientnet_b0.ra_in1k",
    "convnext_atto": "convnext_atto.d2_in1k",
    "convnext_femto": "convnext_femto.d1_in1k",
}


class ManifestImageDataset(Dataset):
    """Dataset backed by a JSON manifest of {path, label, domain} entries."""

    def __init__(self, items: List[dict], class_to_idx: Dict[str, int], transform=None):
        self.items = items
        self.class_to_idx = class_to_idx
        self.transform = transform

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        rec = self.items[idx]
        with Image.open(rec["path"]) as im:
            img = ImageOps.exif_transpose(im).convert("RGB")
        if self.transform is not None:
            img = self.transform(img)
        return img, self.class_to_idx[rec["label"]]


class TransformSubset(Dataset):
    """Wraps a PyTorch Subset with its own dedicated transform (prevents shared-dataset mutation)."""

    def __init__(self, subset: Subset, transform=None):
        self.subset = subset
        self.transform = transform

    def __len__(self) -> int:
        return len(self.subset)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        base_idx = self.subset.indices[idx]
        path, target = self.subset.dataset.samples[base_idx]
        with Image.open(path) as im:
            img = ImageOps.exif_transpose(im).convert("RGB")
        if self.transform is not None:
            img = self.transform(img)
        return img, target


def get_transforms(img_size: int = 224):
    """
    Field-resilient training augmentations + exact inference-matched validation transform.
    Note: DiagnosisService resizes directly to (224, 224) bilinear before ImageNet normalization.
    """
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(
            img_size,
            scale=(0.60, 1.0),
            ratio=(0.8, 1.25),
            interpolation=transforms.InterpolationMode.BILINEAR,
        ),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=45),
        transforms.RandomAffine(degrees=0, translate=(0.08, 0.08), shear=8),
        transforms.ColorJitter(brightness=0.28, contrast=0.28, saturation=0.25, hue=0.06),
        transforms.RandomApply([transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 1.2))], p=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        transforms.RandomErasing(p=0.15, scale=(0.02, 0.10)),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((img_size, img_size), interpolation=transforms.InterpolationMode.BILINEAR),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])
    return train_transform, val_transform


def build_model(arch: str = "mobilenetv4_conv_small", num_classes: int = 48, drop_rate: float = 0.25) -> nn.Module:
    """Instantiates pretrained vision backbone with custom classification head."""
    arch_key = arch.lower()
    if arch_key in TIMM_MODEL_MAP:
        return timm.create_model(
            TIMM_MODEL_MAP[arch_key],
            pretrained=True,
            num_classes=num_classes,
            drop_rate=drop_rate,
        )
    if arch_key == "convnext_tiny":
        model = models.convnext_tiny(weights=models.ConvNeXt_Tiny_Weights.DEFAULT)
        in_features = model.classifier[2].in_features
        model.classifier[2] = nn.Sequential(nn.Dropout(p=drop_rate), nn.Linear(in_features, num_classes))
        return model
    if arch_key == "efficientnet_b2":
        model = models.efficientnet_b2(weights=models.EfficientNet_B2_Weights.DEFAULT)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Sequential(nn.Dropout(p=drop_rate), nn.Linear(in_features, num_classes))
        return model
    if arch_key == "mobilenet_v3":
        model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT)
        in_features = model.classifier[3].in_features
        model.classifier[3] = nn.Sequential(nn.Dropout(p=drop_rate), nn.Linear(in_features, num_classes))
        return model
    return timm.create_model(arch, pretrained=True, num_classes=num_classes, drop_rate=drop_rate)


class ModelEMA:
    """Exponential Moving Average of model parameters & buffers for stronger generalization."""

    def __init__(self, model: nn.Module, decay: float = 0.999):
        self.ema = copy.deepcopy(model).eval()
        self.decay = decay
        for p in self.ema.parameters():
            p.requires_grad_(False)

    @torch.no_grad()
    def update(self, model: nn.Module):
        msd = model.state_dict()
        for k, ema_v in self.ema.state_dict().items():
            model_v = msd[k]
            if ema_v.dtype.is_floating_point:
                ema_v.mul_(self.decay).add_(model_v, alpha=1.0 - self.decay)
            else:
                ema_v.copy_(model_v)


def evaluate(model: nn.Module, loader: DataLoader, criterion: nn.Module, device: torch.device) -> Tuple[float, float, float, float]:
    """Returns (avg_loss, top1_acc_pct, macro_f1_pct, mean_correct_conf)."""
    model.eval()
    total_loss, total = 0.0, 0
    all_preds: List[int] = []
    all_targets: List[int] = []
    correct_confs: List[float] = []

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)
            logits = model(images)
            loss = criterion(logits, labels)

            probs = torch.softmax(logits, dim=1)
            confs, preds = torch.max(probs, dim=1)

            total_loss += loss.item() * images.size(0)
            total += images.size(0)
            all_preds.extend(preds.cpu().tolist())
            all_targets.extend(labels.cpu().tolist())

            mask = (preds == labels)
            if mask.any():
                correct_confs.extend(confs[mask].cpu().tolist())

    if total == 0:
        return 0.0, 0.0, 0.0, 0.0

    acc = 100.0 * sum(int(p == t) for p, t in zip(all_preds, all_targets)) / total
    macro_f1 = 100.0 * f1_score(all_targets, all_preds, average="macro", zero_division=0)
    avg_conf = float(np.mean(correct_confs)) if correct_confs else 0.0
    return total_loss / total, acc, macro_f1, avg_conf


def evaluate_detailed(model: nn.Module, loader: DataLoader, classes: List[str], device: torch.device) -> Dict[str, object]:
    """Computes overall, per-crop/group, and per-class accuracy on the validation set."""
    model.eval()
    all_preds: List[int] = []
    all_targets: List[int] = []
    all_confs: List[float] = []

    with torch.no_grad():
        for images, labels in loader:
            logits = model(images.to(device))
            probs = torch.softmax(logits, dim=1)
            confs, preds = torch.max(probs, dim=1)
            all_preds.extend(preds.cpu().tolist())
            all_targets.extend(labels.cpu().tolist())
            all_confs.extend(confs.cpu().tolist())

    per_class = {}
    for idx, cls_name in enumerate(classes):
        idxs = [i for i, t in enumerate(all_targets) if t == idx]
        if not idxs:
            continue
        correct = sum(int(all_preds[i] == idx) for i in idxs)
        per_class[cls_name] = {
            "count": len(idxs),
            "correct": correct,
            "acc": round(100.0 * correct / len(idxs), 2),
        }

    group_accs = {}
    for prefix in ["Tomato", "Potato", "Corn", "Apple", "Grape", "Rice", "Healthy Rice", "Cotton", "Bell Pepper"]:
        idxs = [i for i, t in enumerate(all_targets) if prefix.lower() in classes[t].lower()]
        if idxs:
            correct = sum(int(all_preds[i] == all_targets[i]) for i in idxs)
            group_accs[prefix] = round(100.0 * correct / len(idxs), 2)

    sorted_cls = sorted(per_class.items(), key=lambda kv: kv[1]["acc"])
    return {
        "per_class": per_class,
        "group_accs": group_accs,
        "lowest_5_classes": sorted_cls[:5],
    }


def export_onnx_and_verify(
    model: nn.Module,
    classes: List[str],
    output_dir: Path,
    arch: str,
    metrics: dict,
):
    """Exports single-file ONNX model (<25 MB), verifies PyTorch parity, and benchmarks CPU latency."""
    model_cpu = copy.deepcopy(model).cpu().eval()
    dummy_input = torch.randn(1, 3, 224, 224, dtype=torch.float32)

    onnx_path = output_dir / "plantcare_model.onnx"
    tmp_onnx_path = output_dir / "_tmp_export.onnx"

    torch.onnx.export(
        model_cpu,
        dummy_input,
        str(tmp_onnx_path),
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=["input_tensor"],
        output_names=["logits"],
        dynamic_axes={"input_tensor": {0: "batch_size"}, "logits": {0: "batch_size"}},
        dynamo=False,
    )

    # Ensure single self-contained ONNX file (no external .data sidecar)
    onnx_model = onnx.load(str(tmp_onnx_path), load_external_data=True)
    onnx.checker.check_model(onnx_model)
    onnx.save_model(onnx_model, str(onnx_path), save_as_external_data=False)
    tmp_onnx_path.unlink(missing_ok=True)
    data_sidecar = Path(str(tmp_onnx_path) + ".data")
    data_sidecar.unlink(missing_ok=True)

    # Verify numerical parity between PyTorch and ONNXRuntime
    sess = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    test_np = np.random.randn(2, 3, 224, 224).astype(np.float32)
    with torch.no_grad():
        pt_out = model_cpu(torch.from_numpy(test_np)).numpy()
    ort_out = sess.run(None, {"input_tensor": test_np})[0]
    max_diff = float(np.max(np.abs(pt_out - ort_out)))

    # Benchmark single-image CPU inference latency
    bench_np = np.random.randn(1, 3, 224, 224).astype(np.float32)
    for _ in range(5):
        sess.run(None, {"input_tensor": bench_np})
    t0 = time.perf_counter()
    for _ in range(50):
        sess.run(None, {"input_tensor": bench_np})
    latency_ms = (time.perf_counter() - t0) * 1000.0 / 50.0

    onnx_mb = onnx_path.stat().st_size / (1024 * 1024)

    class_map_path = output_dir / "class_labels.json"
    class_map_path.write_text(json.dumps(classes, indent=2))

    config_payload = {
        "architecture": arch,
        "timm_model_id": TIMM_MODEL_MAP.get(arch.lower(), arch),
        "num_classes": len(classes),
        "image_size": 224,
        "normalization": {"mean": IMAGENET_MEAN, "std": IMAGENET_STD},
        "id2label": {str(i): c for i, c in enumerate(classes)},
        "label2id": {c: i for i, c in enumerate(classes)},
        "onnx_size_mb": round(onnx_mb, 2),
        "cpu_latency_ms": round(latency_ms, 2),
        "pytorch_onnx_max_abs_diff": round(max_diff, 7),
        "metrics": metrics,
    }
    (output_dir / "config.json").write_text(json.dumps(config_payload, indent=2))

    print(
        f"\n[ONNX Export] Path={onnx_path} | Size={onnx_mb:.2f} MB | "
        f"CPU Latency={latency_ms:.2f} ms/img | Max Parity Diff={max_diff:.2e}"
    )


def train_pipeline(
    manifest_dir: Optional[str],
    data_dir: Optional[str],
    output_dir: str = "app/models/weights",
    arch: str = "mobilenetv4_conv_small",
    epochs: int = 12,
    batch_size: int = 64,
    lr: float = 5e-4,
    weight_decay: float = 2e-2,
    num_workers: int = 4,
    device_str: str = "auto",
    seed: int = 42,
):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if device_str == "auto":
        if torch.cuda.is_available():
            device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            device = torch.device("mps")
        else:
            device = torch.device("cpu")
    else:
        device = torch.device(device_str)

    print(f"[PlantCare AI] Training on device={device} | arch={arch} | epochs={epochs} | bs={batch_size} | lr={lr}")
    train_tf, val_tf = get_transforms(img_size=224)

    field_test_loader: Optional[DataLoader] = None

    if manifest_dir:
        mdir = Path(manifest_dir)
        classes: List[str] = json.loads((mdir / "class_labels.json").read_text())
        class_to_idx = {c: i for i, c in enumerate(classes)}
        train_items = json.loads((mdir / "train_manifest.json").read_text())
        val_items = json.loads((mdir / "val_manifest.json").read_text())
        field_test_items = json.loads((mdir / "field_test_manifest.json").read_text()) if (mdir / "field_test_manifest.json").exists() else []

        train_ds = ManifestImageDataset(train_items, class_to_idx, transform=train_tf)
        val_ds = ManifestImageDataset(val_items, class_to_idx, transform=val_tf)

        # Domain & class balanced sampling weights
        class_counts = Counter(r["label"] for r in train_items)
        domain_boost = {
            "lab_plantvillage": 1.0,
            "field_corn": 2.0,
            "field_cotton": 2.0,
            "field_rice": 2.2,
            "field_plantdoc": 3.5,
        }
        sample_weights = []
        for rec in train_items:
            cls_w = (class_counts[rec["label"]] ** -0.55)
            dom_w = domain_boost.get(rec.get("domain", ""), 1.0)
            sample_weights.append(cls_w * dom_w)

        sampler = WeightedRandomSampler(
            weights=torch.DoubleTensor(sample_weights),
            num_samples=len(train_items),
            replacement=True,
        )
        dl_kwargs = {"num_workers": num_workers, "persistent_workers": (num_workers > 0)}
        if num_workers > 0:
            dl_kwargs["prefetch_factor"] = 3

        train_loader = DataLoader(
            train_ds,
            batch_size=batch_size,
            sampler=sampler,
            **dl_kwargs,
        )
        val_loader = DataLoader(
            val_ds,
            batch_size=batch_size,
            shuffle=False,
            **dl_kwargs,
        )
        if field_test_items:
            ft_ds = ManifestImageDataset(field_test_items, class_to_idx, transform=val_tf)
            field_test_loader = DataLoader(ft_ds, batch_size=batch_size, shuffle=False, **dl_kwargs)
        print(f"Dataset loaded from manifests: classes={len(classes)} | train={len(train_ds)} | val={len(val_ds)} | field_test={len(field_test_items)}")
    else:
        assert data_dir is not None, "Either --manifest_dir or --data_dir is required"
        full_dataset = datasets.ImageFolder(root=data_dir)
        classes = full_dataset.classes
        val_size = int(len(full_dataset) * 0.2)
        train_size = len(full_dataset) - val_size
        train_sub, val_sub = torch.utils.data.random_split(
            full_dataset, [train_size, val_size], generator=torch.Generator().manual_seed(seed)
        )
        train_ds = TransformSubset(train_sub, transform=train_tf)
        val_ds = TransformSubset(val_sub, transform=val_tf)
        train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers)
        val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)
        print(f"Dataset loaded from {data_dir}: classes={len(classes)} | train={len(train_ds)} | val={len(val_ds)}")

    num_classes = len(classes)
    model = build_model(arch=arch, num_classes=num_classes, drop_rate=0.25).to(device)
    ema = ModelEMA(model, decay=0.999)

    criterion = nn.CrossEntropyLoss(label_smoothing=0.06)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)

    total_steps = epochs * len(train_loader)
    warmup_steps = max(1, len(train_loader))  # 1 epoch linear warmup

    def lr_lambda(step: int) -> float:
        if step < warmup_steps:
            return float(step + 1) / float(warmup_steps)
        progress = float(step - warmup_steps) / float(max(1, total_steps - warmup_steps))
        return max(1e-3, 0.5 * (1.0 + math.cos(math.pi * progress)))

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=lr_lambda)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    ckpt_dir = Path("checkpoints")
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    best_weights_path = ckpt_dir / f"{arch}_best.pth"

    best_score = -1.0
    best_metrics = {}

    for epoch in range(1, epochs + 1):
        t0 = time.time()
        model.train()
        train_loss, train_correct, train_total = 0.0, 0, 0

        for step_idx, (images, labels) in enumerate(train_loader):
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad(set_to_none=True)
            logits = model(images)
            loss = criterion(logits, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
            optimizer.step()
            scheduler.step()
            ema.update(model)

            train_loss += loss.item() * images.size(0)
            preds = torch.argmax(logits, dim=1)
            train_correct += int((preds == labels).sum().item())
            train_total += images.size(0)

            if (step_idx + 1) % 250 == 0:
                print(
                    f"  Epoch {epoch:02d} step {step_idx + 1}/{len(train_loader)} "
                    f"loss={train_loss / train_total:.4f} acc={100.0 * train_correct / train_total:.2f}% "
                    f"lr={optimizer.param_groups[0]['lr']:.2e}",
                    flush=True,
                )

        train_acc = 100.0 * train_correct / max(1, train_total)
        avg_train_loss = train_loss / max(1, train_total)

        # Evaluate both raw model and EMA model on validation
        raw_loss, raw_acc, raw_f1, raw_conf = evaluate(model, val_loader, criterion, device)
        ema_loss, ema_acc, ema_f1, ema_conf = evaluate(ema.ema, val_loader, criterion, device)

        use_ema = ema_acc >= raw_acc
        eval_model = ema.ema if use_ema else model
        val_loss, val_acc, val_f1, val_conf = (ema_loss, ema_acc, ema_f1, ema_conf) if use_ema else (raw_loss, raw_acc, raw_f1, raw_conf)

        ft_msg = ""
        ft_acc, ft_f1 = None, None
        if field_test_loader is not None:
            _, ft_acc, ft_f1, ft_conf = evaluate(eval_model, field_test_loader, criterion, device)
            ft_msg = f" | FieldTest Acc={ft_acc:.2f}% F1={ft_f1:.2f}%"

        elapsed = time.time() - t0
        tag = "EMA" if use_ema else "RAW"
        print(
            f"Epoch [{epoch:02d}/{epochs:02d}] ({elapsed:.1f}s) | "
            f"Train Loss={avg_train_loss:.4f} Acc={train_acc:.2f}% | "
            f"Val({tag}) Loss={val_loss:.4f} Acc={val_acc:.2f}% MacroF1={val_f1:.2f}% Conf={val_conf:.3f}"
            f"{ft_msg}",
            flush=True,
        )

        # Combined selection score balancing Val Acc and Macro-F1
        score = 0.7 * val_acc + 0.3 * val_f1
        if score > best_score:
            best_score = score
            best_metrics = {
                "best_epoch": epoch,
                "variant": tag,
                "val_top1_acc": round(val_acc, 2),
                "val_macro_f1": round(val_f1, 2),
                "val_mean_correct_confidence": round(val_conf, 3),
                "field_test_top1_acc": round(ft_acc, 2) if ft_acc is not None else None,
                "field_test_macro_f1": round(ft_f1, 2) if ft_f1 is not None else None,
            }
            torch.save(eval_model.state_dict(), best_weights_path)
            print(f"  * Best checkpoint saved! Val Acc={val_acc:.2f}% MacroF1={val_f1:.2f}%", flush=True)

    print(f"\nTraining complete! Best metrics: {best_metrics}")

    best_model = build_model(arch=arch, num_classes=num_classes, drop_rate=0.0)
    best_model.load_state_dict(torch.load(best_weights_path, map_location="cpu"))
    best_model.to(device)
    detailed = evaluate_detailed(best_model, val_loader, classes, device)
    best_metrics["group_val_acc"] = detailed["group_accs"]
    best_metrics["lowest_5_val_classes"] = detailed["lowest_5_classes"]
    print(f"Group Validation Accuracies: {detailed['group_accs']}")
    print(f"Lowest 5 Val Classes: {detailed['lowest_5_classes']}")

    export_onnx_and_verify(best_model, classes=classes, output_dir=out_path, arch=arch, metrics=best_metrics)

    # Explicitly release DataLoader worker pools to avoid macOS spawn hang at exit
    for loader in (train_loader, val_loader, field_test_loader):
        if loader is not None and getattr(loader, "_iterator", None) is not None:
            loader._iterator._shutdown_workers()
            loader._iterator = None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PlantCare AI - Model Training Pipeline")
    parser.add_argument("--manifest_dir", type=str, default=None, help="Directory with train/val manifests")
    parser.add_argument("--data_dir", type=str, default=None, help="Fallback ImageFolder dataset directory")
    parser.add_argument("--output_dir", type=str, default="app/models/weights", help="Directory to save ONNX model")
    parser.add_argument(
        "--arch",
        type=str,
        default="mobilenetv4_conv_small",
        choices=["mobilenetv4_conv_small", "efficientnet_b0", "convnext_atto", "convnext_femto", "convnext_tiny", "efficientnet_b2", "mobilenet_v3"],
    )
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--num_workers", type=int, default=8)
    parser.add_argument("--device", type=str, default="auto")

    args = parser.parse_args()
    train_pipeline(
        manifest_dir=args.manifest_dir,
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        arch=args.arch,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        num_workers=args.num_workers,
        device_str=args.device,
    )
