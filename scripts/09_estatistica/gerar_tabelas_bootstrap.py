"""Monta as tabelas de incerteza a partir das saidas do bootstrap.

Uso: python3 -I gerar_tabelas_bootstrap.py <intervalos.csv> <razoes.csv> <saida>
"""
import csv
import io
import os
import sys

inter, razoes, saida = sys.argv[1], sys.argv[2], sys.argv[3]


def virgula(x, casas=2):
    return ("%.*f" % (casas, float(x))).replace(".", ",")


def parte(cfg):
    """'YOLOv8n · FP16 · GPU' -> ('YOLOv8n', 'FP16', 'GPU')"""
    p = [x.strip() for x in cfg.replace("·", "|").split("|")]
    return (p + ["", "", ""])[:3]


def gravar(nome, conteudo):
    caminho = os.path.join(saida, nome)
    io.open(caminho, "w", encoding="utf-8").write(conteudo)
    print("gravado %s" % caminho)


# ------------------------------------------------------- intervalos
linhas = list(csv.DictReader(io.open(inter, encoding="utf-8")))
ordem = {"YOLOv8n": 0, "YOLOv10n": 1}
prec = {"FP32": 0, "FP16": 1, "INT8": 2}
linhas.sort(key=lambda r: (ordem.get(parte(r["configuracao"])[0], 9),
                           prec.get(parte(r["configuracao"])[1], 9),
                           parte(r["configuracao"])[2]))
corpo = []
anterior = None
for r in linhas:
    m, p, d = parte(r["configuracao"])
    if anterior is not None and m != anterior:
        corpo.append("\\midrule")
    anterior = m
    corpo.append("%s %s & \\ac{%s} & %s & %s & [%s; %s] \\\\"
                 % (m, p, d, r["n"], virgula(r["media_ms"], 1),
                    virgula(r["ic_inferior_ms"], 1),
                    virgula(r["ic_superior_ms"], 1)))

gravar("intervalos.tex", """\\begin{table}[H]
\\centering
\\small
\\caption{Latência média de inferência e intervalo de confiança da média,
em milissegundos}
\\label{tab:intervalos}
\\begin{tabular}{llrrc}
\\toprule
\\textbf{Modelo} & \\textbf{\\textit{Delegate}} & \\textbf{Imagens} &
\\textbf{Média} & \\textbf{\\ac{IC}~95\\%%} \\\\
\\midrule
%s
\\bottomrule
\\end{tabular}
\\legend{Elaborada pela autora (2026). O intervalo decorre de reamostragem
com reposição sobre as imagens, com 10.000 reamostras e percentis 2,5 e
97,5, conforme \\texttt{scripts/09\\_estatistica/intervalos\\_bootstrap.py}.}
\\end{table}
""" % "\n".join(corpo))

# ------------------------------------------------------- razoes
linhas = list(csv.DictReader(io.open(razoes, encoding="utf-8")))
linhas.sort(key=lambda r: (ordem.get(parte(r["configuracao"])[0], 9),
                           prec.get(parte(r["configuracao"])[1], 9)))
corpo = []
anterior = None
for r in linhas:
    m, p, _ = parte(r["configuracao"])
    if anterior is not None and m != anterior:
        corpo.append("\\midrule")
    anterior = m
    ph = float(r["p_holm"])
    texto_p = "$<$~0,001" if ph < 0.001 else virgula(ph, 3)
    corpo.append("%s %s & %s$\\times$ & [%s; %s] & %s \\\\"
                 % (m, p, virgula(r["razao_cpu_gpu"]),
                    virgula(r["ic_inferior"]), virgula(r["ic_superior"]),
                    texto_p))

gravar("razoes_ic.tex", """\\begin{table}[H]
\\centering
\\small
\\caption{Razão entre a latência de inferência em processador e em
processador gráfico, com intervalo de confiança e significância}
\\label{tab:razoes_ic}
\\begin{tabular}{lccc}
\\toprule
\\textbf{Modelo} & \\textbf{Razão} & \\textbf{\\ac{IC}~95\\%%} &
\\textbf{$p$ ajustado} \\\\
\\midrule
%s
\\bottomrule
\\end{tabular}
\\legend{Elaborada pela autora (2026). Valores acima da unidade indicam ganho
do \\textit{delegate} de processador gráfico. O intervalo decorre de
reamostragem conjunta das duas execuções e o valor de $p$, de teste de
permutação bilateral sobre a diferença das médias, com 10.000 permutações e
correção de Holm para as cinco comparações.}
\\end{table}
""" % "\n".join(corpo))
