# -*- coding: utf-8 -*-
"""Compacta os flutuantes que nao cabiam no espaco restante da pagina.

Com a quebra de paragrafo proibida, o flutuante que nao cabe migra inteiro
e deixa vazio atras de si. Reduzir o corpo e o espacamento entre linhas da
tabela devolve esse espaco sem comprometer a leitura. O ajuste e local,
pois aplicado a todas as tabelas o resultado piorou.
"""
import re
import sys

ARQ = sys.argv[1]
t = open(ARQ, encoding="utf-8").read()

ALVOS = ["quad:metricas_avaliacao", "tab:latencia_inferencia", "tab:ganho_gpu"]
AJUSTE = "\\small\n\\renewcommand{\\arraystretch}{1.1}\n"

for rotulo in ALVOS:
    m = re.search(r"\\label\{" + re.escape(rotulo) + r"\}", t)
    if not m:
        sys.exit("FALHOU, rotulo ausente %s" % rotulo)
    # ponto de insercao, logo apos a linha do rotulo
    fim = t.index("\n", m.end()) + 1
    trecho = t[m.start() - 400:fim]
    if "\\small" in trecho or "\\footnotesize" in trecho or "\\scriptsize" in trecho:
        print("   ja compacto, ignorado  %s" % rotulo)
        continue
    t = t[:fim] + AJUSTE + t[fim:]
    print("ok  compactado  %s" % rotulo)

# O ambiente board nao e solto ainda no Quadro 1, que e pagina inteira e
# permanece como esta, por ja empregar corpo reduzido.
open(ARQ, "w", encoding="utf-8").write(t)
print("\narquivo gravado")
