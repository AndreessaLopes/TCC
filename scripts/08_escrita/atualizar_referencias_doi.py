# -*- coding: utf-8 -*-
"""Registra o DOI do conjunto de imagens e corrige a entrada do deposito.

Tres mudancas.

1. A entrada do conjunto passa a trazer o DOI emitido pela Kaggle, que
   dispensa a data de acesso, exigida pela NBR 6023:2025 apenas para
   conteudo instavel.
2. A entrada do deposito perde o campo de versao, que indicava 1.0.0
   enquanto o DOI registrado e o de conceito, o qual resolve sempre para
   a versao mais recente.
3. A entrada do deposito perde a data de acesso, pela mesma razao do
   item 1.

Uso: python atualizar_referencias_doi.py <referencias.bib>
"""

import io
import re
import sys

ANTIGO_CONJUNTO = """@misc{Assis2026Conjunto,
  author       = {Lopes de Assis, Andressa Caroline},
  title        = {Coffee fruit detection in the field ({YOLO})},
  year         = {2026},
  publisher    = {Kaggle},
  howpublished = {Conjunto de dados},
  url          = {https://www.kaggle.com/datasets/andressac/coffee-fruit-detection-yolo},
  urldate      = {2026-11-06},
}"""

NOVO_CONJUNTO = """@misc{Assis2026Conjunto,
  author       = {Lopes de Assis, Andressa Caroline},
  title        = {Coffee fruit detection in the field ({YOLO})},
  year         = {2026},
  publisher    = {Kaggle},
  howpublished = {Conjunto de dados},
  doi          = {10.34740/KAGGLE/DSV/21781111},
  url          = {https://doi.org/10.34740/KAGGLE/DSV/21781111},
}"""

ANTIGO_VERSAO = """  version      = {1.0.0},
  doi          = {10.5281/zenodo.23989617},
  url          = {https://doi.org/10.5281/zenodo.23989617},
  urldate      = {2026-11-05},"""

NOVO_VERSAO = """  doi          = {10.5281/zenodo.23989617},
  url          = {https://doi.org/10.5281/zenodo.23989617},"""


def trocar(texto, rotulo, antigo, novo):
    n = texto.count(antigo)
    if n != 1:
        sys.exit("FALHOU em %s: %d ocorrencias" % (rotulo, n))
    return texto.replace(antigo, novo, 1)


def main():
    if len(sys.argv) != 2:
        sys.exit("uso: atualizar_referencias_doi.py <referencias.bib>")
    caminho = sys.argv[1]
    with io.open(caminho, "r", encoding="utf-8") as f:
        texto = f.read()
    texto = trocar(texto, "entrada do conjunto", ANTIGO_CONJUNTO, NOVO_CONJUNTO)
    texto = trocar(texto, "versao e acesso do deposito", ANTIGO_VERSAO, NOVO_VERSAO)
    with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
    print("Referencias atualizadas.")


if __name__ == "__main__":
    main()
