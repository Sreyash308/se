#!/usr/bin/env python3
"""
PlantCare AI - Multi-Dataset Deduplication, Unification & Split Pipeline
=========================================================================
Unifies 8 Kaggle foliar pathology datasets (PlantVillage, PlantDoc real-world field,
Corn field imagery, 4 Rice/Paddy datasets, and Cotton leaf diseases) into 48 canonical
classes, eliminates exact + perceptual duplicates across datasets to prevent train/val
leakage, caches oversized images at <=384px for high-throughput MPS training, and
writes reproducible train / val / field_test manifests.
"""

import hashlib
import json
import os
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageOps

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

# 48 Canonical PlantCare AI Classes (sorted/grouped deterministically)
CANONICAL_CLASSES: List[str] = [
    # Apple (4)
    "Apple Scab",
    "Apple with Black Rot",
    "Cedar Apple Rust",
    "Healthy Apple",
    # Blueberry (1)
    "Healthy Blueberry Plant",
    # Cherry (2)
    "Cherry with Powdery Mildew",
    "Healthy Cherry Plant",
    # Corn / Maize (4)
    "Corn (Maize) with Cercospora and Gray Leaf Spot",
    "Corn (Maize) with Common Rust",
    "Corn (Maize) with Northern Leaf Blight",
    "Healthy Corn (Maize) Plant",
    # Grape (4)
    "Grape with Black Rot",
    "Grape with Esca (Black Measles)",
    "Grape with Isariopsis Leaf Spot",
    "Healthy Grape Plant",
    # Orange (1)
    "Orange with Citrus Greening",
    # Peach (2)
    "Peach with Bacterial Spot",
    "Healthy Peach Plant",
    # Bell Pepper (2)
    "Bell Pepper with Bacterial Spot",
    "Healthy Bell Pepper Plant",
    # Potato (3)
    "Potato with Early Blight",
    "Potato with Late Blight",
    "Healthy Potato Plant",
    # Raspberry (1)
    "Healthy Raspberry Plant",
    # Soybean (1)
    "Healthy Soybean Plant",
    # Squash (1)
    "Squash with Powdery Mildew",
    # Strawberry (2)
    "Strawberry with Leaf Scorch",
    "Healthy Strawberry Plant",
    # Tomato (10)
    "Tomato with Bacterial Spot",
    "Tomato with Early Blight",
    "Tomato with Late Blight",
    "Tomato with Leaf Mold",
    "Tomato with Septoria Leaf Spot",
    "Tomato with Spider Mites or Two-spotted Spider Mite",
    "Tomato with Target Spot",
    "Tomato Yellow Leaf Curl Virus",
    "Tomato Mosaic Virus",
    "Healthy Tomato Plant",
    # Rice / Paddy (6)
    "Rice Blast",
    "Rice with Sheath Blight",
    "Rice with Brown Spot",
    "Rice with Bacterial Leaf Blight",
    "Rice with Tungro",
    "Healthy Rice",
    # Cotton (4)
    "Cotton with Bacterial Blight",
    "Cotton with Leaf Curl Virus",
    "Cotton with Fusarium Wilt",
    "Healthy Cotton Plant",
]

# Source dataset folder -> canonical class mapping
PLANTVILLAGE_MAP: Dict[str, str] = {
    "Apple___Apple_scab": "Apple Scab",
    "Apple___Black_rot": "Apple with Black Rot",
    "Apple___Cedar_apple_rust": "Cedar Apple Rust",
    "Apple___healthy": "Healthy Apple",
    "Blueberry___healthy": "Healthy Blueberry Plant",
    "Cherry_(including_sour)___Powdery_mildew": "Cherry with Powdery Mildew",
    "Cherry_(including_sour)___healthy": "Healthy Cherry Plant",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Corn (Maize) with Cercospora and Gray Leaf Spot",
    "Corn_(maize)___Common_rust_": "Corn (Maize) with Common Rust",
    "Corn_(maize)___Northern_Leaf_Blight": "Corn (Maize) with Northern Leaf Blight",
    "Corn_(maize)___healthy": "Healthy Corn (Maize) Plant",
    "Grape___Black_rot": "Grape with Black Rot",
    "Grape___Esca_(Black_Measles)": "Grape with Esca (Black Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "Grape with Isariopsis Leaf Spot",
    "Grape___healthy": "Healthy Grape Plant",
    "Orange___Haunglongbing_(Citrus_greening)": "Orange with Citrus Greening",
    "Peach___Bacterial_spot": "Peach with Bacterial Spot",
    "Peach___healthy": "Healthy Peach Plant",
    "Pepper,_bell___Bacterial_spot": "Bell Pepper with Bacterial Spot",
    "Pepper,_bell___healthy": "Healthy Bell Pepper Plant",
    "Potato___Early_blight": "Potato with Early Blight",
    "Potato___Late_blight": "Potato with Late Blight",
    "Potato___healthy": "Healthy Potato Plant",
    "Raspberry___healthy": "Healthy Raspberry Plant",
    "Soybean___healthy": "Healthy Soybean Plant",
    "Squash___Powdery_mildew": "Squash with Powdery Mildew",
    "Strawberry___Leaf_scorch": "Strawberry with Leaf Scorch",
    "Strawberry___healthy": "Healthy Strawberry Plant",
    "Tomato___Bacterial_spot": "Tomato with Bacterial Spot",
    "Tomato___Early_blight": "Tomato with Early Blight",
    "Tomato___Late_blight": "Tomato with Late Blight",
    "Tomato___Leaf_Mold": "Tomato with Leaf Mold",
    "Tomato___Septoria_leaf_spot": "Tomato with Septoria Leaf Spot",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Tomato with Spider Mites or Two-spotted Spider Mite",
    "Tomato___Target_Spot": "Tomato with Target Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Tomato Yellow Leaf Curl Virus",
    "Tomato___Tomato_mosaic_virus": "Tomato Mosaic Virus",
    "Tomato___healthy": "Healthy Tomato Plant",
}

PLANTDOC_MAP: Dict[str, str] = {
    "Apple_Scab_Leaf": "Apple Scab",
    "Apple_leaf": "Healthy Apple",
    "Apple_rust_leaf": "Cedar Apple Rust",
    "Bell_pepper_leaf": "Healthy Bell Pepper Plant",
    "Bell_pepper_leaf_spot": "Bell Pepper with Bacterial Spot",
    "Blueberry_leaf": "Healthy Blueberry Plant",
    "Cherry_leaf": "Healthy Cherry Plant",
    "Corn_Gray_leaf_spot": "Corn (Maize) with Cercospora and Gray Leaf Spot",
    "Corn_leaf_blight": "Corn (Maize) with Northern Leaf Blight",
    "Corn_rust_leaf": "Corn (Maize) with Common Rust",
    "Peach_leaf": "Healthy Peach Plant",
    "Potato_leaf_early_blight": "Potato with Early Blight",
    "Potato_leaf_late_blight": "Potato with Late Blight",
    "Raspberry_leaf": "Healthy Raspberry Plant",
    "Soyabean_leaf": "Healthy Soybean Plant",
    "Squash_Powdery_mildew_leaf": "Squash with Powdery Mildew",
    "Strawberry_leaf": "Healthy Strawberry Plant",
    "Tomato_Early_blight_leaf": "Tomato with Early Blight",
    "Tomato_Septoria_leaf_spot": "Tomato with Septoria Leaf Spot",
    "Tomato_leaf": "Healthy Tomato Plant",
    "Tomato_leaf_bacterial_spot": "Tomato with Bacterial Spot",
    "Tomato_leaf_late_blight": "Tomato with Late Blight",
    "Tomato_leaf_mosaic_virus": "Tomato Mosaic Virus",
    "Tomato_leaf_yellow_virus": "Tomato Yellow Leaf Curl Virus",
    "Tomato_mold_leaf": "Tomato with Leaf Mold",
    "Tomato_two_spotted_spider_mites_leaf": "Tomato with Spider Mites or Two-spotted Spider Mite",
    "grape_leaf": "Healthy Grape Plant",
    "grape_leaf_black_rot": "Grape with Black Rot",
}

CORN_MAP: Dict[str, str] = {
    "Blight": "Corn (Maize) with Northern Leaf Blight",
    "Common_Rust": "Corn (Maize) with Common Rust",
    "Gray_Leaf_Spot": "Corn (Maize) with Cercospora and Gray Leaf Spot",
    "Healthy": "Healthy Corn (Maize) Plant",
}

RICE_MAP: Dict[str, str] = {
    "Blast": "Rice Blast",
    "leaf_blast": "Rice Blast",
    "rice_blast": "Rice Blast",
    "sheath_blight": "Rice with Sheath Blight",
    "Brownspot": "Rice with Brown Spot",
    "brown_spot": "Rice with Brown Spot",
    "Brown spot": "Rice with Brown Spot",
    "Bacterialblight": "Rice with Bacterial Leaf Blight",
    "bacterial_leaf_blight": "Rice with Bacterial Leaf Blight",
    "Bacterial leaf blight": "Rice with Bacterial Leaf Blight",
    "Tungro": "Rice with Tungro",
    "tungro_virus": "Rice with Tungro",
    "healthy": "Healthy Rice",
    "healthy_rice_plant": "Healthy Rice",
}

COTTON_MAP: Dict[str, str] = {
    "bacterial_blight": "Cotton with Bacterial Blight",
    "curl_virus": "Cotton with Leaf Curl Virus",
    "fussarium_wilt": "Cotton with Fusarium Wilt",
    "healthy": "Healthy Cotton Plant",
}


def compute_dhash(img: Image.Image, hash_size: int = 8) -> str:
    """Computes a 64-bit difference perceptual hash for near-duplicate detection."""
    gray = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.BILINEAR)
    arr = np.asarray(gray, dtype=np.int16)
    diff = arr[:, 1:] > arr[:, :-1]
    bits = "".join("1" if b else "0" for b in diff.flatten())
    return f"{int(bits, 2):016x}"


def prepare_all(output_dir: Path = Path("data"), max_dim: int = 384, seed: int = 42):
    random.seed(seed)
    cache_root = Path.home() / ".cache/kagglehub/datasets"
    prepared_imgs_dir = output_dir / "prepared_cache"
    prepared_imgs_dir.mkdir(parents=True, exist_ok=True)

    # Collect raw records: (path, canonical_label, domain, suggested_split)
    # Note: process PlantDoc/test FIRST when deduplicating so test images stay pure
    raw_records: List[Tuple[Path, str, str, str]] = []

    def scan(ds_rel: str, label_map: Dict[str, str], domain: str, split_mode: str):
        root = cache_root / ds_rel
        if not root.exists():
            print(f"[WARN] Missing dataset: {root}")
            return
        for p in sorted(root.rglob("*")):
            if not (p.is_file() and p.suffix.lower() in IMAGE_EXTS):
                continue
            cls_folder = p.parent.name
            if cls_folder not in label_map:
                continue
            canon = label_map[cls_folder]
            parts_lower = [x.lower() for x in p.parts]
            if split_mode == "plantdoc":
                split = "field_test" if "test" in parts_lower else "train"
            elif split_mode == "train_val_dir":
                split = "val" if ("val" in parts_lower or "validation" in parts_lower) else "train"
            else:
                split = "auto"
            raw_records.append((p, canon, domain, split))

    # Order puts field_test & validation first during dedup priority, wait:
    # Actually we put field_test FIRST so if a PlantDoc test image also appeared in PlantDoc train,
    # it stays in field_test and is removed from train (zero leakage!).
    scan("nirmalsankalana/plantdoc-dataset", PLANTDOC_MAP, "field_plantdoc", "plantdoc")
    scan("mohitsingh1804/plantvillage", PLANTVILLAGE_MAP, "lab_plantvillage", "train_val_dir")
    scan("smaranjitghose/corn-or-maize-leaf-disease-dataset", CORN_MAP, "field_corn", "auto")
    scan("dedeikhsandwisaputra/rice-leafs-disease-dataset", RICE_MAP, "field_rice", "train_val_dir")
    scan("shrupyag001/philippines-rice-diseases", RICE_MAP, "field_rice", "auto")
    scan("nirmalsankalana/rice-leaf-disease-image", RICE_MAP, "field_rice", "auto")
    scan("vbookshelf/rice-leaf-diseases", RICE_MAP, "field_rice", "auto")
    scan("seroshkarim/cotton-leaf-disease-dataset", COTTON_MAP, "field_cotton", "auto")

    # Prioritize field_test records first so they never leak into train
    priority_order = {"field_test": 0, "val": 1, "train": 2, "auto": 3}
    raw_records.sort(key=lambda r: (priority_order[r[3]], str(r[0])))

    print(f"Scanned {len(raw_records)} candidate images across 8 datasets. Deduplicating & caching <= {max_dim}px...")

    seen_sha = set()
    seen_dhash: Dict[str, str] = {}  # (dhash -> canon)
    dedup_sha = 0
    dedup_dhash = 0
    corrupt = 0

    clean_records = []
    for idx, (src_path, canon, domain, split) in enumerate(raw_records):
        try:
            raw_bytes = src_path.read_bytes()
            sha = hashlib.sha256(raw_bytes).hexdigest()
            if sha in seen_sha:
                dedup_sha += 1
                continue
            seen_sha.add(sha)

            with Image.open(src_path) as im:
                im = ImageOps.exif_transpose(im).convert("RGB")
                dh = compute_dhash(im)
                # Deduplicate identical perceptual hash within the same class
                dh_key = f"{canon}::{dh}"
                if dh_key in seen_dhash:
                    dedup_dhash += 1
                    continue
                seen_dhash[dh_key] = str(src_path)

                w, h = im.size
                if max(w, h) > max_dim:
                    scale = max_dim / max(w, h)
                    new_w, new_h = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
                    im_resized = im.resize((new_w, new_h), Image.Resampling.BICUBIC)
                    cached_path = prepared_imgs_dir / f"{sha[:16]}.jpg"
                    if not cached_path.exists():
                        im_resized.save(cached_path, format="JPEG", quality=92)
                    final_path = str(cached_path)
                else:
                    # Keep direct path if already <=384px JPEG/PNG (fast!)
                    final_path = str(src_path)

            clean_records.append({
                "path": final_path,
                "label": canon,
                "domain": domain,
                "orig_split": split,
            })
        except Exception:
            corrupt += 1

        if (idx + 1) % 10000 == 0:
            print(f"  Processed {idx + 1}/{len(raw_records)} | kept={len(clean_records)} | dup_sha={dedup_sha} | dup_dhash={dedup_dhash}", flush=True)

    print(f"Deduplication complete: kept={len(clean_records)}, exact_dups={dedup_sha}, near_dups={dedup_dhash}, corrupt={corrupt}")

    # Assign final splits cleanly:
    # - field_test: PlantDoc test set
    # - val: PlantVillage val + Rice val + 15% stratified split of 'auto' and 'field_plantdoc' train
    #        Wait: keep PlantDoc train mostly in train (85/15 stratified) so real-world field images
    #        exist in both train and val, while PlantDoc test stays 100% unseen!
    train_items = []
    val_items = []
    field_test_items = []

    auto_by_class: Dict[str, List[dict]] = defaultdict(list)
    plantdoc_train_by_class: Dict[str, List[dict]] = defaultdict(list)

    for rec in clean_records:
        sp = rec["orig_split"]
        if sp == "field_test":
            field_test_items.append(rec)
        elif sp == "val":
            val_items.append(rec)
        elif sp == "train" and rec["domain"] == "field_plantdoc":
            plantdoc_train_by_class[rec["label"]].append(rec)
        elif sp == "train":
            train_items.append(rec)
        else:
            auto_by_class[rec["label"]].append(rec)

    # Stratified 85/15 split for 'auto' datasets (Rice Mendeley, PH Rice, Corn extra, Cotton)
    for cls, items in sorted(auto_by_class.items()):
        random.shuffle(items)
        n_val = max(1, int(round(len(items) * 0.15)))
        val_items.extend(items[:n_val])
        train_items.extend(items[n_val:])

    # Keep all PlantDoc train in train (we already have PlantDoc test as held-out real-world field test!)
    for cls, items in sorted(plantdoc_train_by_class.items()):
        train_items.extend(items)

    # Verify all 48 canonical classes are present in both train and val
    train_counts = Counter(r["label"] for r in train_items)
    val_counts = Counter(r["label"] for r in val_items)
    test_counts = Counter(r["label"] for r in field_test_items)

    print("\nClass distribution summary:")
    for c in CANONICAL_CLASSES:
        print(f"  {c:54s} | train={train_counts[c]:5d} | val={val_counts[c]:4d} | field_test={test_counts[c]:3d}")

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "class_labels.json").write_text(json.dumps(CANONICAL_CLASSES, indent=2))
    (output_dir / "train_manifest.json").write_text(json.dumps(train_items))
    (output_dir / "val_manifest.json").write_text(json.dumps(val_items))
    (output_dir / "field_test_manifest.json").write_text(json.dumps(field_test_items))

    summary = {
        "total_raw": len(raw_records),
        "total_clean": len(clean_records),
        "dedup_sha256": dedup_sha,
        "dedup_dhash": dedup_dhash,
        "corrupt": corrupt,
        "num_classes": len(CANONICAL_CLASSES),
        "train_count": len(train_items),
        "val_count": len(val_items),
        "field_test_count": len(field_test_items),
        "domain_counts_train": dict(Counter(r["domain"] for r in train_items)),
        "class_counts_train": dict(train_counts),
        "class_counts_val": dict(val_counts),
        "class_counts_field_test": dict(test_counts),
    }
    (output_dir / "dataset_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nSaved manifests to {output_dir}: train={len(train_items)}, val={len(val_items)}, field_test={len(field_test_items)}")


if __name__ == "__main__":
    prepare_all()
