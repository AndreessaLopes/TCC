"""
Checagem visual rápida das pré-anotações geradas (Etapa 3).

Antes de importar as 836 imagens no MakeSense.ai para revisão manual
completa, este script sorteia uma amostra pequena, desenha as caixas
finais (mantidas + sugeridas pelo modelo) e monta um contact sheet único,
para você avaliar rapidamente se a qualidade geral das sugestões é boa
o suficiente para o fluxo de "revisar e corrigir" valer a pena, ou se
o modelo baseline está errando demais.

Uso:
    python visualizar_preanotacoes.py \
        --preanotacoes_dir preanotacoes_cacho \
        --n_amostra 24
"""

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def ler_boxes(txt_path: Path):
    boxes = []
    if not txt_path.exists():
        return boxes
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


def desenhar_boxes(img_path: Path, boxes, destino: Path):
    img = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    largura_img, altura_img = img.size

    for classe, xc, yc, w, h in boxes:
        x0 = (xc - w / 2) * largura_img
        y0 = (yc - h / 2) * altura_img
        x1 = (xc + w / 2) * largura_img
        y1 = (yc + h / 2) * altura_img
        espessura = max(2, int(min(largura_img, altura_img) * 0.004))
        draw.rectangle([x0, y0, x1, y1], outline="cyan", width=espessura)

    img.save(destino, quality=90)


def montar_contact_sheet(itens, saida_path: Path, colunas=4, largura_thumb=350):
    if not itens:
        return
    thumbs = []
    for caminho, legenda in itens:
        img = Image.open(caminho).convert("RGB")
        w_orig, h_orig = img.size
        altura_thumb = int(largura_thumb * h_orig / w_orig)
        thumbs.append((img.resize((largura_thumb, altura_thumb)), legenda))

    linhas = math.ceil(len(thumbs) / colunas)
    altura_max = max(t[0].size[1] for t in thumbs)
    margem_legenda = 22
    sheet = Image.new("RGB", (colunas * largura_thumb, linhas * (altura_max + margem_legenda)), (20, 20, 20))
    draw = ImageDraw.Draw(sheet)
    try:
        fonte = ImageFont.truetype("arial.ttf", 16)
    except Exception:
        fonte = ImageFont.load_default()

    for idx, (thumb, legenda) in enumerate(thumbs):
        col, row = idx % colunas, idx // colunas
        x, y = col * largura_thumb, row * (altura_max + margem_legenda)
        sheet.paste(thumb, (x, y))
        draw.text((x + 5, y + altura_max + 2), legenda, fill="white", font=fonte)

    sheet.save(saida_path, quality=92)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preanotacoes_dir", type=str, required=True,
                        help="Pasta gerada na Etapa 3 (contém images/ e labels/).")
    parser.add_argument("--saida", type=str, default="contact_sheet_preanotacoes.jpg")
    parser.add_argument("--n_amostra", type=int, default=24)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    base = Path(args.preanotacoes_dir)
    images_dir = base / "images"
    labels_dir = base / "labels"

    imagens = sorted(images_dir.glob("*"))
    if not imagens:
        raise FileNotFoundError(f"Nenhuma imagem encontrada em {images_dir}")

    amostra = random.sample(imagens, min(args.n_amostra, len(imagens)))

    pasta_tmp = base / "_tmp_visualizacao"
    pasta_tmp.mkdir(exist_ok=True)

    itens = []
    for i, img_path in enumerate(amostra):
        txt_path = labels_dir / f"{img_path.stem}.txt"
        boxes = ler_boxes(txt_path)
        destino = pasta_tmp / f"{i:02d}_{img_path.stem}.jpg"
        desenhar_boxes(img_path, boxes, destino)
        legenda = f"{i:02d} {img_path.stem} (n_boxes={len(boxes)})"
        itens.append((destino, legenda))

    montar_contact_sheet(itens, Path(args.saida))
    print(f"Contact sheet salvo em: {Path(args.saida).resolve()}")
    print("Caixas em ciano = resultado final (caixas mantidas + sugeridas pelo modelo).")
    print("Avalie: as caixas parecem cobrir bem os grãos individuais? Há muita "
          "sobreposição, caixas faltando, ou falsos positivos em folhas/galhos?")


if __name__ == "__main__":
    main()