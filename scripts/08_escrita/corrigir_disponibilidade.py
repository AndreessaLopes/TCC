# -*- coding: utf-8 -*-
"""Atualiza a Secao de disponibilidade dos dados e do codigo.

A redacao anterior afirmava que a divulgacao das imagens dependia de
autorizacao ainda nao obtida. A autorizacao foi obtida, de modo que a
frase passou a ser falsa.

Uso: python corrigir_disponibilidade.py <caminho do artigo.tex>
"""

import io
import re
import sys

ANTIGO = (
    u"O conjunto de imagens de lavoura não integra o depósito, uma vez que "
    u"as imagens foram adquiridas em propriedades privadas e sua divulgação "
    u"depende de autorização dos proprietários das áreas, ainda não obtida."
)

NOVO = (
    u"O conjunto de imagens de lavoura não integra esse depósito, por volume, "
    u"e é distribuído à parte. A autorização de divulgação pelos proprietários "
    u"das áreas em que as imagens foram adquiridas foi obtida, e o conjunto, "
    u"composto por 2.168 imagens e 17.659 instâncias anotadas, é disponibilizado "
    u"sob licença Creative Commons Atribuição 4.0 Internacional, com os metadados "
    u"EXIF, XMP e IPTC removidos dos arquivos, que registravam a coordenada de "
    u"aquisição em 618 das imagens. Enquanto o depósito em repositório de dados "
    u"não é concluído, o acesso é fornecido mediante solicitação à autora."
)


def trocar(texto, rotulo, antigo, novo):
    padrao = r"\s+".join(re.escape(p) for p in antigo.split())
    n = len(re.findall(padrao, texto))
    if n != 1:
        sys.exit("FALHOU em %s: %d ocorrencias" % (rotulo, n))
    return re.sub(padrao, lambda _: novo, texto, count=1)


def main():
    if len(sys.argv) != 2:
        sys.exit("uso: corrigir_disponibilidade.py <artigo.tex>")
    caminho = sys.argv[1]
    with io.open(caminho, "r", encoding="utf-8") as f:
        texto = f.read()

    texto = trocar(texto, "disponibilidade das imagens", ANTIGO, NOVO)

    with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
    print("Paragrafo atualizado.")


if __name__ == "__main__":
    main()
