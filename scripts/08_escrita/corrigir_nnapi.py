# -*- coding: utf-8 -*-
"""Corrige a inferencia invalida sobre a depreciacao da NNAPI.

A depreciacao no Android 15 retira a interface do rol recomendado, mas nao
a remove dos aparelhos. A restricao aos delegates de CPU e GPU decorre de
decisao de escopo, nao de indisponibilidade.
"""
import re
import sys

ARQ = sys.argv[1]
t = open(ARQ, encoding="utf-8").read()


def trocar(rotulo, antigo, novo):
    global t
    padrao = r"\s+".join(re.escape(p) for p in antigo.split())
    n = len(re.findall(padrao, t))
    if n != 1:
        sys.exit("FALHOU em %s: %d ocorrencias" % (rotulo, n))
    t = re.sub(padrao, lambda _: novo, t, count=1)
    print("ok  %s" % rotulo)


trocar(
    "fundamentacao",
    "Registre-se que a \\ac{NNAPI} foi depreciada a partir do Android~15, "
    "deixando de receber novos recursos e sendo desencorajada para novas "
    "aplicações; como o dispositivo utilizado neste trabalho executa "
    "Android~16, a avaliação experimental restringiu-se aos "
    "\\textit{delegates} de \\ac{CPU} e \\ac{GPU}.",

    "Registre-se que a \\ac{NNAPI} foi depreciada no Android~15, deixando de "
    "receber novos recursos e sendo desencorajada para novas aplicações, "
    "ainda que permaneça disponível nos aparelhos. A documentação do próprio "
    "fornecedor recomenda a migração para o \\ac{TFLite} com "
    "\\textit{delegate} de \\ac{CPU} ou de \\ac{GPU} \\cite{Android2026NNAPI}, "
    "e é a esses dois que a avaliação experimental deste trabalho se "
    "restringe, por decisão de escopo.",
)

trocar(
    "limitacoes",
    "foi depreciada a partir do Android~15, e a própria documentação recomenda "
    "a migração para o \\ac{TFLite} \\cite{Android2026NNAPI}. Como o "
    "dispositivo utilizado executa Android~16, a avaliação restringiu-se aos "
    "\\textit{delegates} de \\ac{CPU} e \\ac{GPU}.",

    "foi depreciada no Android~15, e a própria documentação recomenda a "
    "migração para o \\ac{TFLite} \\cite{Android2026NNAPI}. A depreciação não "
    "retira a interface dos aparelhos, de modo que a restrição aos "
    "\\textit{delegates} de \\ac{CPU} e \\ac{GPU} decorre de decisão de "
    "escopo, alinhada à recomendação do fornecedor, e não de "
    "indisponibilidade.",
)

trocar(
    "trabalhos futuros",
    "caminho que a depreciação da \\ac{NNAPI} tornou o único disponível para "
    "esse tipo de acelerador.",
    "caminho que a depreciação da \\ac{NNAPI} tornou o recomendado para esse "
    "tipo de acelerador.",
)

open(ARQ, "w", encoding="utf-8").write(t)
print("\narquivo gravado")
