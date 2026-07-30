"""
Gera o gráfico de distribuição das imagens entre os subconjuntos de
treinamento, validação e teste.

Os valores correspondem ao conjunto consolidado, posterior à curadoria por
pHash e à revisão do critério de anotação.
"""

import matplotlib.pyplot as plt

# Distribuição do conjunto consolidado
labels = ["Treinamento", "Validação", "Teste"]
valores = [1410, 473, 285]
total = sum(valores)
cores = ["#1f77b4", "#ff7f0e", "#2ca02c"]

SAIDA = "distribuicao_dataset.png"


def formatar_percentual(pct):
    valor = int(round(pct / 100 * total))
    return f"{pct:.2f}%\n({valor})"


fig, ax = plt.subplots(figsize=(7, 7))

wedges, texts, autotexts = ax.pie(
    valores,
    labels=labels,
    autopct=formatar_percentual,
    colors=cores,
    startangle=90,
    textprops={"fontsize": 11},
)

for autotext in autotexts:
    autotext.set_fontsize(10)

ax.set_title("")
plt.tight_layout()
plt.savefig(SAIDA, dpi=300, bbox_inches="tight")

print(f"Figura salva em: {SAIDA}")
print(f"Total: {total}")
for nome, valor in zip(labels, valores):
    print(f"  {nome}: {valor} ({valor / total * 100:.2f}%)")
