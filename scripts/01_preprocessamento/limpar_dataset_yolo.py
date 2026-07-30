from pathlib import Path
from PIL import Image
import shutil

DATASET = Path("dataset_final")
EXTS = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]

def criar_pasta(path):
    path.mkdir(parents=True, exist_ok=True)

def listar_imagens(img_dir):
    imagens = []
    for ext in EXTS:
        imagens.extend(img_dir.glob(f"*{ext}"))
        imagens.extend(img_dir.glob(f"*{ext.upper()}"))
    return list({p.resolve(): p for p in imagens}.values())

def validar_imagem(img_path):
    try:
        with Image.open(img_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def validar_label(label_path):
    if not label_path.exists():
        return False, "label ausente"

    linhas = label_path.read_text(encoding="utf-8").strip().splitlines()

    if len(linhas) == 0:
        return False, "label vazio"

    for i, linha in enumerate(linhas, start=1):
        partes = linha.strip().split()

        if len(partes) != 5:
            return False, f"linha {i} inválida"

        try:
            cls = int(float(partes[0]))
            valores = list(map(float, partes[1:]))
        except ValueError:
            return False, f"linha {i} com valores não numéricos"

        if cls < 0:
            return False, f"linha {i} com classe negativa"

        if any(v < 0 or v > 1 for v in valores):
            return False, f"linha {i} com coordenada fora de 0-1"

    return True, "ok"

def mover_seguro(origem, destino):
    if not origem.exists():
        return False

    criar_pasta(destino.parent)

    if destino.exists():
        destino = destino.with_name(f"{destino.stem}_duplicado{destino.suffix}")

    shutil.move(str(origem), str(destino))
    return True

def limpar_subset(subset):
    print(f"\nVerificando: {subset}")

    img_dir = DATASET / "images" / subset
    lbl_dir = DATASET / "labels" / subset

    lixo_img = DATASET / "removidos" / "images" / subset
    lixo_lbl = DATASET / "removidos" / "labels" / subset

    criar_pasta(lixo_img)
    criar_pasta(lixo_lbl)

    imagens = listar_imagens(img_dir)

    total = len(imagens)
    removidas = 0
    sem_label = 0
    label_invalido = 0
    imagem_corrompida = 0

    for img_path in imagens:
        if not img_path.exists():
            continue

        label_path = lbl_dir / f"{img_path.stem}.txt"
        motivo = None

        if not validar_imagem(img_path):
            motivo = "imagem corrompida"
            imagem_corrompida += 1
        else:
            ok_label, msg = validar_label(label_path)
            if not ok_label:
                motivo = msg
                if msg == "label ausente":
                    sem_label += 1
                else:
                    label_invalido += 1

        if motivo:
            print(f"Removendo {img_path.name}: {motivo}")

            if mover_seguro(img_path, lixo_img / img_path.name):
                removidas += 1

            if label_path.exists():
                mover_seguro(label_path, lixo_lbl / label_path.name)

    labels = list(lbl_dir.glob("*.txt"))
    labels_orfas = 0
    imagens_stems = {p.stem for p in listar_imagens(img_dir)}

    for label in labels:
        if label.stem not in imagens_stems:
            print(f"Label órfã removida: {label.name}")
            if mover_seguro(label, lixo_lbl / label.name):
                labels_orfas += 1

    print(f"Total de imagens verificadas: {total}")
    print(f"Imagens removidas: {removidas}")
    print(f"Imagens corrompidas: {imagem_corrompida}")
    print(f"Sem label: {sem_label}")
    print(f"Labels inválidas/vazias: {label_invalido}")
    print(f"Labels órfãs removidas: {labels_orfas}")

def contar_final():
    print("\nResumo final:")
    for subset in ["train", "val", "test"]:
        img_dir = DATASET / "images" / subset
        lbl_dir = DATASET / "labels" / subset

        imgs = listar_imagens(img_dir)
        labels = list(lbl_dir.glob("*.txt"))

        print(f"{subset}: {len(imgs)} imagens | {len(labels)} labels")

if __name__ == "__main__":
    for subset in ["train", "val", "test"]:
        limpar_subset(subset)

    contar_final()