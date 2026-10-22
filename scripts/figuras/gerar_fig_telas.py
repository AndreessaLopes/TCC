"""Figura com as telas da aplicacao.

O trabalho descreve a aplicacao em texto e nao a mostra em lugar nenhum.
Quatro telas cobrem o fluxo de uso e o instrumento de medida: a escolha
da configuracao, a captura com as caixas sobrepostas, a execucao em lote
e as metricas coletadas.

A barra de status do sistema e a barra de gestos sao recortadas. A
primeira traz hora e nivel de bateria do aparelho, que nada informam
sobre a aplicacao, e a segunda e desenho do sistema. A barra inferior da
propria aplicacao, com as quatro abas, permanece.

Uso: python3 -I gerar_fig_telas.py <pasta das capturas> <saida.jpg>
"""
import os
import sys

from PIL import Image

pasta, saida = sys.argv[1], sys.argv[2]

# Ordem do fluxo de uso, nao a ordem em que as capturas foram feitas.
TELAS = [
    ("Screenshot_20261020_180129.jpg", "a"),   # configuracao
    ("Screenshot_20261020_180237.jpg", "b"),   # captura
    ("Screenshot_20261020_180313.jpg", "c"),   # execucao em lote
    ("Screenshot_20261020_182102.jpg", "d"),   # metricas
]

CORTE_TOPO = 78       # barra de status do sistema
CORTE_BASE = 26       # barra de gestos do sistema
ESPACO = 26           # respiro entre as telas
MARGEM_ROTULO = 34    # faixa para a letra de cada painel
BORDA = (205, 198, 188)
FUNDO = (255, 255, 255)


def preparar(nome):
    im = Image.open(os.path.join(pasta, nome)).convert("RGB")
    l, a = im.size
    return im.crop((0, CORTE_TOPO, l, a - CORTE_BASE))


telas = [preparar(n) for n, _ in TELAS]
altura = min(t.size[1] for t in telas)
# Todas na mesma altura, para que a figura leia como uma sequencia.
telas = [t.resize((round(t.size[0] * altura / t.size[1]), altura),
                  Image.LANCZOS) for t in telas]

largura = sum(t.size[0] for t in telas) + ESPACO * (len(telas) - 1)
folha = Image.new("RGB", (largura, altura + MARGEM_ROTULO), FUNDO)

try:
    from PIL import ImageDraw, ImageFont
    desenho = ImageDraw.Draw(folha)
    fonte = None
    for caminho in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(caminho):
            fonte = ImageFont.truetype(caminho, 30)
            break
except ImportError:
    desenho, fonte = None, None

x = 0
for tela, (_, letra) in zip(telas, TELAS):
    folha.paste(tela, (x, MARGEM_ROTULO))
    if desenho is not None:
        desenho.rectangle(
            [x, MARGEM_ROTULO, x + tela.size[0] - 1,
             MARGEM_ROTULO + altura - 1], outline=BORDA, width=2)
        desenho.text((x + 2, 2), "(%s)" % letra, fill=(60, 60, 60), font=fonte)
    x += tela.size[0] + ESPACO

# 2.400 px de largura bastam para a figura ocupar a largura do texto com
# folga de resolucao na impressao.
alvo = 2400
if folha.size[0] > alvo:
    folha = folha.resize(
        (alvo, round(folha.size[1] * alvo / folha.size[0])), Image.LANCZOS)

folha.save(saida, quality=92, subsampling=1, optimize=True)
print("gravado %s  %dx%d  %.0f KB"
      % (saida, folha.size[0], folha.size[1],
         os.path.getsize(saida) / 1024))
