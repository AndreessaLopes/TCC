"""Confere a integridade das entradas do arquivo de referencias.

O conferir_regras.py ja verifica que toda citacao tem entrada e que toda
entrada e citada. Falta a verificacao de dentro da entrada, isto e, se os
campos exigidos por tipo estao presentes e se as fontes consultadas em
linha trazem endereco e data de acesso, como a norma pede.

Uso: python3 -I conferir_referencias.py <referencias.bib>
"""
import io
import re
import sys
from collections import Counter

caminho = sys.argv[1]
texto = io.open(caminho, encoding="utf-8").read()

EXIGIDOS = {
    "article": ("author", "title", "journal", "year"),
    "inproceedings": ("author", "title", "booktitle", "year"),
    "incollection": ("author", "title", "booktitle", "year"),
    "book": ("author", "title", "year"),
    "misc": ("author", "title", "year"),
    "online": ("author", "title", "year"),
    "techreport": ("author", "title", "year"),
}

entradas = []
for bloco in re.split(r"\n@", "\n" + texto)[1:]:
    m = re.match(r"(\w+)\s*\{\s*([^,]+),", bloco)
    if not m:
        continue
    tipo, chave = m.group(1).lower(), m.group(2).strip()
    campos = {}
    for c in re.finditer(r"^\s*(\w+)\s*=\s*[{\"](.*?)[}\"]\s*,?\s*$",
                         bloco, re.M | re.S):
        campos[c.group(1).lower()] = c.group(2).strip()
    entradas.append((chave, tipo, campos))

print("%d entradas lidas de %s\n" % (len(entradas), caminho))

problemas = []
for chave, tipo, campos in entradas:
    faltam = [c for c in EXIGIDOS.get(tipo, ("author", "title", "year"))
              if not campos.get(c)]
    if faltam:
        problemas.append((chave, "sem %s" % ", ".join(faltam)))
    # Fonte consultada em linha precisa de endereco e data de acesso.
    if campos.get("url") and not campos.get("urldate"):
        problemas.append((chave, "tem url sem data de acesso"))
    if not campos.get("doi") and not campos.get("url") \
            and not campos.get("eprint"):
        problemas.append((chave, "sem doi, url ou eprint"))
    ano = campos.get("year", "")
    if ano and not re.fullmatch(r"\d{4}", ano):
        problemas.append((chave, "ano em formato inesperado: %r" % ano))

# Chaves e titulos repetidos indicariam referencia duplicada.
for rotulo, valores in (("chave", [c for c, _, _ in entradas]),
                        ("titulo", [f.get("title", "").lower()
                                    for _, _, f in entradas])):
    for v, n in Counter(valores).items():
        if v and n > 1:
            problemas.append((v[:40], "%s repetido %d vezes" % (rotulo, n)))

if problemas:
    print("apontamentos:")
    for chave, descricao in problemas:
        print("  %-28s %s" % (chave, descricao))
else:
    print("nenhum apontamento")

anos = sorted(int(f["year"]) for _, _, f in entradas if f.get("year", "").isdigit())
if anos:
    print("\nanos: de %d a %d" % (anos[0], anos[-1]))
    print("de 2021 em diante: %d de %d" % (sum(1 for a in anos if a >= 2021),
                                           len(entradas)))
