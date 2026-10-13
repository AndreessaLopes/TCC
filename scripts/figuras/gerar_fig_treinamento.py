"""Figura da evolução do treinamento dos dois modelos.

Substitui as duas figuras geradas pelo Ultralytics, que traziam dez
painéis cada uma, com rótulos de eixo ilegíveis na página e eixos em
inglês com ponto decimal.

Quatro painéis. Os dois de cima mostram, para cada arquitetura, a perda
de caixa em treinamento e em validação, com o mínimo da curva de
validação assinalado. Os dois de baixo comparam as arquiteturas nas
métricas de avaliação, que são grandezas equivalentes entre elas. As
perdas não são comparadas entre arquiteturas porque o YOLOv10 emprega
formulação distinta, o que tornaria a comparação de valores absolutos
sem significado.

Uso: python3 -I gerar_fig_treinamento.py <v8n.csv> <v10n.csv> <saida.pdf>
"""
import csv
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TREINO = "#1f77b4"
VALID = "#ff7f0e"
V8 = "#1f77b4"
V10 = "#ff7f0e"


def ler(caminho):
    linhas = [{k.strip(): v for k, v in r.items()}
              for r in csv.DictReader(open(caminho, encoding="utf-8"))]
    return {
        "epoca": [int(r["epoch"]) for r in linhas],
        "treino": [float(r["train/box_loss"]) for r in linhas],
        "valid": [float(r["val/box_loss"]) for r in linhas],
        "map50": [float(r["metrics/mAP50(B)"]) for r in linhas],
        "map5095": [float(r["metrics/mAP50-95(B)"]) for r in linhas],
    }


v8, v10, saida = ler(sys.argv[1]), ler(sys.argv[2]), sys.argv[3]

plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42})
fig, eixos = plt.subplots(2, 2, figsize=(5.85, 4.2))


def virgula(x, _):
    return f"{x:.2f}".replace(".", ",")


def painel_perda(ax, d, titulo):
    ax.plot(d["epoca"], d["treino"], color=TREINO, lw=1.6,
            label="Treinamento")
    ax.plot(d["epoca"], d["valid"], color=VALID, lw=1.6, ls="--",
            label="Validação")
    i = d["valid"].index(min(d["valid"]))
    ax.plot(d["epoca"][i], d["valid"][i], "o", ms=5, color=VALID,
            mec="white", mew=1.0, zorder=5)
    ax.text(0.02, 0.04,
            f"mínimo da validação na época {d['epoca'][i]}",
            transform=ax.transAxes, fontsize=6, color="#666666",
            ha="left", va="bottom")
    ax.set_title(titulo, fontsize=8, color="#333333", pad=4)
    ax.set_ylabel("Perda de caixa", fontsize=7, color="#333333")
    ax.legend(frameon=False, fontsize=6.5, loc="upper right",
              handlelength=1.6)


def painel_metrica(ax, chave, titulo):
    ax.plot(v8["epoca"], v8[chave], color=V8, lw=1.6, label="YOLOv8n")
    ax.plot(v10["epoca"], v10[chave], color=V10, lw=1.6, ls="--",
            label="YOLOv10n")
    ax.set_title(titulo, fontsize=8, color="#333333", pad=4)
    ax.legend(frameon=False, fontsize=6.5, loc="lower right",
              handlelength=1.6)


painel_perda(eixos[0][0], v8, "YOLOv8n")
painel_perda(eixos[0][1], v10, "YOLOv10n")
painel_metrica(eixos[1][0], "map50", "mAP@0,50")
painel_metrica(eixos[1][1], "map5095", "mAP@0,50–0,95")

for linha in eixos:
    for ax in linha:
        ax.set_xlabel("Época", fontsize=7, color="#333333")
        ax.tick_params(labelsize=6.5, colors="#666666", length=3)
        ax.yaxis.set_major_formatter(virgula)
        ax.grid(color="#ececec", lw=0.6)
        ax.set_axisbelow(True)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
        for lado in ("bottom", "left"):
            ax.spines[lado].set_color("#aaaaaa")
            ax.spines[lado].set_linewidth(0.6)
        for rotulo in ax.get_xticklabels() + ax.get_yticklabels():
            rotulo.set_color("#444444")

fig.tight_layout(pad=0.6, w_pad=1.6, h_pad=1.4)
fig.savefig(saida, bbox_inches="tight", pad_inches=0.02)
print(f"gravado {saida}")
