from pathlib import Path

DATASET = Path("dataset_final")
EXTS = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]

def listar_imagens(pasta):
    return [p for p in pasta.iterdir() if p.is_file() and p.suffix.lower() in EXTS]

def contar_boxes(label_path):
    if not label_path.exists():
        return 0
    conteudo = label_path.read_text(encoding="utf-8").strip()
    if not conteudo:
        return 0
    return len(conteudo.splitlines())

total_imgs = 0
total_labels = 0
total_boxes = 0

print("\nAUDITORIA DO DATASET PRINCIPAL\n")

for subset in ["train", "val", "test"]:
    img_dir = DATASET / "images" / subset
    lbl_dir = DATASET / "labels" / subset

    imagens = listar_imagens(img_dir)
    labels = list(lbl_dir.glob("*.txt"))

    boxes = sum(contar_boxes(lbl) for lbl in labels)

    total_imgs += len(imagens)
    total_labels += len(labels)
    total_boxes += boxes

    media = boxes / len(imagens) if imagens else 0

    print(f"{subset}")
    print(f"  imagens: {len(imagens)}")
    print(f"  labels:  {len(labels)}")
    print(f"  boxes:   {boxes}")
    print(f"  média de objetos/imagem: {media:.2f}\n")

print("TOTAL")
print(f"  imagens: {total_imgs}")
print(f"  labels:  {total_labels}")
print(f"  boxes:   {total_boxes}")
print(f"  média geral de objetos/imagem: {total_boxes / total_imgs:.2f}")