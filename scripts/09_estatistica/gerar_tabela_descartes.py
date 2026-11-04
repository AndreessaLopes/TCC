# -*- coding: utf-8 -*-
"""Gera tabelas/descartes.tex, sensibilidade da latencia de inferencia ao
descarte de medicoes.

Convencoes identicas as da tabela publicada: desvio populacional no
coeficiente de variacao e p95 por interpolacao linear.

Uso:
    python gerar_tabela_descartes.py <dir_medicoes> <saida_dir>
"""
import csv
import math
import os
import statistics as st
import sys

MEDICOES, SAIDA = sys.argv[1], sys.argv[2]

ALVOS = [
    ("YOLOv8n \\ac{FP32} \\ac{GPU}", "YOLOv8n_FP32_GPU"),
    ("YOLOv8n \\ac{INT8} \\ac{GPU}", "YOLOv8n_INT8_GPU"),
]


def carregar(marca):
    for arquivo in sorted(os.listdir(MEDICOES)):
        if marca in arquivo and arquivo.endswith(".csv"):
            caminho = os.path.join(MEDICOES, arquivo)
            linhas = [x for x in open(caminho, encoding="utf-8",
                                      errors="replace")
                      if not x.startswith("#") and x.strip()]
            return list(csv.DictReader(linhas))
    sys.exit("nao encontrei medicoes para %s" % marca)


def p95(v):
    pos = (len(v) - 1) * 0.95
    lo, hi = math.floor(pos), math.ceil(pos)
    return v[lo] + (v[hi] - v[lo]) * (pos - lo)


def resumo(valores):
    v = sorted(valores)
    media = st.mean(v)
    return len(v), media, p95(v), 100 * st.pstdev(v) / media


def vg(x):
    return ("%.1f" % x).replace(".", ",")


def milhar(x):
    inteiro, decimal = ("%.2f" % x).split(".")
    partes = []
    while len(inteiro) > 3:
        partes.insert(0, inteiro[-3:])
        inteiro = inteiro[:-3]
    partes.insert(0, inteiro)
    return ".".join(partes) + "," + decimal


linhas = []
brutos = []
for rotulo, marca in ALVOS:
    registros = carregar(marca)
    mantidas = [r for r in registros
                if r.get("descartada", "0").strip() in ("0", "")]
    fora = [r for r in registros
            if r.get("descartada", "0").strip() not in ("0", "")]
    for r in fora:
        brutos.append("%s & %s & %s & %s \\\\"
                      % (rotulo, r["arquivo"].replace("_", "\\_"),
                         milhar(float(r["inferencia_ms"])),
                         milhar(float(r["total_ms"]))))

    a = resumo(float(r["inferencia_ms"]) for r in mantidas)
    b = resumo(float(r["inferencia_ms"]) for r in registros)
    linhas.append("%s & Com descarte & %d & %s & %s & %s \\\\"
                  % (rotulo, a[0], vg(a[1]), vg(a[2]), vg(a[3])))
    linhas.append(" & Sem descarte & %d & %s & %s & %s \\\\"
                  % (b[0], vg(b[1]), vg(b[2]), vg(b[3])))
    if marca.endswith("FP32_GPU"):
        linhas.append("\\midrule")

texto = """\\begin{table}[H]
\\centering
\\small
\\caption{Efeito do descarte de medições sobre a latência de inferência
das configurações afetadas}
\\label{tab:descartes}
\\begin{tabular}{llrrrr}
\\toprule
\\textbf{Configuração} & \\textbf{Medições} & \\textbf{n} &
\\textbf{Média} & \\textbf{p95} & \\textbf{CV} \\\\
 &  &  & (ms) & (ms) & (\\%%) \\\\
\\midrule
%s
\\bottomrule
\\end{tabular}
\\legend{Elaborada pela autora (2026). A linha com descarte reproduz a
Tabela~\\ref{tab:latencia_inferencia} e a linha sem descarte incorpora as
medições excluídas pelo critério, relacionadas na
Tabela~\\ref{tab:descartes_brutos}. O coeficiente de variação emprega desvio
populacional e o p95 emprega interpolação linear, nas mesmas convenções
daquela tabela.}
\\end{table}
""" % "\n".join(linhas)

texto += """
\\begin{table}[H]
\\centering
\\small
\\caption{Medições excluídas pelo critério de descarte}
\\label{tab:descartes_brutos}
\\begin{tabular}{llrr}
\\toprule
\\textbf{Configuração} & \\textbf{Imagem} & \\textbf{Inferência} &
\\textbf{Total} \\\\
 &  & (ms) & (ms) \\\\
\\midrule
%s
\\bottomrule
\\end{tabular}
\\legend{Elaborada pela autora (2026). A latência de inferência situa-se na
faixa da respectiva execução, ao passo que a latência total alcança cerca do
dobro da média, o que localiza a anomalia na preparação da imagem.}
\\end{table}
""" % "\n".join(brutos)

os.makedirs(SAIDA, exist_ok=True)
caminho = os.path.join(SAIDA, "descartes.tex")
open(caminho, "w", encoding="utf-8").write(texto)
print("gravado %s" % caminho)
