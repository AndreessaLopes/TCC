import os

labels_path = "dataset_final/labels"

remover_arquivos_vazios = False  # mude pra True se quiser apagar labels vazios

total_erros = 0
total_linhas = 0
total_corrigidas = 0

for split in ["train", "val", "test"]:
    pasta = os.path.join(labels_path, split)

    for file in os.listdir(pasta):
        caminho = os.path.join(pasta, file)

        if not file.endswith(".txt"):
            continue

        with open(caminho, "r") as f:
            linhas = f.readlines()

        novas_linhas = []

        for linha in linhas:
            total_linhas += 1
            partes = linha.strip().split()

            # ❌ formato inválido
            if len(partes) != 5:
                total_erros += 1
                continue

            try:
                cls, x, y, w, h = map(float, partes)
            except:
                total_erros += 1
                continue

            # 🔧 força classe = 0
            cls = 0

            # ❌ valores inválidos
            if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1):
                total_erros += 1
                continue

            # ✔ mantém linha corrigida
            novas_linhas.append(f"{int(cls)} {x} {y} {w} {h}\n")
            total_corrigidas += 1

        # 🔥 reescreve arquivo
        if novas_linhas:
            with open(caminho, "w") as f:
                f.writelines(novas_linhas)
        else:
            if remover_arquivos_vazios:
                os.remove(caminho)

print("\n===== RELATÓRIO =====")
print(f"Total de linhas lidas: {total_linhas}")
print(f"Erros removidos: {total_erros}")
print(f"Linhas válidas mantidas: {total_corrigidas}")
print("=====================\n")