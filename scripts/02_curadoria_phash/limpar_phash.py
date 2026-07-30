from pathlib import Path
from PIL import Image
import imagehash
import shutil
import csv
import itertools

# ==========================
# CONFIGURAÇÕES
# ==========================

PASTA_IMAGES = Path("dataset_final/images")
PASTA_LABELS = Path("dataset_final/labels")

SAIDA_LIMPA = Path("dataset_limpo")
CSV_DUPLICADAS = Path("duplicadas_phash.csv")
CSV_MANTIDAS = Path("imagens_mantidas.csv")

LIMIAR_SIMILARIDADE = 0.90

EXTENSOES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# ==========================
# FUNÇÕES
# ==========================

def calcular_phash(caminho):
    try:
        with Image.open(caminho) as img:
            return imagehash.phash(img.convert("RGB"))
    except Exception as e:
        print(f"Erro em {caminho}: {e}")
        return None


def similaridade(h1, h2):
    distancia = h1 - h2
    max_distancia = len(h1.hash) ** 2
    return 1 - (distancia / max_distancia)


# ==========================
# CARREGAR TODAS AS IMAGENS
# ==========================

imagens = []

for subset in ["train", "val", "test"]:
    pasta = PASTA_IMAGES / subset
    for img in pasta.rglob("*"):
        if img.suffix.lower() in EXTENSOES:
            imagens.append(img)

print(f"Total de imagens encontradas: {len(imagens)}")

hashes = {}

for img in imagens:
    h = calcular_phash(img)
    if h is not None:
        hashes[img] = h

print(f"Hashes calculados: {len(hashes)}")

# ==========================
# IDENTIFICAR DUPLICADAS
# ==========================

duplicadas = []
remover = set()
manter = set(hashes.keys())

for img1, img2 in itertools.combinations(hashes.keys(), 2):
    sim = similaridade(hashes[img1], hashes[img2])

    if sim >= LIMIAR_SIMILARIDADE:
        duplicadas.append([str(img1), str(img2), round(sim * 100, 2)])

        # regra simples: mantém a primeira, remove a segunda
        if img2 in manter:
            remover.add(img2)

manter = manter - remover

print(f"Pares duplicados encontrados: {len(duplicadas)}")
print(f"Imagens a remover: {len(remover)}")
print(f"Imagens mantidas: {len(manter)}")

# ==========================
# SALVAR CSVs
# ==========================

with open(CSV_DUPLICADAS, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["imagem_1", "imagem_2", "similaridade"])
    writer.writerows(duplicadas)

with open(CSV_MANTIDAS, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["imagem"])
    for img in sorted(manter):
        writer.writerow([str(img)])

# ==========================
# COPIAR DATASET LIMPO
# ==========================

saida_img = SAIDA_LIMPA / "images" / "all"
saida_lbl = SAIDA_LIMPA / "labels" / "all"

saida_img.mkdir(parents=True, exist_ok=True)
saida_lbl.mkdir(parents=True, exist_ok=True)

for img in manter:
    nome = img.name
    label_nome = img.with_suffix(".txt").name

    subset = img.parent.name

    label_origem = PASTA_LABELS / subset / label_nome

    shutil.copy2(img, saida_img / nome)

    if label_origem.exists():
        shutil.copy2(label_origem, saida_lbl / label_nome)
    else:
        print(f"Label não encontrada para: {img}")

print("Dataset limpo criado em:", SAIDA_LIMPA)
print("CSV de duplicadas:", CSV_DUPLICADAS)