"""Figuras da caracterizacao bibliometrica, a partir dos exports da base.

Gera tres arquivos:

    crescimento_temporal.pdf   evolucao anual por tema
    topicos_busca.pdf          volume recuperado por tema
    termos_titulos.pdf         termos mais frequentes nos titulos

Substituem as versoes anteriores, cujos rotulos traziam valores
arredondados a mao sobre barras desenhadas com os valores reais, e que
exibiam a preposicao "with" entre os termos de conteudo.

A contagem de termos e por frequencia de documento: conta em quantos
titulos distintos o termo ocorre, nao o total de ocorrencias. Registros
repetidos entre os cinco conjuntos sao unificados por DOI e, na falta
dele, pelo titulo normalizado. Plurais regulares sao somados ao singular
quando este tambem ocorre. Descartam-se apenas palavras funcionais e
formulas de titulo sem conteudo tematico, listadas em VAZIAS: nenhum
termo e removido por ser esperado na expressao de busca.

Uso: python3 -I gerar_fig_bibliometria.py <pasta dos csv> <pasta de saida>
"""
import csv
import io
import os
import re
import sys
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

csv.field_size_limit(10 ** 7)
entrada, saida = sys.argv[1], sys.argv[2]

ANOS = [2021, 2022, 2023, 2024, 2025]

TEMAS = [
    ("quantizacao_inferencia.csv", "Quantização de modelos"),
    ("yolo_mobile_edge.csv", "YOLO em dispositivos móveis"),
    ("vc_agricultura_detection.csv", "Visão computacional agrícola"),
    ("inferencia_tflite.csv", "TensorFlow Lite"),
    ("yolo_cafeicultura.csv", "Cafeicultura e YOLO"),
]

SERIES = [
    ("yolo_mobile_edge.csv", "YOLO em dispositivos móveis", "#2b2b2b", "-", "o"),
    ("inferencia_tflite.csv", "TensorFlow Lite", "#6e6e6e", "--", "s"),
    ("yolo_cafeicultura.csv", "Cafeicultura e YOLO", "#9e9e9e", ":", "^"),
]

VAZIAS = {
    "a", "an", "the", "and", "or", "of", "for", "in", "on", "to", "with",
    "by", "from", "at", "as", "is", "are", "its", "their", "this", "that",
    "these", "those", "into", "under", "over", "between", "through",
    "via", "using", "use", "used", "based", "toward", "towards", "it",
    "be", "can", "new", "study", "approach", "method", "methods", "model",
    "models", "research", "paper", "analysis", "application",
    "applications", "system", "systems", "we", "our", "no", "not",
}

plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42})


def milhar(n):
    return "{:,}".format(n).replace(",", ".")


def registros(nome):
    with io.open(os.path.join(entrada, nome), encoding="utf-8-sig",
                 newline="") as f:
        return list(csv.DictReader(f))


def por_ano(linhas):
    c = Counter()
    for linha in linhas:
        v = (linha.get("Year") or "").strip()[:4]
        if v.isdigit():
            c[int(v)] += 1
    return c


def eixo_milhar(x, _):
    return milhar(int(x))


def moldura(ax):
    ax.grid(color="#ececec", lw=0.6)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("bottom", "left"):
        ax.spines[lado].set_color("#aaaaaa")
        ax.spines[lado].set_linewidth(0.6)
    ax.tick_params(labelsize=7, colors="#666666", length=3)
    for rotulo in ax.get_xticklabels() + ax.get_yticklabels():
        rotulo.set_color("#444444")


# ----------------------------------------------------------- Figura 2
fig, ax = plt.subplots(figsize=(5.85, 3.0))
for nome, rotulo, cor, traco, marca in SERIES:
    c = por_ano(registros(nome))
    y = [c.get(a, 0) for a in ANOS]
    ax.plot(ANOS, y, color=cor, ls=traco, marker=marca, ms=3.5, lw=1.5,
            clip_on=False, zorder=3)
    ax.annotate(" %s (%s)" % (rotulo, milhar(y[-1])),
                xy=(ANOS[-1], y[-1]), xytext=(4, 0),
                textcoords="offset points", fontsize=6.5, color=cor,
                va="center", ha="left")
ax.set_xticks(ANOS)
ax.set_xlabel("Ano de publicação", fontsize=7.5, color="#333333")
ax.set_ylabel("Registros recuperados", fontsize=7.5, color="#333333")
ax.set_xlim(2021, 2025)
ax.set_ylim(0, 780)
moldura(ax)
fig.subplots_adjust(right=0.62)
fig.savefig(os.path.join(saida, "crescimento_temporal.pdf"),
            bbox_inches="tight", pad_inches=0.02)
plt.close(fig)
print("gravado crescimento_temporal.pdf")

# ----------------------------------------------------------- Figura 3
dados = [(rotulo, len(registros(nome))) for nome, rotulo in TEMAS]
fig, ax = plt.subplots(figsize=(5.85, 2.5))
pos = range(len(dados))
for i, (rotulo, n) in enumerate(dados):
    ax.barh(i, n, color="#555555", edgecolor="white", lw=0.6, height=0.68)
    ax.text(n + 18, i, milhar(n), va="center", ha="left", fontsize=7,
            color="#333333")
ax.set_yticks(list(pos))
ax.set_yticklabels([r for r, _ in dados], fontsize=7.5)
ax.invert_yaxis()
ax.set_xlabel("Registros recuperados", fontsize=7.5, color="#333333")
ax.set_xlim(0, max(n for _, n in dados) * 1.14)
moldura(ax)
ax.xaxis.set_major_formatter(eixo_milhar)
ax.grid(axis="y", visible=False)
fig.savefig(os.path.join(saida, "topicos_busca.pdf"),
            bbox_inches="tight", pad_inches=0.02)
plt.close(fig)
print("gravado topicos_busca.pdf")

# ----------------------------------------------------------- Figura 4
vistos, titulos = set(), []
for nome, _ in TEMAS:
    for linha in registros(nome):
        titulo = (linha.get("Title") or "").strip()
        if not titulo:
            continue
        doi = (linha.get("DOI") or "").strip().lower()
        chave = doi or re.sub(r"[^a-z0-9]+", "", titulo.lower())
        if chave not in vistos:
            vistos.add(chave)
            titulos.append(titulo)

bruto = Counter()
for titulo in titulos:
    termos = re.findall(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", titulo.lower())
    bruto.update({t for t in termos if len(t) > 2 and t not in VAZIAS})

# Soma plurais regulares ao singular, quando o singular tambem ocorre.
contagem = Counter()
for termo, n in bruto.items():
    if termo.endswith("s") and termo[:-1] in bruto:
        continue
    plural = termo + "s"
    contagem[termo] = n + (bruto[plural] if plural in bruto else 0)

topo = contagem.most_common(15)[::-1]
fig, ax = plt.subplots(figsize=(5.85, 2.95))
for i, (termo, n) in enumerate(topo):
    ax.barh(i, n, color="#555555", edgecolor="white", lw=0.6, height=0.7)
    ax.text(n + 12, i, milhar(n), va="center", ha="left", fontsize=7,
            color="#333333")
ax.set_yticks(range(len(topo)))
ax.set_yticklabels([t for t, _ in topo], fontsize=7.5, style="italic")
ax.set_xlabel("Títulos em que o termo ocorre (de %s)" % milhar(len(titulos)),
              fontsize=7.5, color="#333333")
ax.set_xlim(0, topo[-1][1] * 1.12)
moldura(ax)
ax.xaxis.set_major_formatter(eixo_milhar)
ax.grid(axis="y", visible=False)
fig.savefig(os.path.join(saida, "termos_titulos.pdf"),
            bbox_inches="tight", pad_inches=0.02)
plt.close(fig)
print("gravado termos_titulos.pdf  (%d registros unicos)" % len(titulos))
