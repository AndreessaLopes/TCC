from pathlib import Path

IMAGES = Path(r"dataset/images/vermelhas")
LABELS = Path(r"dataset/labels/vermelhas")

imgs = {p.stem for p in IMAGES.glob("*.*")}
labs = {p.stem for p in LABELS.glob("*.txt")}

print("Imagens:", len(imgs))
print("Labels:", len(labs))

print("\nSem label:")
for x in sorted(imgs - labs)[:20]:
    print(x)

print("\nSem imagem:")
for x in sorted(labs - imgs)[:20]:
    print(x)