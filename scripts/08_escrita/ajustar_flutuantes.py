# -*- coding: utf-8 -*-
"""Solta os flutuantes grandes que forcam quebra de pagina.

Com [H] o flutuante e fixado no ponto exato do texto. Quando nao cabe no
espaco restante, a pagina e encerrada ali e sobra um vazio. Trocando para
[htbp], o texto seguinte preenche a pagina e o flutuante vai para o topo
da proxima ou para pagina propria.
"""
import re
import sys

ARQ = sys.argv[1]
t = open(ARQ, encoding="utf-8").read()

# Flutuantes identificados como causadores de vazio superior a 20%.
ALVOS = [
    "fig:crescimento_temporal",
    "quad:survey",
    "quad:ambiente_computacional",
    "quad:config_treinamento",
    "tab:estatisticas_dataset",
    "tab:ganho_gpu",
    "tab:deteccoes_dispositivo",
    "fig:deriva_tercos",
    "fig:razao_delegates",
]

trocados = 0
for rotulo in ALVOS:
    m = re.search(r"\\label\{" + re.escape(rotulo) + r"\}", t)
    if not m:
        print("   aviso, rotulo ausente %s" % rotulo)
        continue
    ini = max(0, m.start() - 600)
    bloco = t[ini:m.start()]
    amb = None
    for a in ("figure", "table", "board"):
        p = bloco.rfind("\\begin{%s}[H]" % a)
        if p != -1 and (amb is None or p > amb[1]):
            amb = (a, p)
    if amb is None:
        print("   aviso, sem [H] antes de %s" % rotulo)
        continue
    pos = ini + amb[1]
    antigo = "\\begin{%s}[H]" % amb[0]
    t = t[:pos] + "\\begin{%s}[htbp]" % amb[0] + t[pos + len(antigo):]
    trocados += 1
    print("ok  %-30s %s" % (rotulo, amb[0]))

print("\n%d flutuantes soltos" % trocados)

# Espaco entre a legenda e o primeiro bloco do fluxograma da conversao.
antigo = ("\\caption{Fluxo de conversão e otimização dos modelos para "
          "TensorFlow Lite}\n\\label{fig:fluxo_tflite}\n"
          "\\resizebox{0.86\\textwidth}{!}{%")
novo = ("\\caption{Fluxo de conversão e otimização dos modelos para "
        "TensorFlow Lite}\n\\label{fig:fluxo_tflite}\n"
        "\\vspace{1.2\\baselineskip}\n"
        "\\resizebox{0.86\\textwidth}{!}{%")
if t.count(antigo) != 1:
    sys.exit("FALHOU no espaco da Figura do fluxo de conversao")
t = t.replace(antigo, novo)
print("ok  espaco acrescentado abaixo da legenda do fluxo de conversão")

open(ARQ, "w", encoding="utf-8").write(t)
print("\narquivo gravado")
