"""Figura das curvas de precisao e revocacao dos dois modelos.

Substitui as duas figuras geradas pelo Ultralytics, que traziam eixos em
ingles com ponto decimal e ocupavam uma pagina cada. Reunidas em um unico
grafico, a proximidade entre as curvas, afirmada no texto, passa a ser
visivel em vez de depender da comparacao entre duas paginas.

A curva e tracada de forma parametrica: cada ponto corresponde a um
limiar de confianca, com a revocacao no eixo horizontal e a precisao no
vertical. Assinala-se o limiar de 0,25, adotado pelo aplicativo.

Uso: python3 -I gerar_fig_curvas_pr.py <v8n.csv> <v10n.csv> <saida.pdf>
"""
import csv
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

LIMIAR_APLICACAO = 0.25

SERIES = [
    ("YOLOv8n", "#2b2b2b", "-", "o"),
    ("YOLOv10n", "#8a8a8a", "--", "s"),
]


def ler(caminho):
    linhas = list(csv.DictReader(open(caminho, encoding="utf-8")))
    return [(float(d["limiar_confianca"]), float(d["revocacao"]),
             float(d["precisao"])) for d in linhas]


def virgula(x, _):
    return ("%.1f" % x).replace(".", ",")


v8, v10, saida = ler(sys.argv[1]), ler(sys.argv[2]), sys.argv[3]

plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42})
fig, ax = plt.subplots(figsize=(5.0, 3.6))

for dados, (rotulo, cor, traco, marca) in zip((v8, v10), SERIES):
    # A curva so e informativa onde ha deteccoes; o limiar 1,0 colapsa em
    # revocacao nula e distorce a leitura do inicio do eixo.
    pontos = [(r, p) for _, r, p in dados if r > 0]
    ax.plot([r for r, _ in pontos], [p for _, p in pontos],
            color=cor, ls=traco, lw=1.6, label=rotulo, zorder=3)

    opera = min(dados, key=lambda t: abs(t[0] - LIMIAR_APLICACAO))
    ax.plot(opera[1], opera[2], marker=marca, ms=5, color=cor,
            mec="white", mew=1.0, zorder=5, ls="none")

ax.annotate("limiar de 0,25,\nadotado no aplicativo",
            xy=(v8[min(range(len(v8)),
                       key=lambda i: abs(v8[i][0] - LIMIAR_APLICACAO))][1],
                v8[min(range(len(v8)),
                       key=lambda i: abs(v8[i][0] - LIMIAR_APLICACAO))][2]),
            xytext=(0.40, 0.30), fontsize=6.5, color="#555555",
            ha="center", va="top",
            arrowprops=dict(arrowstyle="-", color="#999999", lw=0.7,
                            shrinkA=2, shrinkB=4))

ax.set_xlabel("Revocação", fontsize=8, color="#333333")
ax.set_ylabel("Precisão", fontsize=8, color="#333333")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
ax.xaxis.set_major_formatter(virgula)
ax.yaxis.set_major_formatter(virgula)
ax.grid(color="#ececec", lw=0.6)
ax.set_axisbelow(True)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
for lado in ("bottom", "left"):
    ax.spines[lado].set_color("#aaaaaa")
    ax.spines[lado].set_linewidth(0.6)
ax.tick_params(labelsize=7, colors="#666666", length=3)
for rotulo in ax.get_xticklabels() + ax.get_yticklabels():
    rotulo.set_color("#444444")
ax.legend(frameon=False, fontsize=7, loc="upper right", handlelength=1.8)

fig.tight_layout(pad=0.4)
fig.savefig(saida, bbox_inches="tight", pad_inches=0.02)
print("gravado %s" % saida)
