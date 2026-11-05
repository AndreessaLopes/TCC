# -*- coding: utf-8 -*-
"""Oculta a lista de siglas sem perder o funcionamento do \\ac.

O modelo oficial de artigo do curso nao traz lista de siglas. As
declaracoes do ambiente acronym, porem, sao o que faz o \\ac expandir a
sigla na primeira ocorrencia, e elas trafegam pelo arquivo auxiliar. Por
isso o ambiente nao pode ir para dentro de uma caixa descartada, cujas
escritas nunca chegam ao .aux. A opcao nolist do proprio pacote suprime a
impressao da lista e preserva as declaracoes, alem de desligar os
hiperlinks que apontariam para a lista ausente.
"""
import sys

ARQ = sys.argv[1]
t = open(ARQ, encoding="utf-8").read()


def trocar(rotulo, antigo, novo):
    global t
    if t.count(antigo) != 1:
        sys.exit("FALHOU em %s, %d ocorrencias" % (rotulo, t.count(antigo)))
    t = t.replace(antigo, novo)
    print("ok  %s" % rotulo)


trocar(
    "opcao nolist",
    "\\usepackage{acronym}",
    "\\usepackage[nolist]{acronym}",
)

trocar(
    "cabecalho e quebra de pagina",
    "\\maketitle\n\\newpage\n\n\\section*{LISTA DE SIGLAS}\n"
    "\\addcontentsline{toc}{section}{LISTA DE SIGLAS}\n\n"
    "\\begin{acronym}[OpenCV]",

    "\\maketitle\n\n"
    "% A lista de siglas nao e impressa, por nao constar do modelo oficial\n"
    "% de artigo do curso. As declaracoes abaixo permanecem porque sao elas\n"
    "% que fazem o \\ac expandir a sigla na primeira ocorrencia.\n"
    "\\begin{acronym}[OpenCV]",
)

trocar(
    "quebra apos a lista",
    "\\end{acronym}\n\n\\newpage\n\\acresetall",
    "\\end{acronym}\n\n\\acresetall",
)

open(ARQ, "w", encoding="utf-8").write(t)
print("\narquivo gravado")
