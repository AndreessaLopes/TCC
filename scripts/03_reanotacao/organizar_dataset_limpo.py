"""
Etapa 1 do pipeline de reanotação semi-automática.

Organiza uma cópia do dataset contendo APENAS os arquivos que não foram
sinalizados como "provavel_cacho" ou "provavel_erro" pelo script de triagem
(triagem_bbox_suspeitas.py), preservando a divisão train/val/test já
existente (baseada no prefixo do nome do arquivo: train_*, val_*, test_*).

O resultado é um dataset pronto para treinar um modelo YOLO "baseline",
usado depois para sugerir anotações nas imagens de cacho.

Uso:
    python organizar_dataset_limpo.py \
        --labels_dir dataset_24_06/labels \
        --images_dir dataset_24_06/images \
        --relatorio_csv relatorio_bboxes_suspeitas.csv \
        --saida_dir dataset_baseline
"""

import argparse
import csv
import shutil
from pathlib import Path


def carregar_arquivos_sinalizados(csv_path: Path):
    """Retorna o conjunto de nomes de arquivo .txt que possuem ao menos uma
    caixa suspeita (provavel_cacho ou provavel_erro), independentemente da
    linha específica."""
    sinalizados = set()
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sinalizados.add(row["arquivo"])
    return sinalizados


def identificar_split(nome_arquivo: str):
    """Identifica train/val/test a partir do prefixo do nome do arquivo."""
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
    parser.add_argument("--relatorio_csv", type=str, required=True,
                        help="CSV gerado por triagem_bbox_suspeitas.py")
    parser.add_argument("--saida_dir", type=str, default="dataset_baseline")
    args = parser.parse_args()

    labels_dir = Path(args.labels_dir)
    images_dir = Path(args.images_dir)
    saida_dir = Path(args.saida_dir)
    sinalizados = carregar_arquivos_sinalizados(Path(args.relatorio_csv))

    contagem = {"train": 0, "val": 0, "test": 0, "ignorado_sem_split": 0}
    pulados = 0

    for txt_path in sorted(labels_dir.rglob("*.txt")):
        if txt_path.name in sinalizados:
            pulados += 1
            continue

        split = identificar_split(txt_path.name)
        if split is None:
            contagem["ignorado_sem_split"] += 1
            print(f"  [aviso] não foi possível identificar split de {txt_path.name}, ignorando.")
            continue

        img_path = encontrar_imagem_correspondente(images_dir, txt_path.stem)
        if img_path is None:
            print(f"  [aviso] imagem não encontrada para {txt_path.stem}, ignorando.")
            continue

        dest_labels = saida_dir / split / "labels"
        dest_images = saida_dir / split / "images"
        dest_labels.mkdir(parents=True, exist_ok=True)
        dest_images.mkdir(parents=True, exist_ok=True)

        shutil.copy2(txt_path, dest_labels / txt_path.name)
        shutil.copy2(img_path, dest_images / img_path.name)
        contagem[split] += 1

    escrever_data_yaml(saida_dir)

    print("\n=== Resumo ===")
    print(f"Arquivos sinalizados (excluídos): {pulados}")
    print(f"Train (limpo): {contagem['train']}")
    print(f"Val (limpo):   {contagem['val']}")
    print(f"Test (limpo):  {contagem['test']}")
    print(f"\nDataset baseline pronto em: {saida_dir.resolve()}")
    print(f"Arquivo de configuração gerado: {saida_dir / 'data.yaml'}")


if __name__ == "__main__":
    main()