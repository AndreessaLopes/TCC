# -*- coding: utf-8 -*-
"""Menciona os repositorios no ultimo paragrafo da Introducao.

Acrescenta, ao final do paragrafo de organizacao do documento, a frase
que remete ao deposito de codigo e ao conjunto de imagens, no mesmo
padrao adotado em trabalhos anteriores do grupo.

Uso: python citar_repositorios_introducao.py <artigo.tex>
"""

import io
import re
import sys

ANTIGO = (
    u"e a Seção~\\ref{sec:conclusao} sintetiza as conclusões, as limitações "
    u"do estudo e as possibilidades de continuidade."
)

NOVO = (
    u"e a Seção~\\ref{sec:conclusao} sintetiza as conclusões, as limitações "
    u"do estudo e as possibilidades de continuidade. Além das seções deste "
    u"documento, o código desenvolvido ao longo do trabalho, a aplicação "
    u"Android, os modelos convertidos e os arquivos de medição encontram-se "
    u"disponíveis publicamente em repositório indexado~\\cite{Assis2026Repositorio}, "
    u"e o conjunto de imagens em repositório de dados de acesso "
    u"aberto~\\cite{Assis2026Conjunto}."
)


def trocar(texto, rotulo, antigo, novo):
    padrao = r"\s+".join(re.escape(p) for p in antigo.split())
    n = len(re.findall(padrao, texto))
    if n != 1:
        sys.exit("FALHOU em %s: %d ocorrencias" % (rotulo, n))
    return re.sub(padrao, lambda _: novo, texto, count=1)


def main():
    if len(sys.argv) != 2:
        sys.exit("uso: citar_repositorios_introducao.py <artigo.tex>")
    caminho = sys.argv[1]
    with io.open(caminho, "r", encoding="utf-8") as f:
        texto = f.read()
    texto = trocar(texto, "paragrafo de organizacao", ANTIGO, NOVO)
    with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
    print("Frase acrescentada ao paragrafo de organizacao.")


if __name__ == "__main__":
    main()
