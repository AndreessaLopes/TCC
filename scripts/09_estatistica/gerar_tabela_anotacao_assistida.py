# -*- coding: utf-8 -*-
"""Gera tabelas/anotacao_assistida.tex a partir de metricas_teste_limpo.csv.

Uso:
    python gerar_tabela_anotacao_assistida.py <csv> <saida_dir>
"""
import csv
import os
import sys

CSV, SAIDA = sys.argv[1], sys.argv[2]

d = {}
for r in csv.DictReader(open(CSV, encoding="utf-8")):
    d[(r["conjunto"], r["modelo"])] = {
        k: float(r[k]) for k in ("mAP50", "mAP50_95", "precisao", "revocacao")
    }

COLUNAS = ("mAP50", "mAP50_95", "precisao", "revocacao")


def num(v, sinal=False):
    texto = ("%+.4f" if sinal else "%.4f") % v
    texto = texto.replace(".", ",")
    if sinal:
        texto = "$" + texto[0] + "$" + texto[1:]
    return texto


linhas = []
for modelo in ("YOLOv8n", "YOLOv10n"):
    a = d[("completo", modelo)]
    b = d[("nao_afetado", modelo)]
    linhas.append("%s & 285 & %s \\\\" % (
        modelo, " & ".join(num(a[c]) for c in COLUNAS)))
    linhas.append(" & 194 & %s \\\\" % (
        " & ".join(num(b[c]) for c in COLUNAS)))
    linhas.append(" & Diferença & %s \\\\" % (
        " & ".join(num(b[c] - a[c], True) for c in COLUNAS)))
    if modelo == "YOLOv8n":
        linhas.append("\\midrule")

corpo = "\n".join(linhas)

texto = """\\begin{table}[H]
\\centering
\\small
\\caption{Indicadores de detecção no conjunto de teste completo e no
subconjunto não submetido a anotação assistida por modelo}
\\label{tab:anotacao_assistida}
\\begin{tabular}{llrrrr}
\\toprule
\\textbf{Modelo} & \\textbf{Imagens} & \\textbf{mAP@0,50} &
\\textbf{mAP@0,50:0,95} & \\textbf{Precisão} & \\textbf{Revocação} \\\\
\\midrule
%s
\\bottomrule
\\end{tabular}
\\legend{Elaborada pela autora (2026).}
\\nota{As 194 imagens correspondem à partição de teste após a retirada dos 91 arquivos cujas caixas foram propostas pelo modelo auxiliar. Ambas as medições empregaram os mesmos ajustes de avaliação, com entrada de 960~pixels e preenchimento até o quadrado. Valores obtidos com o avaliar\\_teste\\_limpo.py e registrados em resultados/csv/metricas\\_teste\\_limpo.csv.}
\\end{table}
""" % corpo

os.makedirs(SAIDA, exist_ok=True)
caminho = os.path.join(SAIDA, "anotacao_assistida.tex")
open(caminho, "w", encoding="utf-8").write(texto)
print("gravado %s" % caminho)
