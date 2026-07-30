"""
Amostragem visual estratificada de bounding boxes suspeitas (YOLO).

Objetivo: em vez de reanotar ou inspecionar as ~800 imagens suspeitas uma a
uma, este script pega uma amostra pequena e bem distribuída ao longo das
faixas de área (0.15-0.30, 0.30-0.50, 0.50-0.95, >=0.95), desenha as
bounding boxes sobre as imagens e organiza tudo em "contact sheets" (grades
de miniaturas) para você folhear rapidamente e decidir visualmente:

    - "isso é um cacho real (vários frutos numa caixa só)"  -> reanotar
    - "isso é um close-up legítimo de 1 fruto"               -> manter como está

Uso:
    python amostra_visual_bbox.py \
        --labels_dir dataset_24_06/labels \
        --images_dir dataset_24_06/images \
        --saida_dir amostra_visual \
        --n_por_faixa 12

Isso gera, dentro de --saida_dir:
    - imagens individuais com as caixas desenhadas, organizadas por faixa
    - um contact_sheet_<faixa>.jpg por faixa, com grade de miniaturas
      numeradas, para revisão rápida
"""

import argparse
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


FAIXAS = [
    ("0.15_a_0.30", 0.15, 0.30),
    ("0.30_a_0.50", 0.30, 0.50),
    ("0.50_a_0.95", 0.50, 0.95),
    ("0.95_a_1.00", 0.95, 1.01),  # inclui área == 1.0
]


def encontrar_imagem_correspondente(images_dir: Path, nome_base: str):
    for ext in (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"):
        candidato = images_dir / f"{nome_base}{ext}"
        if candidato.exists():
            return candidato
    encontrados = list(images_dir.rglob(f"{nome_base}.*"))
    return encontrados[0] if encontrados else None


def ler_boxes(txt_path: Path):
    boxes = []
    with open(txt_path, "r") as f:
        for linha in f:
            partes = linha.strip().split()
            if len(partes) < 5:
                continue
            try:
                classe, xc, yc, w, h = partes[:5]
                boxes.append((classe, float(xc), float(yc), float(w), float(h)))
            except ValueError:
                continue
    return boxes


def maior_area_do_arquivo(boxes):
    if not boxes:
        return 0.0
    return max(w * h for _, _, _, w, h in boxes)


def desenhar_boxes(img_path: Path, boxes, destino: Path):
    img = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    largura_img, altura_img = img.size

    for classe, xc, yc, w, h in boxes:
        x0 = (xc - w / 2) * largura_img
        y0 = (yc - h / 2) * altura_img
        x1 = (xc + w / 2) * largura_img
        y1 = (yc + h / 2) * altura_img
        area = w * h
        cor = "red" if area >= 0.15 else "lime"
        espessura = max(2, int(min(largura_img, altura_img) * 0.004))
        draw.rectangle([x0, y0, x1, y1], outline=cor, width=espessura)

    img.save(destino, quality=90)
    return img.size


def montar_contact_sheet(caminhos_com_legenda, saida_path: Path, colunas=4, largura_thumb=350):
    """Monta uma grade de miniaturas numeradas a partir de uma lista de (caminho, legenda)."""
    if not caminhos_com_legenda:
        return

    thumbs = []
    for caminho, legenda in caminhos_com_legenda:
        img = Image.open(caminho).convert("RGB")
        w_orig, h_orig = img.size
        altura_thumb = int(largura_thumb * h_orig / w_orig)
        img_thumb = img.resize((largura_thumb, altura_thumb))
        thumbs.append((img_thumb, legenda))

    linhas = math.ceil(len(thumbs) / colunas)
    altura_max = max(t[0].size[1] for t in thumbs)
    margem_legenda = 22

    sheet_w = colunas * largura_thumb
    sheet_h = linhas * (altura_max + margem_legenda)
    sheet = Image.new("RGB", (sheet_w, sheet_h), color=(20, 20, 20))
    draw = ImageDraw.Draw(sheet)

    try:
        fonte = ImageFont.truetype("arial.ttf", 16)
    except Exception:
        fonte = ImageFont.load_default()

    for idx, (thumb, legenda) in enumerate(thumbs):
        col = idx % colunas
        row = idx // colunas
        x = col * largura_thumb
        y = row * (altura_max + margem_legenda)
        sheet.paste(thumb, (x, y))
        draw.text((x + 5, y + altura_max + 2), legenda, fill="white", font=fonte)

    sheet.save(saida_path, quality=92)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels_dir", type=str, required=True)
    parser.add_argument("--images_dir", type=str, required=True)
    parser.add_argument("--saida_dir", type=str, default="amostra_visual")
    parser.add_argument("--n_por_faixa", type=int, default=12,
                        help="Quantidade de imagens sorteadas por faixa de área.")
    parser.add_argument("--seed", type=int, default=42, help="Seed para reprodutibilidade do sorteio.")
    args = parser.parse_args()

    random.seed(args.seed)
    labels_dir = Path(args.labels_dir)
    images_dir = Path(args.images_dir)
    saida_dir = Path(args.saida_dir)
    saida_dir.mkdir(parents=True, exist_ok=True)

    txt_files = sorted(labels_dir.rglob("*.txt"))

    # Classifica cada arquivo pela sua maior caixa
    por_faixa = {nome: [] for nome, _, _ in FAIXAS}
    for txt_path in txt_files:
        boxes = ler_boxes(txt_path)
        area_max = maior_area_do_arquivo(boxes)
        for nome, minimo, maximo in FAIXAS:
            if minimo <= area_max < maximo:
                por_faixa[nome].append((txt_path, boxes, area_max))
                break

    print("=== Quantidade de arquivos por faixa de área (maior caixa do arquivo) ===")
    for nome, _, _ in FAIXAS:
        print(f"  {nome}: {len(por_faixa[nome])} arquivos")

    for nome_faixa, _, _ in FAIXAS:
        candidatos = por_faixa[nome_faixa]
        if not candidatos:
            continue

        amostra = random.sample(candidatos, min(args.n_por_faixa, len(candidatos)))
        pasta_faixa = saida_dir / nome_faixa
        pasta_faixa.mkdir(parents=True, exist_ok=True)

        legendas = []
        for i, (txt_path, boxes, area_max) in enumerate(amostra):
            img_path = encontrar_imagem_correspondente(images_dir, txt_path.stem)
            if not img_path:
                print(f"  [aviso] imagem não encontrada para {txt_path.stem}, pulando.")
                continue

            destino = pasta_faixa / f"{i:02d}_{txt_path.stem}.jpg"
            desenhar_boxes(img_path, boxes, destino)
            legenda = f"{i:02d} {txt_path.stem} (area={area_max:.2f}, n_boxes={len(boxes)})"
            legendas.append((destino, legenda))

        contact_sheet_path = saida_dir / f"contact_sheet_{nome_faixa}.jpg"
        montar_contact_sheet(legendas, contact_sheet_path)
        print(f"Contact sheet gerado: {contact_sheet_path}")

    print(f"\nTudo pronto. Abra os arquivos contact_sheet_*.jpg em: {saida_dir.resolve()}")
    print("Caixas em vermelho = área >= 0.15 (a suspeita); verde = caixas normais na mesma imagem.")


if __name__ == "__main__":
    main()