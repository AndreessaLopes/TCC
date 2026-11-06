# -*- coding: utf-8 -*-
"""Aponta o conjunto de imagens publicado na Secao de disponibilidade.

Substitui a frase provisoria, que oferecia o acesso mediante solicitacao,
pela citacao do conjunto publicado, e acrescenta a entrada correspondente
ao arquivo de referencias.

Uso: python registrar_dataset.py <artigo.tex> <referencias.bib>
"""

import io
import re
import sys

ANTIGO = (
    u"Enquanto o depósito em repositório de dados não é concluído, o acesso "
    u"é fornecido mediante solicitação à autora."
)

NOVO = (
    u"O conjunto encontra-se publicado em repositório de dados de acesso "
    u"aberto~\\cite{Assis2026Conjunto}."
)

ENTRADA = u"""
% Conjunto de imagens publicado a parte do deposito de codigo, por volume.
@misc{Assis2026Conjunto,
  author       = {Lopes de Assis, Andressa Caroline},
  title        = {Coffee fruit detection in the field ({YOLO})},
  year         = {2026},
  publisher    = {Kaggle},
  howpublished = {Conjunto de dados},
  url          = {https://www.kaggle.com/datasets/andressac/coffee-fruit-detection-yolo},
  urldate      = {2026-11-06},
}
"""


def trocar(texto, rotulo, antigo, novo):
    padrao = r"\s+".join(re.escape(p) for p in antigo.split())
    n = len(re.findall(padrao, texto))
    if n != 1:
        sys.exit("FALHOU em %s: %d ocorrencias" % (rotulo, n))
    return re.sub(padrao, lambda _: novo, texto, count=1)


def main():
    if len(sys.argv) != 3:
        sys.exit("uso: registrar_dataset.py <artigo.tex> <referencias.bib>")
    tex, bib = sys.argv[1], sys.argv[2]

    with io.open(bib, "r", encoding="utf-8") as f:
        referencias = f.read()
    if "Assis2026Conjunto" in referencias:
        sys.exit("FALHOU: a entrada Assis2026Conjunto ja existe")

    with io.open(tex, "r", encoding="utf-8") as f:
        texto = f.read()
    texto = trocar(texto, "frase provisoria de acesso", ANTIGO, NOVO)

    with io.open(tex, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
    with io.open(bib, "a", encoding="utf-8", newline="\n") as f:
        f.write(ENTRADA)
    print("Frase substituida e entrada acrescentada.")


if __name__ == "__main__":
    main()
