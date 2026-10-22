"""Duas figuras da coleta em multiplos dispositivos.

A primeira mostra a razao entre a execucao em processador e em
processador grafico, por aparelho e configuracao. A escala e logaritmica
porque o dado e uma razao, de modo que dobrar e reduzir a metade ficam a
mesma distancia da unidade, que e a leitura correta.

A segunda mostra o coeficiente de variacao da inferencia dentro de cada
execucao, por configuracao, com um ponto por aparelho. Responde a
afirmacao do trabalho sobre estabilidade com os sete aparelhos no lugar
de um.

As convencoes de cor sao as que o documento ja emprega. Azul e laranja
nomeiam os delegates, como na figura de latencia; cinza escuro e claro
nomeiam as arquiteturas, como na figura das curvas de precisao e
revocacao. Em ambas as figuras a forma do marcador repete a distincao,
para que a leitura sobreviva a impressao em tons de cinza.

Uso: python3 -I gerar_fig_multidispositivo.py <pasta multidispositivo>
                 <aparelhos.csv> <pasta de saida>
"""
import csv
import os
import re
import statistics as st
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

entrada, mapa_csv, saida = sys.argv[1], sys.argv[2], sys.argv[3]

COR_CPU, COR_GPU = "#1f77b4", "#ff7f0e"
COR_V8, COR_V10 = "#2b2b2b", "#8a8a8a"
TINTA, TINTA_FRACA, GRADE = "#333333", "#666666", "#ececec"

FORMA_PRECISAO = {"FP32": "o", "FP16": "s", "INT8": "^"}
ORDEM_PRECISAO = {"FP32": 0, "FP16": 1, "INT8": 2}

plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42})


def virgula(x, _=None, casas=1):
    return ("%.*f" % (casas, x)).replace(".", ",")


# ------------------------------------------------------------- leitura
def ler(caminho):
    cab, linhas, corpo = {}, [], False
    for linha in open(caminho, encoding="utf-8", errors="replace"):
        if linha.startswith("#"):
            m = re.match(r"# ([^:]+): (.+)", linha.strip())
            if m:
                cab[m.group(1)] = m.group(2).strip()
        elif linha.startswith("arquivo,"):
            corpo = True
        elif corpo and linha.strip():
            c = linha.strip().split(",")
            if len(c) >= 8 and c[7] != "1":
                linhas.append(float(c[3]))
    return cab, linhas


def sessao_de(raiz):
    rel = os.path.relpath(raiz, entrada)
    partes = [x for x in rel.split(os.sep) if x not in (".", "")]
    return partes[1] if len(partes) > 1 else "unica"


execucoes = []
for raiz, _, arquivos in os.walk(entrada):
    for nome in sorted(arquivos):
        if not nome.startswith("lote_") or not nome.endswith(".csv"):
            continue
        cab, v = ler(os.path.join(raiz, nome))
        if "Configuracao" not in cab or len(v) < 5:
            continue
        arq, prec, deleg = cab["Configuracao"].split(" · ")
        execucoes.append({
            "aparelho": cab["Aparelho"], "android": cab.get("Android", ""),
            "sessao": sessao_de(raiz), "arq": arq, "prec": prec,
            "deleg": deleg, "media": st.mean(v),
            "cv": st.pstdev(v) / st.mean(v) * 100,
        })

if not execucoes:
    sys.exit("Nenhuma execucao lida em %s" % entrada)

# Um aparelho medido em versoes diferentes do Android nao e uma repeticao
# de si mesmo; fica-se com o maior grupo, como no gerador de tabelas.
versoes = {}
for e in execucoes:
    versoes.setdefault(e["aparelho"], {}).setdefault(e["android"], set()).add(
        e["sessao"])
manter = {}
for ap, vs in versoes.items():
    maior = max(vs, key=lambda v: (len(vs[v]), v))
    manter[ap] = (maior, vs[maior])
execucoes = [e for e in execucoes
             if e["android"] == manter[e["aparelho"]][0]
             and e["sessao"] in manter[e["aparelho"]][1]]

nomes = {}
if os.path.exists(mapa_csv):
    for r in csv.DictReader(open(mapa_csv, encoding="utf-8")):
        nomes[r["aparelho"].strip()] = r.get("curto", r["aparelho"])

curto = lambda ap: nomes.get(ap, ap)


def media_de(ap, arq, prec, deleg, campo="media"):
    v = [e[campo] for e in execucoes if e["aparelho"] == ap
         and e["arq"] == arq and e["prec"] == prec and e["deleg"] == deleg]
    return st.mean(v) if v else None


aparelhos = sorted({e["aparelho"] for e in execucoes},
                   key=lambda a: media_de(a, "YOLOv8n", "FP32", "CPU") or 0,
                   reverse=True)


def moldura(ax):
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("bottom", "left"):
        ax.spines[lado].set_color("#aaaaaa")
        ax.spines[lado].set_linewidth(0.6)
    ax.tick_params(labelsize=7, colors=TINTA_FRACA, length=3)
    for r in ax.get_xticklabels() + ax.get_yticklabels():
        r.set_color("#444444")


# ------------------------------------------------- 1. razao entre delegates
fig, ax = plt.subplots(figsize=(5.9, 3.5))
ax.axvspan(0.4, 1.0, color="#f6f6f6", zorder=0)
ax.axvline(1.0, color="#999999", lw=0.9, ls="--", zorder=2)

for i, ap in enumerate(aparelhos):
    y = len(aparelhos) - 1 - i
    for arq, cor in (("YOLOv8n", COR_V8), ("YOLOv10n", COR_V10)):
        for prec in ("FP32", "FP16", "INT8"):
            c = media_de(ap, arq, prec, "CPU")
            g = media_de(ap, arq, prec, "GPU")
            if not c or not g:
                continue
            desloc = 0.17 if arq == "YOLOv8n" else -0.17
            ax.plot(c / g, y + desloc, FORMA_PRECISAO[prec], ms=5.2,
                    color=cor, mec="white", mew=0.8, zorder=4, ls="none")

ax.set_yticks(range(len(aparelhos)))
ax.set_yticklabels([curto(a) for a in reversed(aparelhos)], fontsize=7.5)
ax.set_xscale("log")
ax.set_xlim(0.45, 9)
ax.set_xticks([0.5, 1, 2, 4, 8])
ax.set_xticklabels(["0,5", "1", "2", "4", "8"])
ax.set_xlabel("Razão entre a inferência em processador e em processador "
              "gráfico", fontsize=8, color=TINTA)
ax.grid(axis="x", color=GRADE, lw=0.6)
ax.set_axisbelow(True)
ax.set_ylim(-0.75, len(aparelhos) - 0.15)
ax.text(0.68, len(aparelhos) - 0.25, "processador gráfico mais lento",
        fontsize=6.5, color=TINTA_FRACA, ha="center", va="top")
moldura(ax)

legenda = [
    Line2D([], [], color=COR_V8, marker="o", ls="none", ms=5,
           label="YOLOv8n"),
    Line2D([], [], color=COR_V10, marker="o", ls="none", ms=5,
           label="YOLOv10n"),
    Line2D([], [], color=TINTA_FRACA, marker="o", ls="none", ms=5,
           label="FP32"),
    Line2D([], [], color=TINTA_FRACA, marker="s", ls="none", ms=5,
           label="FP16"),
    Line2D([], [], color=TINTA_FRACA, marker="^", ls="none", ms=5,
           label="INT8"),
]
ax.legend(handles=legenda, frameon=False, fontsize=6.8, ncol=5,
          loc="lower center", bbox_to_anchor=(0.5, -0.33),
          handletextpad=0.3, columnspacing=1.1)
fig.tight_layout(pad=0.4)
destino = os.path.join(saida, "razao_delegates.pdf")
fig.savefig(destino, bbox_inches="tight", pad_inches=0.02)
print("gravado %s" % destino)
plt.close(fig)

# ------------------------------------------------- 2. dispersao por execucao
CONFIGS = [(a, p, d) for a in ("YOLOv8n", "YOLOv10n")
           for p in ("FP32", "FP16", "INT8") for d in ("CPU", "GPU")]
CONFIGS = [c for c in CONFIGS
           if any(e["arq"] == c[0] and e["prec"] == c[1] and e["deleg"] == c[2]
                  for e in execucoes)]

fig, ax = plt.subplots(figsize=(5.9, 3.8))
for i in range(0, len(CONFIGS), 2):
    ax.axhspan(len(CONFIGS) - 1 - i - 0.5, len(CONFIGS) - 1 - i + 0.5,
               color="#fafafa", zorder=0)
for i, (arq, prec, deleg) in enumerate(CONFIGS):
    y = len(CONFIGS) - 1 - i
    pares = [(ap, media_de(ap, arq, prec, deleg, "cv")) for ap in aparelhos]
    pares = [(ap, v) for ap, v in pares if v is not None]
    valores = [v for _, v in pares]
    cor = COR_CPU if deleg == "CPU" else COR_GPU
    forma = "o" if deleg == "CPU" else "D"
    # Sem deslocamento, aparelhos de valor proximo se escondem.
    for k, (ap, v) in enumerate(pares):
        desvio = (k - (len(pares) - 1) / 2) * 0.1
        ax.plot(v, y + desvio, forma, ms=4.2, color=cor, mec="white",
                mew=0.7, alpha=0.9, zorder=4, ls="none")
    if valores:
        ax.plot(st.median(valores), y, "|", ms=13, color=TINTA, mew=1.4,
                zorder=5)

ax.set_yticks(range(len(CONFIGS)))
ax.set_yticklabels(["%s %s %s" % (a, p, d)
                    for a, p, d in reversed(CONFIGS)], fontsize=7)
ax.set_xlabel("Coeficiente de variação da inferência dentro da execução (\\%)"
              .replace("\\", ""), fontsize=8, color=TINTA)
ax.grid(axis="x", color=GRADE, lw=0.6)
ax.set_axisbelow(True)
ax.set_xlim(left=0)
moldura(ax)
ax.legend(handles=[
    Line2D([], [], color=COR_CPU, marker="o", ls="none", ms=5, label="CPU"),
    Line2D([], [], color=COR_GPU, marker="D", ls="none", ms=5, label="GPU"),
    Line2D([], [], color=TINTA, marker="|", ls="none", ms=9, mew=1.4,
           label="mediana dos aparelhos"),
], frameon=False, fontsize=6.8, ncol=3, loc="lower center",
    bbox_to_anchor=(0.5, -0.27), handletextpad=0.3, columnspacing=1.2)
fig.tight_layout(pad=0.4)
destino = os.path.join(saida, "dispersao_execucao.pdf")
fig.savefig(destino, bbox_inches="tight", pad_inches=0.02)
print("gravado %s" % destino)
plt.close(fig)

# ------------------------------------------------- numeros para o texto
print("\naparelhos, do mais lento ao mais rapido: %s"
      % ", ".join(curto(a) for a in aparelhos))

print("\ncoeficiente de variacao por aparelho, mediana das configuracoes:")
for ap in aparelhos:
    c = [e["cv"] for e in execucoes
         if e["aparelho"] == ap and e["deleg"] == "CPU"]
    g = [e["cv"] for e in execucoes
         if e["aparelho"] == ap and e["deleg"] == "GPU"]
    if c and g:
        print("  %-10s CPU %5.1f%%   GPU %5.1f%%   %s"
              % (curto(ap), st.median(c), st.median(g),
                 "GPU mais disperso" if st.median(g) > st.median(c)
                 else "CPU mais disperso"))
cv_cpu = [e["cv"] for e in execucoes if e["deleg"] == "CPU"]
cv_gpu = [e["cv"] for e in execucoes if e["deleg"] == "GPU"]
print("coeficiente de variacao, mediana: CPU %.1f%%, GPU %.1f%%"
      % (st.median(cv_cpu), st.median(cv_gpu)))
print("coeficiente de variacao, maximo:  CPU %.1f%%, GPU %.1f%%"
      % (max(cv_cpu), max(cv_gpu)))
