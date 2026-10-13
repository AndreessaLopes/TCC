"""Verifica se sobrou imagem repetida entre treinamento, validação e teste.

Compara as três combinações de uma vez: treinamento com validação,
treinamento com teste e validação com teste.

COMO USAR
    1. Coloque este arquivo na raiz do ProjetoCafe.
    2. Rode:  python verificar_vazamento.py
    3. Me mande o vazamento_entre_particoes.csv que ele gera.

Não precisa configurar caminho. O script procura sozinho as pastas
train, val e test dentro do projeto e mostra o que encontrou. Se houver
mais de um conjunto possível, ele lista todos e pergunta qual usar.

Para escolher um conjunto específico, rode com o caminho como argumento:
    python verificar_vazamento.py dataset_final
"""

from pathlib import Path
import csv
import itertools
import sys

from PIL import Image
import imagehash

LIMIAR = 0.90
EXTENSOES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SAIDA = Path("vazamento_entre_particoes.csv")

NOMES = {
    "train": ("train", "treino", "treinamento"),
    "val": ("val", "valid", "validacao", "validação"),
    "test": ("test", "teste"),
}

IGNORAR = {"venv", ".git", "__pycache__", "node_modules", "runs", ".vscode"}


def papel(nome):
    """Diz se o nome da pasta corresponde a train, val ou test."""
    n = nome.lower()
    for chave, variantes in NOMES.items():
        if n in variantes:
            return chave
    return None


def conta_imagens(pasta):
    return sum(1 for p in pasta.rglob("*")
               if p.suffix.lower() in EXTENSOES)


def procurar_conjuntos(raiz):
    """Procura pastas-mãe que contenham train, val e test com imagens."""
    achados = {}
    for caminho in raiz.rglob("*"):
        if not caminho.is_dir():
            continue
        if any(parte in IGNORAR for parte in caminho.parts):
            continue
        p = papel(caminho.name)
        if p is None:
            continue
        n = conta_imagens(caminho)
        if n == 0:
            continue
        achados.setdefault(caminho.parent, {})[p] = (caminho, n)
    completos = {mae: d for mae, d in achados.items() if len(d) == 3}
    return completos, achados


def calcular_phash(caminho):
    try:
        with Image.open(caminho) as img:
            return imagehash.phash(img.convert("RGB"))
    except Exception as erro:
        print(f"  erro ao abrir {caminho}: {erro}")
        return None


def similaridade(h1, h2):
    distancia = h1 - h2
    max_distancia = len(h1.hash) ** 2
    return 1 - (distancia / max_distancia)


# =====================================================================
# 1. LOCALIZAR O CONJUNTO
# =====================================================================

raiz = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

if not raiz.is_dir():
    raise SystemExit(f"Pasta não encontrada: {raiz.resolve()}")

print(f"Procurando em {raiz.resolve()} ...\n")

completos, todos = procurar_conjuntos(raiz)

if not completos:
    print("Não encontrei nenhuma pasta com train, val e test juntas.")
    if todos:
        print("\nO que encontrei solto foi isto:\n")
        for mae, d in sorted(todos.items(), key=lambda x: str(x[0])):
            partes = ", ".join(f"{k} ({v[1]} imagens)"
                               for k, v in sorted(d.items()))
            print(f"  {mae}  ->  {partes}")
        print("\nRode de novo apontando para a pasta-mãe certa, por "
              "exemplo:\n  python verificar_vazamento.py dataset_final")
    else:
        print("Nenhuma pasta train, val ou test com imagens dentro de "
              f"{raiz.resolve()}")
    raise SystemExit(1)

if len(completos) > 1:
    print("Encontrei mais de um conjunto completo:\n")
    for mae, d in sorted(completos.items(), key=lambda x: str(x[0])):
        total = sum(v[1] for v in d.values())
        partes = ", ".join(f"{k} {v[1]}" for k, v in sorted(d.items()))
        print(f"  {mae}   ({partes})   total {total}")
    print("\nRode de novo apontando para o certo, que é o conjunto "
          "DEPOIS da\nremoção das redundâncias e da redistribuição. "
          "Por exemplo:\n  python verificar_vazamento.py dataset_final")
    raise SystemExit(1)

mae, conjunto = next(iter(completos.items()))
print(f"Conjunto encontrado em: {mae}")
for p in ("train", "val", "test"):
    print(f"  {p}: {conjunto[p][1]} imagens  ({conjunto[p][0]})")
print()

# =====================================================================
# 2. CALCULAR OS HASHES
# =====================================================================

hashes = {}

for p in ("train", "val", "test"):
    pasta = conjunto[p][0]
    hashes[p] = {}
    for img in pasta.rglob("*"):
        if img.suffix.lower() in EXTENSOES:
            h = calcular_phash(img)
            if h is not None:
                hashes[p][img] = h

print("Hashes calculados. Comparando...\n")

# =====================================================================
# 3. COMPARAR AS TRÊS COMBINAÇÕES
# =====================================================================

pares = []

for p1, p2 in itertools.combinations(("train", "val", "test"), 2):
    encontrados = 0
    for img1, h1 in hashes[p1].items():
        for img2, h2 in hashes[p2].items():
            sim = similaridade(h1, h2)
            if sim >= LIMIAR:
                pares.append([p1, p2, str(img1), str(img2),
                              round(sim * 100, 2)])
                encontrados += 1
    print(f"  {p1} x {p2}: {encontrados} pares acima de "
          f"{round(LIMIAR * 100)}%")

# =====================================================================
# 4. GRAVAR
# =====================================================================

with open(SAIDA, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["particao_1", "particao_2",
                     "imagem_1", "imagem_2", "similaridade"])
    writer.writerows(pares)

print()
print(f"Total de pares entre partições: {len(pares)}")
print(f"Arquivo gerado: {SAIDA.resolve()}")
print()

if pares:
    print("ATENÇÃO: há imagens repetidas entre as partições.")
else:
    print("Nenhuma imagem repetida entre as partições.")
