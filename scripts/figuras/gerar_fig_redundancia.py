"""Figura da curadoria por pHash, construída a partir de duplicadas_phash.csv.

Substitui a matriz de similaridade. A matriz anterior exibia uma fatia
de 30 pares escolhida por ordenação decrescente de similaridade, o que,
havendo 412 pares empatados em 100%, selecionava um recorte arbitrário;
agrupava as imagens pelo prefixo do nome de arquivo, que não corresponde
à partição em que a imagem estava; e preenchia com zero as células dos
pares não registrados, que não são pares de similaridade nula, e sim
pares abaixo do limiar.

Esta figura usa os 426 pares registrados e a partição real, dada pelo
diretório de cada imagem.

Uso: python3 -I gerar_fig_redundancia.py <duplicadas_phash.csv> <saida.pdf>
"""
import collections
import csv
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

entrada, saida = sys.argv[1], sys.argv[2]

NOMES = {"train": "treinamento", "val": "validação", "test": "teste"}
ENTRE = "#2b2b2b"
DENTRO = "#b4b4b4"


def pasta(caminho):
    return caminho.replace("\\", "/").split("/")[-2]


linhas = list(csv.DictReader(open(entrada, encoding="utf-8")))
contagem = collections.Counter(
    tuple(sorted((pasta(l["imagem_1"]), pasta(l["imagem_2"]))))
    for l in linhas
)
total = sum(contagem.values())
itens = sorted(contagem.items(), key=lambda x: x[1])

rotulos, valores, cores, texturas = [], [], [], []
for (a, b), v in itens:
    if a == b:
        rotulos.append(f"{NOMES[a].capitalize()} e {NOMES[b]}")
        cores.append(DENTRO)
        texturas.append("")
    else:
        rotulos.append(f"{NOMES[a].capitalize()} e {NOMES[b]}")
        cores.append(ENTRE)
        texturas.append("///")
    valores.append(v)

plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42})
fig, ax = plt.subplots(figsize=(5.85, 2.65))

barras = ax.barh(range(len(valores)), valores, height=0.62,
                 color=cores, edgecolor="white", linewidth=0.6)
for b, h in zip(barras, texturas):
    if h:
        b.set_hatch(h)

for i, v in enumerate(valores):
    ax.text(v + total * 0.012, i, f"{v}  ({100 * v / total:.1f} %)",
            va="center", ha="left", fontsize=7, color="#333333")

ax.set_yticks(range(len(rotulos)))
ax.set_yticklabels(rotulos, fontsize=7.5, color="#333333")
ax.set_xlabel("Pares de imagens acima do limiar de 90 %",
              fontsize=7.5, color="#333333")
ax.tick_params(axis="x", labelsize=7, colors="#555555", length=3)
ax.tick_params(axis="y", length=0)
ax.set_xlim(0, max(valores) * 1.30)
ax.xaxis.grid(True, color="#e2e2e2", lw=0.6)
ax.set_axisbelow(True)
for lado in ("top", "right", "left"):
    ax.spines[lado].set_visible(False)
ax.spines["bottom"].set_color("#999999")
ax.spines["bottom"].set_linewidth(0.6)

entre = sum(v for (a, b), v in contagem.items() if a != b)
legenda = [
    mpatches.Patch(facecolor=ENTRE, hatch="///", edgecolor="white",
                   label=f"partições distintas ({entre} pares, "
                         f"{100 * entre / total:.1f} %)"),
    mpatches.Patch(facecolor=DENTRO, edgecolor="white",
                   label=f"mesma partição ({total - entre} pares, "
                         f"{100 * (total - entre) / total:.1f} %)"),
]
ax.legend(handles=legenda, loc="lower right", frameon=False, fontsize=7,
          handlelength=1.3, handleheight=1.1, labelspacing=0.4)

fig.savefig(saida, bbox_inches="tight", pad_inches=0.02)
print(f"gravado {saida}  |  {total} pares, {entre} entre partições")
