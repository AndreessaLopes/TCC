"""Figura de exemplo de imagem anotada do conjunto.

Desenha as caixas delimitadoras do arquivo de rotulos YOLO sobre a
imagem correspondente. A saida e um JPEG de 1600 px de largura, o que
corresponde a cerca de 370 dpi na largura impressa, suficiente para que
as caixas e os frutos permanecam nitidos na pagina.

As fotos do conjunto trazem orientacao registrada em EXIF. O
carregamento precisa aplica-la, porque as anotacoes foram feitas sobre
a imagem ja rotacionada. Sem isso, as caixas aparecem deslocadas.

Uso: python3 -I gerar_fig_anotacao.py <imagem> <rotulos> <saida.jpg>
"""
import io
import sys

from PIL import Image, ImageDraw, ImageOps

imagem, rotulos, saida = sys.argv[1], sys.argv[2], sys.argv[3]

LARGURA_ALVO = 1600
COR = (242, 194, 0)   # amarelo de alto contraste sobre folhagem
ESPESSURA = 3

im = ImageOps.exif_transpose(Image.open(imagem)).convert("RGB")
if im.width > LARGURA_ALVO:
    altura = round(im.height * LARGURA_ALVO / im.width)
    im = im.resize((LARGURA_ALVO, altura), Image.LANCZOS)

desenho = ImageDraw.Draw(im)
n = 0
for linha in io.open(rotulos, encoding="utf-8"):
    partes = linha.split()
    if len(partes) < 5:
        continue
    cx, cy, w, h = (float(v) for v in partes[1:5])
    x0 = (cx - w / 2) * im.width
    y0 = (cy - h / 2) * im.height
    x1 = (cx + w / 2) * im.width
    y1 = (cy + h / 2) * im.height
    desenho.rectangle([x0, y0, x1, y1], outline=COR, width=ESPESSURA)
    n += 1

im.save(saida, "JPEG", quality=92, optimize=True, subsampling=0)
print("gravado %s  (%d caixas, %dx%d px)" % (saida, n, im.width, im.height))
