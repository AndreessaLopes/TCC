# -*- coding: utf-8 -*-
"""Deixa a Fonte com a origem apenas e passa a explicacao para Nota.

A NBR 14724 e as normas de apresentacao tabular preveem, no rodape do
flutuante, a fonte e, abaixo dela, as notas. A classe iftex2024 define
somente \\legend, que imprime "Fonte: ...". O comando \\nota e declarado no
preambulo do artigo.tex, de modo que a classe permanece intacta.

Uso:
    python separar_fonte_nota.py <artigo.tex> [outros .tex ...]
"""
import re
import sys

ORIGEM = "Elaborada pela autora (2026)."
TOTAL = 0


def corpo_da_chave(t, i):
    """Devolve (conteudo, indice_apos_fecho) a partir do '{' em i-1."""
    nivel, j = 1, i
    while j < len(t) and nivel:
        if t[j] == "{":
            nivel += 1
        elif t[j] == "}":
            nivel -= 1
        j += 1
    return t[i:j - 1], j


def tratar(caminho):
    global TOTAL
    t = open(caminho, encoding="utf-8").read()
    saida, pos, mudou = [], 0, 0
    while True:
        m = re.compile(r"\\legend\{").search(t, pos)
        if not m:
            saida.append(t[pos:])
            break
        saida.append(t[pos:m.start()])
        conteudo, fim = corpo_da_chave(t, m.end())
        limpo = " ".join(conteudo.split())
        if limpo.startswith(ORIGEM) and len(limpo) > len(ORIGEM):
            resto = limpo[len(ORIGEM):].strip()
            saida.append("\\legend{%s}\n\\nota{%s}" % (ORIGEM, resto))
            mudou += 1
        else:
            saida.append(t[m.start():fim])
        pos = fim
    novo = "".join(saida)
    if mudou:
        open(caminho, "w", encoding="utf-8").write(novo)
    TOTAL += mudou
    print("%-34s %d legenda(s) separada(s)" % (caminho.split("/")[-1], mudou))


for arquivo in sys.argv[1:]:
    tratar(arquivo)
print("\ntotal: %d" % TOTAL)
