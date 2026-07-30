from pathlib import Path
import shutil
import random

SEED = 42
BASE = Path("dataset_limpo")
OUT = Path("dataset_70_20_10_corrigido")
IMG_EXTS = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]

random.seed(SEED)

img_dir = BASE / "images" / "all"
lbl_dir = BASE / "labels" / "all"

pares = []

for img in img_dir.iterdir():
    if img.suffix.lower() not in IMG_EXTS:
        continue

    lbl = lbl_dir / f"{img.stem}.txt"

    if lbl.exists():
        pares.append((img, lbl, img.stem, img.suffix.lower()))
    else:
        print(f"Sem label: {img.name}")

random.shuffle(pares)

total = len(pares)
n_train = int(total * 0.70)
n_val = int(total * 0.20)

splits = {
    "train": pares[:n_train],
    "val": pares[n_train:n_train + n_val],
    "test": pares[n_train + n_val:]
}

if OUT.exists():
    shutil.rmtree(OUT)

for subset in ["train", "val", "test"]:
    (OUT / "images" / subset).mkdir(parents=True, exist_ok=True)
    (OUT / "labels" / subset).mkdir(parents=True, exist_ok=True)

for subset, lista in splits.items():
    for img, lbl, nome, ext in lista:
        shutil.copy2(img, OUT / "images" / subset / f"{nome}{ext}")
        shutil.copy2(lbl, OUT / "labels" / subset / f"{nome}.txt")

print("Redistribuição concluída.")
print(f"Total: {total}")

for subset in ["train", "val", "test"]:
    imgs = list((OUT / "images" / subset).iterdir())
    lbls = list((OUT / "labels" / subset).iterdir())
    print(f"{subset}: {len(imgs)} imagens | {len(lbls)} labels")