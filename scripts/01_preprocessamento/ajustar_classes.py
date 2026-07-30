import os

# caminhos
base = "dataset/labels"

pastas = {
    "amarelas": 0,
    "vermelhas": 1
}

for pasta, classe in pastas.items():
    caminho = os.path.join(base, pasta)

    for arquivo in os.listdir(caminho):
        if arquivo.endswith(".txt"):
            path = os.path.join(caminho, arquivo)

            with open(path, "r") as f:
                linhas = f.readlines()

            novas = []
            for linha in linhas:
                partes = linha.strip().split()
                if len(partes) >= 5:
                    partes[0] = str(classe)
                    novas.append(" ".join(partes))

            with open(path, "w") as f:
                f.write("\n".join(novas))

print("Classes ajustadas com sucesso!")