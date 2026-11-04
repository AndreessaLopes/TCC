"""Monta a tabela de revocacao por faixa de tamanho.

Uso: python3 -I gerar_tabela_tamanho.py <deteccoes_por_tamanho.csv> <saida.tex>
"""
import csv
import io
import sys

origem, destino = sys.argv[1], sys.argv[2]
linhas = [r for r in csv.DictReader(io.open(origem, encoding="utf-8"))
          if r["precisao_numerica"] == "PyTorch"]
if not linhas:
    sys.exit("FALHOU: nenhuma linha em PyTorch")

ROTULO = {"pequena": "Pequena ($<32^2$)",
          "media": "Média ($32^2$ a $96^2$)",
          "grande": "Grande ($>96^2$)"}
ORDEM = ["pequena", "media", "grande"]


def milhar(n):
    """Separador de milhar com ponto, como no restante do trabalho."""
    return "{:,}".format(int(n)).replace(",", ".")

corpo, anterior = [], None
for modelo in ("YOLOv8n", "YOLOv10n"):
    if anterior is not None:
        corpo.append("\\midrule")
    anterior = modelo
    for f in ORDEM:
        r = next(x for x in linhas
                 if x["modelo"] == modelo and x["faixa"] == f)
        corpo.append("%s & %s & %s & %s & %s \\\\" % (
            modelo, ROTULO[f], milhar(r["anotadas"]), milhar(r["encontradas"]),
            ("%.3f" % float(r["revocacao"])).replace(".", ",")))

io.open(destino, "w", encoding="utf-8").write("""\\begin{table}[H]
\\centering
\\small
\\caption{Revocação por faixa de tamanho da instância anotada}
\\label{tab:tamanho}
\\begin{tabular}{llrrr}
\\toprule
\\textbf{Modelo} & \\textbf{Faixa} & \\textbf{Anotadas} &
\\textbf{Encontradas} & \\textbf{Revocação} \\\\
\\midrule
%s
\\bottomrule
\\end{tabular}
\\legend{Elaborada pela autora (2026).}
\\nota{A faixa decorre da área que a caixa anotada ocupa na entrada de 960~pixels, com os limites convencionais de 32 e 96~pixels de lado. A instância é considerada encontrada quando alguma detecção com confiança igual ou superior a 0,25 alcança interseção sobre união de 0,50 com ela.}
\\end{table}
""" % "\n".join(corpo))
print("gravado %s" % destino)
