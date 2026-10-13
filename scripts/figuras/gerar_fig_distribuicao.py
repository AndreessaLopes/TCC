"""Figura da distribuição das imagens entre as partições.

Substitui distribuicao_dataset.png, que era um gráfico de setores com
separador decimal em ponto, contrariando a convenção do trabalho. A
barra empilhada também compara as três parcelas com mais precisão do
que setores, porque a leitura se dá em uma única dimensão.

Uso: python3 -I gerar_fig_distribuicao.py <saida.pdf>
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

saida = sys.argv[1]

PARTICOES = [
    ("Treinamento", 1410, "#3a3a3a", ""),
    ("Validação", 473, "#8f8f8f", "///"),
    ("Teste", 285, "#cfcfcf", "..."),
]

total = sum(n for _, n, _, _ in PARTICOES)

plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42})
fig, ax = plt.subplots(figsize=(5.85, 1.75))

def milhar(n):
    return f"{n:,}".replace(",", ".")

for i, (nome, n, cor, textura) in enumerate(PARTICOES):
    y = len(PARTICOES) - 1 - i
    ax.barh(y, n, height=0.52, color=cor, edgecolor="white",
            linewidth=0.8, hatch=textura)
    pct = f"{100 * n / total:.2f}".replace(".", ",")
    ax.text(n + total * 0.012, y, f"{milhar(n)}  ({pct}\u2009%)",
            va="center", ha="left", fontsize=7.4, color="#333333")

ax.set_yticks(range(len(PARTICOES)))
ax.set_yticklabels([p[0] for p in reversed(PARTICOES)],
                   fontsize=7.8, color="#333333")
ax.set_xlim(0, total * 1.22)
ax.set_xticks([0, 500, 1000, 1500])
ax.set_xticklabels(["0", "500", "1.000", "1.500"],
                   fontsize=7, color="#555555")
ax.set_xlabel(f"Imagens (total de {milhar(total)})",
              fontsize=7.5, color="#333333")
ax.tick_params(axis="x", length=3, colors="#888888")
ax.tick_params(axis="y", length=0)
ax.xaxis.grid(True, color="#e4e4e4", lw=0.6)
ax.set_axisbelow(True)
for lado in ("top", "right", "left"):
    ax.spines[lado].set_visible(False)
ax.spines["bottom"].set_color("#999999")
ax.spines["bottom"].set_linewidth(0.6)

fig.savefig(saida, bbox_inches="tight", pad_inches=0.02)
print(f"gravado {saida}  |  total {total}")
