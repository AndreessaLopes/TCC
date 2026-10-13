from pathlib import Path
from PIL import Image
import imagehash
import csv

TRAIN = Path("dataset_24_06/images/val")
VAL = Path("dataset_24_06/images/test")

SAIDA = "phash_train_val.csv"

EXTENSOES = {".jpg", ".jpeg", ".png"}

LIMIAR = 0.90


def calcular_phash(img_path):
    try:
        with Image.open(img_path) as img:
            return imagehash.phash(img.convert("RGB"))
    except:
        return None


def similaridade(hash1, hash2):
    distancia = hash1 - hash2
    max_distancia = len(hash1.hash) ** 2
    return 1 - (distancia / max_distancia)


print("Calculando hashes TRAIN...")

hash_train = {}

for img in TRAIN.rglob("*"):
    if img.suffix.lower() in EXTENSOES:
        h = calcular_phash(img)
        if h:
            hash_train[img] = h

print("Calculando hashes VAL...")

hash_val = {}

for img in VAL.rglob("*"):
    if img.suffix.lower() in EXTENSOES:
        h = calcular_phash(img)
        if h:
            hash_val[img] = h

print("Comparando...")

pares = []

for img_train, h_train in hash_train.items():

    for img_val, h_val in hash_val.items():

        sim = similaridade(h_train, h_val)

        if sim >= LIMIAR:

            pares.append([
                str(img_train),
                str(img_val),
                round(sim * 100, 2)
            ])

print(f"Pares encontrados: {len(pares)}")

with open(SAIDA, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow([
        "imagem_train",
        "imagem_val",
        "similaridade"
    ])

    writer.writerows(pares)

print("Arquivo salvo:", SAIDA)