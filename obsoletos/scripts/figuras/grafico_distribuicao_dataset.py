import matplotlib.pyplot as plt

# Dados corretos (pos-curadoria por pHash) - Tabela 2
labels = ['Treinamento', 'Validação', 'Teste']
valores = [1410, 473, 285]
total = sum(valores)
cores = ['#1f77b4', '#ff7f0e', '#2ca02c']  # azul, laranja, verde

fig, ax = plt.subplots(figsize=(7, 7))

def autopct_format(pct):
    val = int(round(pct/100*total))
    return f'{pct:.2f}%\n({val})'

wedges, texts, autotexts = ax.pie(
    valores,
    labels=labels,
    autopct=autopct_format,
    colors=cores,
    startangle=90,
    textprops={'fontsize': 11}
)

for autotext in autotexts:
    autotext.set_fontsize(10)

ax.set_title('')
plt.tight_layout()
plt.savefig('distribuicao_dataset.png', dpi=300, bbox_inches='tight')
print("Total:", total)
for l, v in zip(labels, valores):
    print(f"{l}: {v} ({v/total*100:.2f}%)")