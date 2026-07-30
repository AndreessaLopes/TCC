from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

CSV_DUPLICADAS = Path("duplicadas_phash.csv")
SAIDA = Path("matriz_similaridade_phash.png")

df = pd.read_csv(CSV_DUPLICADAS)

if df.empty:
    print("O CSV está vazio. Nenhuma matriz foi gerada.")
    exit()

# Usa só o nome do arquivo para deixar a matriz legível
df["imagem_1_nome"] = df["imagem_1"].apply(lambda x: os.path.basename(x))
df["imagem_2_nome"] = df["imagem_2"].apply(lambda x: os.path.basename(x))

# Para não gerar matriz gigante, pega os 30 pares mais semelhantes
df = df.sort_values("similaridade", ascending=False).head(30)

imagens = sorted(set(df["imagem_1_nome"]) | set(df["imagem_2_nome"]))

matriz = pd.DataFrame(0.0, index=imagens, columns=imagens)

for _, row in df.iterrows():
    img1 = row["imagem_1_nome"]
    img2 = row["imagem_2_nome"]
    sim = row["similaridade"]

    matriz.loc[img1, img2] = sim
    matriz.loc[img2, img1] = sim
    matriz.loc[img1, img1] = 100
    matriz.loc[img2, img2] = 100

plt.figure(figsize=(14, 12))
sns.heatmap(
    matriz,
    cmap="viridis",
    linewidths=0.3,
    annot=False,
    cbar_kws={"label": "Similaridade (%)"}
)

plt.title("Matriz de Similaridade Visual por pHash")
plt.xlabel("Imagens")
plt.ylabel("Imagens")
plt.xticks(rotation=90, fontsize=6)
plt.yticks(rotation=0, fontsize=6)
plt.tight_layout()
plt.savefig(SAIDA, dpi=300)
plt.close()

print(f"Matriz salva em: {SAIDA}")