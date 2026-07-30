from pathlib import Path
from PIL import Image
import imagehash
import itertools
import csv

# ==========================
# CONFIGURACOES
# ==========================

PASTA_IMAGENS = Path("dataset_final/images/test")  # ajuste aqui pro caminho correto da pasta de imagens
SAIDA_CSV = Path("resultados_phash_test.csv")

LIMIARES_SIMILARIDADE = [0.80, 0.85, 0.90]

EXTENSOES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# ==========================
# FUNCOES
# ==========================

def calcular_phash(caminho_imagem):
    try:
        with Image.open(caminho_imagem) as img:
            img = img.convert("RGB")
            return imagehash.phash(img)
    except Exception as erro:
        print(f"Erro ao processar {caminho_imagem}: {erro}")
        return None


def similaridade(hash1, hash2):
    distancia = hash1 - hash2
    max_distancia = len(hash1.hash) ** 2
    return 1 - (distancia / max_distancia)


# ==========================
# PROCESSAMENTO
# ==========================

imagens = [
    p for p in PASTA_IMAGENS.rglob("*")
    if p.suffix.lower() in EXTENSOES
]

print(f"Total de imagens encontradas: {len(imagens)}")

hashes = {}

for img_path in imagens:
    h = calcular_phash(img_path)
    if h is not None:
        hashes[img_path] = h

print(f"Hashes calculados: {len(hashes)}")

pares_semelhantes = []

for (img1, h1), (img2, h2) in itertools.combinations(hashes.items(), 2):
    sim = similaridade(h1, h2)

    if sim >= min(LIMIARES_SIMILARIDADE):
        pares_semelhantes.append({
            "imagem_1": str(img1),
            "imagem_2": str(img2),
            "similaridade": round(sim * 100, 2)
        })

print(f"Pares semelhantes encontrados: {len(pares_semelhantes)}")

with open(SAIDA_CSV, "w", newline="", encoding="utf-8") as f:
    campos = ["imagem_1", "imagem_2", "similaridade"]
    writer = csv.DictWriter(f, fieldnames=campos)
    writer.writeheader()
    writer.writerows(pares_semelhantes)

print(f"Resultado salvo em: {SAIDA_CSV}")