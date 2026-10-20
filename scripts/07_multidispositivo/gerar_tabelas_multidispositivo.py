"""Gera as tabelas da secao multidispositivo a partir do consolidado.

A coleta fecha no mesmo dia da entrega, de modo que um aparelho pode
chegar depois de o texto estar escrito. Para que isso custe um comando e
nao uma reescrita, as tabelas nao sao digitadas: saem daqui como arquivos
.tex que o artigo traz por \\input. Chegou aparelho novo, roda de novo e
recompila.

Tres tabelas:

  aparelhos.tex    o painel de aparelhos avaliados
  ganho_gpu.tex    razao entre CPU e GPU por aparelho, que e o achado
  inferencia.tex   inferencia media por configuracao e aparelho

Os nomes comerciais de aparelho e de SoC nao estao nos arquivos de lote,
que trazem apenas o codigo do modelo e o identificador do hardware. Vem
de um arquivo de apoio, editavel, e o que nao estiver mapeado sai com o
codigo mesmo e um aviso, em vez de ser inventado aqui.

Uso: python3 -I gerar_tabelas_multidispositivo.py <consolidado.csv>
                 <aparelhos.csv> <pasta de saida>
"""
import csv
import os
import sys

consolidado, mapa_csv, saida = sys.argv[1], sys.argv[2], sys.argv[3]

ORDEM_PRECISAO = {"FP32": 0, "FP16": 1, "INT8": 2}
CONFIGS = [(a, p, d)
           for a in ("YOLOv8n", "YOLOv10n")
           for p in ("FP32", "FP16", "INT8")
           for d in ("CPU", "GPU")]


def virgula(x, casas=1):
    if x is None or x == "":
        return "--"
    return ("%.*f" % (casas, float(x))).replace(".", ",")


def milhar(x):
    """Separador de milhar com ponto, como pede a norma."""
    if x is None or x == "":
        return "--"
    inteiro, _, resto = ("%.1f" % float(x)).partition(".")
    sinal = ""
    if inteiro.startswith("-"):
        sinal, inteiro = "-", inteiro[1:]
    grupos = []
    while len(inteiro) > 3:
        grupos.insert(0, inteiro[-3:])
        inteiro = inteiro[:-3]
    grupos.insert(0, inteiro)
    return "%s%s,%s" % (sinal, ".".join(grupos), resto)


# ------------------------------------------------------- nomes comerciais
nomes = {}
if os.path.exists(mapa_csv):
    for r in csv.DictReader(open(mapa_csv, encoding="utf-8")):
        nomes[r["aparelho"].strip()] = r

linhas = list(csv.DictReader(open(consolidado, encoding="utf-8")))

aparelhos = []
for r in linhas:
    chave = r["aparelho"]
    if chave not in [a["aparelho"] for a in aparelhos]:
        aparelhos.append(r)

faltando = [a["aparelho"] for a in aparelhos if a["aparelho"] not in nomes]
if faltando:
    print("aviso: sem nome comercial para %s" % ", ".join(faltando))
    print("       acrescente em %s para sair por extenso na tabela" % mapa_csv)


def nome_curto(cod):
    return nomes.get(cod, {}).get("curto", cod)


def nome_longo(cod):
    return nomes.get(cod, {}).get("comercial", cod)


def soc(registro):
    """Nome comercial do SoC; sem mapeamento, o identificador do hardware.

    O identificador (mt6768, s5e9945, qcom) e o que o Android informa. O
    nome comercial nao se deduz dele com seguranca, porque um mesmo
    identificador atende a varias linhas, de modo que vem do arquivo de
    apoio ou nao vem.
    """
    cod = registro["aparelho"]
    return nomes.get(cod, {}).get(
        "soc", registro.get("hardware") or registro.get("placa", "?"))


# Ordena os aparelhos pela inferencia do YOLOv8n FP32 CPU, do mais rapido
# ao mais lento, para que a tabela leia como uma escala de desempenho.
def referencia(cod):
    for r in linhas:
        if (r["aparelho"] == cod and r["arquitetura"] == "YOLOv8n"
                and r["precisao"] == "FP32" and r["delegate"] == "CPU"
                and r["inferencia_media_ms"]):
            return float(r["inferencia_media_ms"])
    return float("inf")


codigos = sorted({r["aparelho"] for r in linhas}, key=referencia)

dado = {(r["aparelho"], r["arquitetura"], r["precisao"], r["delegate"]): r
        for r in linhas}

os.makedirs(saida, exist_ok=True)


def gravar(nome, texto):
    caminho = os.path.join(saida, nome)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)
    print("gravado %s" % caminho)


# ------------------------------------------------------------ 1. aparelhos
linhas_tab = []
for cod in codigos:
    r = next(x for x in linhas if x["aparelho"] == cod)
    executadas = sum(1 for c in CONFIGS
                     if dado.get((cod,) + c, {}).get("imagens") not in
                     (None, "", "0"))
    linhas_tab.append("%s & %s & %s & %d \\\\" % (
        nome_longo(cod), soc(r), r["android"], executadas))

gravar("aparelhos.tex", """\\begin{table}[H]
\\centering
\\caption{Aparelhos empregados na avaliação multidispositivo}
\\label{tab:aparelhos}
\\begin{tabular}{llcc}
\\toprule
\\textbf{Aparelho} & \\textbf{\\ac{SoC}} & \\textbf{Android} &
\\textbf{Configurações} \\\\
\\midrule
%s
\\bottomrule
\\end{tabular}
\\legend{Elaborada pela autora (2026).}
\\end{table}
""" % "\n".join(linhas_tab))

# ------------------------------------------------------------ 2. ganho GPU
corpo = []
for a in ("YOLOv8n", "YOLOv10n"):
    for p in ("FP32", "FP16", "INT8"):
        celulas = []
        for cod in codigos:
            c = dado.get((cod, a, p, "CPU"), {}).get("inferencia_media_ms")
            g = dado.get((cod, a, p, "GPU"), {}).get("inferencia_media_ms")
            if c and g:
                celulas.append(virgula(float(c) / float(g), 2) + "$\\times$")
            else:
                celulas.append("--")
        corpo.append("%s %s & %s \\\\" % (a, p, " & ".join(celulas)))
    if a == "YOLOv8n":
        corpo.append("\\midrule")

gravar("ganho_gpu.tex", """\\begin{table}[H]
\\centering
\\caption{Razão entre a inferência em processador e em processador
gráfico, por aparelho}
\\label{tab:ganho_gpu_dispositivos}
\\begin{tabular}{l%s}
\\toprule
\\textbf{Configuração} & %s \\\\
\\midrule
%s
\\bottomrule
\\end{tabular}
\\legend{Elaborada pela autora (2026). Valores acima da unidade indicam
ganho do \\textit{delegate} de processador gráfico. O traço assinala
configuração que não executou.}
\\end{table}
""" % ("c" * len(codigos),
       " & ".join("\\textbf{%s}" % nome_curto(c) for c in codigos),
       "\n".join(corpo)))

# -------------------------------------------------------- 3. inferencia
corpo = []
for i, (a, p, d) in enumerate(CONFIGS):
    celulas = [milhar(dado.get((cod, a, p, d), {}).get("inferencia_media_ms"))
               for cod in codigos]
    corpo.append("%s %s & \\ac{%s} & %s \\\\" % (a, p, d, " & ".join(celulas)))
    if i == 5:
        corpo.append("\\midrule")

gravar("inferencia.tex", """\\begin{table}[H]
\\centering
\\caption{Latência média de inferência, em milissegundos, por
configuração e aparelho}
\\label{tab:inferencia_dispositivos}
\\begin{tabular}{ll%s}
\\toprule
\\textbf{Modelo} & \\textbf{\\textit{Delegate}} & %s \\\\
\\midrule
%s
\\bottomrule
\\end{tabular}
\\legend{Elaborada pela autora (2026).}
\\end{table}
""" % ("r" * len(codigos),
       " & ".join("\\textbf{%s}" % nome_curto(c) for c in codigos),
       "\n".join(corpo)))

print("\n%d aparelhos, na ordem: %s"
      % (len(codigos), ", ".join(nome_curto(c) for c in codigos)))
