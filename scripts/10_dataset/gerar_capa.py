# -*- coding: utf-8 -*-
"""Monta a imagem de capa do dataset, em faixa larga.

Escolhe imagens de densidade variada, recorta cada uma em quadrado pelo
centro e emenda em uma faixa unica, com as caixas desenhadas.

Uso: python3 gerar_capa.py <pasta_publicada> <saida.jpg>
"""

import csv
import os
import sys

from PIL import Image, ImageDraw

LARGURA = 1600
ALTURA = 600
ESCOLHIDAS = [
    "train/images/train_1290.jpg",
    "test/images/test_1314.jpg",
    "val/images/val_1308.jpg",
    "test/images/test_1022.jpg",
]


def caixas(raiz, rel):
    rot = os.path.join(raiz, rel.replace("/images/", "/labels/")[:-4] + ".txt")
    saida = []
    with open(rot, encoding="utf-8") as f:
        for ln in f:
            p = ln.split()
            if len(p) == 5:
                saida.append(tuple(float(v) for v in p[1:]))
    return saida


def painel(raiz, rel, lado):
    im = Image.open(os.path.join(raiz, rel)).convert("RGB")
    larg, alt = im.size
    cx = [(c[0] * larg, c[1] * alt, c[2] * larg, c[3] * alt) for c in caixas(raiz, rel)]
    d = ImageDraw.Draw(im)
    esp = max(3, round(min(larg, alt) / 220))
    for x, y, w, h in cx:
        d.rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2],
                    outline=(0, 229, 118), width=esp)
    # Recorte quadrado pelo centro, depois reducao.
    corte = min(larg, alt)
    esq = (larg - corte) // 2
    topo = (alt - corte) // 2
    im = im.crop((esq, topo, esq + corte, topo + corte))
    return im.resize((lado, lado), Image.LANCZOS)


def main():
    raiz, destino = sys.argv[1], sys.argv[2]
    n = len(ESCOLHIDAS)
    vao = 8
    lado = (LARGURA - vao * (n - 1)) // n
    faixa = Image.new("RGB", (LARGURA, lado), (12, 12, 12))
    for k, rel in enumerate(ESCOLHIDAS):
        faixa.paste(painel(raiz, rel, lado), (k * (lado + vao), 0))
    # Recorta a faixa para a altura final, pelo centro.
    topo = max(0, (lado - ALTURA) // 2)
    faixa = faixa.crop((0, topo, LARGURA, topo + min(ALTURA, lado)))
    faixa.save(destino, quality=90)
    print("capa gravada em %s, %dx%d" % (destino, faixa.width, faixa.height))


if __name__ == "__main__":
    main()
