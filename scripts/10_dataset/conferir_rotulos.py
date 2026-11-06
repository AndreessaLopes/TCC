# -*- coding: utf-8 -*-
"""Desenha as caixas sobre a copia publicada, para conferencia visual.

Seleciona imagens das tres particoes, cobrindo cenas densas e esparsas,
e monta uma folha de contato. Serve para verificar que a normalizacao
dos rotulos nao deslocou nenhuma caixa.

Uso: python3 conferir_rotulos.py <pasta_publicada> <saida.jpg>
"""

import csv
import os
import sys

from PIL import Image, ImageDraw

LADO = 760          # lado do quadro de cada miniatura
COLUNAS = 3
MARGEM = 12
FAIXA = 34          # altura da tarja com o nome


def escolher(manifesto):
    """Pega, por particao, a imagem mais densa e a mais esparsa."""
    linhas = list(csv.DictReader(open(manifesto, newline="", encoding="utf-8")))
    saida = []
    for particao in ("train", "val", "test"):
        sub = [l for l in linhas if l["particao"] == particao]
        sub.sort(key=lambda l: int(l["instancias"]))
        saida.append(sub[-1])
        saida.append(sub[len(sub) // 2])
    return saida


def desenhar(raiz, linha):
    caminho = os.path.join(raiz, linha["arquivo"].replace("/", os.sep))
    im = Image.open(caminho).convert("RGB")
    larg, alt = im.size
    rotulo = caminho.replace(os.sep + "images" + os.sep,
                             os.sep + "labels" + os.sep)[:-4] + ".txt"
    d = ImageDraw.Draw(im)
    espessura = max(2, round(min(larg, alt) / 300))
    n = 0
    with open(rotulo, encoding="utf-8") as f:
        for ln in f:
            p = ln.split()
            if len(p) != 5:
                continue
            cx, cy, w, h = (float(v) for v in p[1:])
            x1 = (cx - w / 2) * larg
            y1 = (cy - h / 2) * alt
            x2 = (cx + w / 2) * larg
            y2 = (cy + h / 2) * alt
            d.rectangle([x1, y1, x2, y2], outline=(0, 229, 118), width=espessura)
            n += 1
    im.thumbnail((LADO, LADO), Image.LANCZOS)
    return im, n


def main():
    raiz, destino = sys.argv[1], sys.argv[2]
    escolhidas = escolher(os.path.join(raiz, "manifesto.csv"))

    linhas_grade = (len(escolhidas) + COLUNAS - 1) // COLUNAS
    larg_total = COLUNAS * LADO + (COLUNAS + 1) * MARGEM
    alt_total = linhas_grade * (LADO + FAIXA) + (linhas_grade + 1) * MARGEM
    folha = Image.new("RGB", (larg_total, alt_total), (18, 18, 18))
    pincel = ImageDraw.Draw(folha)

    for k, linha in enumerate(escolhidas):
        im, n = desenhar(raiz, linha)
        col, lin = k % COLUNAS, k // COLUNAS
        x = MARGEM + col * (LADO + MARGEM) + (LADO - im.width) // 2
        y = MARGEM + lin * (LADO + FAIXA + MARGEM)
        folha.paste(im, (x, y + FAIXA))
        pincel.text((MARGEM + col * (LADO + MARGEM) + 4, y + 8),
                    "%s  %d caixas  %sx%s"
                    % (linha["arquivo"], n, linha["largura"], linha["altura"]),
                    fill=(235, 235, 235))
        print("%-28s %4d caixas" % (linha["arquivo"], n))

    folha.save(destino, quality=88)
    print("folha gravada em %s" % destino)


if __name__ == "__main__":
    main()
