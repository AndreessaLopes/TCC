"""Prepara o conjunto de dados para publicacao, em resolucao reduzida.

As imagens originais somam 11 GB em resolucao plena, ate 16 megapixels,
para um modelo treinado em 960 por 960 pixels. Reduzir o lado maior a
1.920 pixels corta o volume por volta de uma ordem de grandeza sem perda
para quem reproduzir o treinamento na resolucao usada aqui.

Os rotulos no formato YOLO sao normalizados pela dimensao da imagem, de
modo que nao mudam com o redimensionamento e sao apenas copiados. O
data.yaml e reescrito com caminhos relativos, uma vez que o original
aponta para o diretorio de quem executou.

Nao sobrescreve nada: grava em pasta nova, para que o conjunto original
permaneca intacto.

Uso: python3 -I redimensionar_dataset.py <dataset_final> <saida> [lado]
"""
import os
import shutil
import sys

from PIL import Image, ImageOps

origem = sys.argv[1]
destino = sys.argv[2]
LADO = int(sys.argv[3]) if len(sys.argv) > 3 else 1920

if os.path.exists(destino) and os.listdir(destino):
    sys.exit("FALHOU: %s existe e nao esta vazio" % destino)

EXTENSOES = (".jpg", ".jpeg", ".png")
total_antes = total_depois = convertidas = copiadas = 0

for particao in ("train", "val", "test"):
    dir_img = os.path.join(origem, particao, "images")
    dir_rot = os.path.join(origem, particao, "labels")
    if not os.path.isdir(dir_img):
        sys.exit("FALHOU: nao encontrei %s" % dir_img)

    saida_img = os.path.join(destino, particao, "images")
    saida_rot = os.path.join(destino, particao, "labels")
    os.makedirs(saida_img, exist_ok=True)
    os.makedirs(saida_rot, exist_ok=True)

    for nome in sorted(os.listdir(dir_img)):
        if not nome.lower().endswith(EXTENSOES):
            continue
        caminho = os.path.join(dir_img, nome)
        total_antes += os.path.getsize(caminho)

        # A orientacao EXIF precisa ser aplicada antes de redimensionar,
        # sob pena de a imagem publicada sair girada em relacao as caixas.
        im = ImageOps.exif_transpose(Image.open(caminho)).convert("RGB")
        if max(im.size) > LADO:
            fator = LADO / max(im.size)
            im = im.resize((round(im.size[0] * fator),
                            round(im.size[1] * fator)), Image.LANCZOS)
            convertidas += 1
        else:
            copiadas += 1

        base = os.path.splitext(nome)[0] + ".jpg"
        alvo = os.path.join(saida_img, base)
        im.save(alvo, quality=92, subsampling=1, optimize=True)
        total_depois += os.path.getsize(alvo)

        # O rotulo acompanha a imagem pelo nome, nao pela extensao.
        rotulo = os.path.join(dir_rot, os.path.splitext(nome)[0] + ".txt")
        if os.path.exists(rotulo):
            shutil.copy2(rotulo, os.path.join(
                saida_rot, os.path.splitext(nome)[0] + ".txt"))
        else:
            print("aviso: sem rotulo para %s" % nome)

with open(os.path.join(destino, "data.yaml"), "w", encoding="utf-8") as f:
    f.write("train: train/images\n"
            "val: val/images\n"
            "test: test/images\n"
            "\n"
            "nc: 1\n"
            "names: ['frutos']\n")

print("imagens redimensionadas: %d" % convertidas)
print("imagens mantidas: %d" % copiadas)
print("antes:  %.2f GB" % (total_antes / 1024 ** 3))
print("depois: %.2f GB" % (total_depois / 1024 ** 3))
print("\ndata.yaml reescrito com caminhos relativos")
