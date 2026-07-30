"""
Organiza o dataset FINAL completo (após a consolidação feita por
consolidar_dataset_final.py) em subpastas train/val/test, com um data.yaml
pronto para o treinamento definitivo do YOLOv8n e YOLOv10 conforme o
protocolo experimental do TCC.

Diferente de organizar_dataset_limpo.py (Etapa 1, que EXCLUÍA os arquivos
de cacho), este script inclui TODAS as imagens do dataset consolidado.

Uso:
    python organizar_dataset_treino_final.py \
        --labels_dir dataset_24_06/labels \
        --images_dir dataset_24_06/images \
        --saida_dir dataset_final
"""

import argparse
import shutil
from pathlib import Path


def identificar_split(nome_arquivo: str):
    nome = nome_arquivo.lower()
    if nome.startswith("train_"):
        return "train"
    if nome.startswith("val_"):
        return "val"
    if nome.startswith("test_"):
        return "test"
    return None


def encontrar_imagem_correspondente(images_dir: Path, nome_base: str):
    for ext in (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"):
        candidato = images_dir / f"{nome_base}{ext}"
        if candidato.exists():
            return candidato
    encontrados = list(images_dir.rglob(f"{nome_base}.*"))
    return encontrados[0] if encontrados else None


def escrever_data_yaml(saida_dir: Path):
    conteudo = (
        f"train: {(saida_dir / 'train' / 'images').resolve()}\n"
        f"val: {(saida_dir / 'val' / 'images').resolve()}\n"
        f"test: {(saida_dir / 'test' / 'images').resolve()}\n"
        "nc: 1\n"
        "names: ['grao']\n"
    )
    (saida_dir / "data.yaml").write_text(conteudo, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels_dir", type=str, required=True)
    parser.add_argument("--images_dir", type=str, required=True)
    parser.add_argument("--saida_dir", type=str, default="dataset_final")
    args = parser.parse_args()

    labels_dir = Path(args.labels_dir)
    images_dir = Path(args.images_dir)
    saida_dir = Path(args.saida_dir)

    contagem = {"train": 0, "val": 0, "test": 0}
    ignorados = 0

    for txt_path in sorted(labels_dir.rglob("*.txt")):
        split = identificar_split(txt_path.name)
        if split is None:
            ignorados += 1
            continue

        img_path = encontrar_imagem_correspondente(images_dir, txt_path.stem)
        if img_path is None:
            print(f"  [aviso] imagem não encontrada para {txt_path.stem}, ignorando.")
            ignorados += 1
            continue

        dest_labels = saida_dir / split / "labels"
        dest_images = saida_dir / split / "images"
        dest_labels.mkdir(parents=True, exist_ok=True)
        dest_images.mkdir(parents=True, exist_ok=True)

        shutil.copy2(txt_path, dest_labels / txt_path.name)
        shutil.copy2(img_path, dest_images / img_path.name)
        contagem[split] += 1

    escrever_data_yaml(saida_dir)

    total = sum(contagem.values())
    print("\n=== Resumo do dataset final ===")
    print(f"Train: {contagem['train']}")
    print(f"Val:   {contagem['val']}")
    print(f"Test:  {contagem['test']}")
    print(f"Total: {total}")
    print(f"Ignorados/sem correspondência: {ignorados}")
    print(f"\nDataset final pronto em: {saida_dir.resolve()}")
    print(f"Arquivo de configuração: {saida_dir / 'data.yaml'}")
    print("\nEsse é o dataset a usar no treinamento definitivo (YOLOv8n e YOLOv10, "
          "imgsz=960, AdamW, lr0=0.003, 120 épocas), conforme a metodologia do TCC.")


if __name__ == "__main__":
    main()