"""Recalcula as colunas de delta do validacao_tflite.csv.

As colunas delta_map50 e delta_map50_95 foram calculadas contra os
valores de 0,650 e 0,644, obtidos sob o agrupamento retangular da
biblioteca. As variantes TFLite tem forma de entrada fixa e por isso sao
avaliadas com preenchimento quadrado, de modo que a comparacao misturava
dois preenchimentos e registrava como perda de conversao o que vinha do
preenchimento.

A referencia correta e a medicao em PyTorch sob o mesmo preenchimento,
gravada em resultados/csv/metricas_teste.csv. Sob ela, as variantes em
precisao plena coincidem com o modelo de origem.

Uso: python3 -I recalcular_deltas_tflite.py <metricas_teste.csv> <validacao_tflite.csv>
"""
import csv
import io
import sys

ref_csv, alvo_csv = sys.argv[1], sys.argv[2]

ref = {}
for r in csv.DictReader(io.open(ref_csv, encoding="utf-8")):
    ref[r["modelo"].lower()] = (float(r["map50"]), float(r["map50_95"]))

if set(ref) != {"yolov8n", "yolov10n"}:
    sys.exit("FALHOU: referencia inesperada em %s, encontrei %s"
             % (ref_csv, sorted(ref)))

linhas = list(csv.DictReader(io.open(alvo_csv, encoding="utf-8")))
if not linhas:
    sys.exit("FALHOU: %s vazio" % alvo_csv)
for c in ("delta_map50", "delta_map50_95"):
    if c not in linhas[0]:
        sys.exit("FALHOU: coluna %s ausente em %s" % (c, alvo_csv))

print("%-24s %10s %10s %10s %10s"
      % ("arquivo", "delta50", "era", "delta50_95", "era"))
for r in linhas:
    m = r["modelo"].lower()
    if m not in ref:
        sys.exit("FALHOU: modelo %r sem referencia" % r["modelo"])
    antes = (r["delta_map50"], r["delta_map50_95"])
    d50 = round(float(r["map50"]) - ref[m][0], 4)
    d95 = round(float(r["map50_95"]) - ref[m][1], 4)
    r["delta_map50"], r["delta_map50_95"] = "%.4f" % d50, "%.4f" % d95
    print("%-24s %10.4f %10s %10.4f %10s"
          % (r["arquivo"], d50, antes[0], d95, antes[1]))

with io.open(alvo_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
    w.writeheader()
    w.writerows(linhas)
print("\n%s regravado" % alvo_csv)
