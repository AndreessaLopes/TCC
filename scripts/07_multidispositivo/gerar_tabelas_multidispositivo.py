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
  sessoes.tex      variacao entre sessoes repetidas do mesmo aparelho

Um aparelho pode ter sido medido mais de uma vez. Onde houver repeticao,
as tabelas trazem a media entre as sessoes, e a tabela de sessoes mostra
a dispersao entre elas, que e o que permite dizer se a diferenca entre
duas configuracoes supera a variacao de uma mesma configuracao medida
novamente.

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
    v = [float(r["inferencia_media_ms"]) for r in linhas
         if r["aparelho"] == cod and r["arquitetura"] == "YOLOv8n"
         and r["precisao"] == "FP32" and r["delegate"] == "CPU"
         and r["inferencia_media_ms"]]
    return sum(v) / len(v) if v else float("inf")


codigos = sorted({r["aparelho"] for r in linhas}, key=referencia)

# Sessoes do mesmo aparelho so sao repeticoes entre si quando rodaram
# sobre a mesma versao do sistema. O S24 foi atualizado de Android 16
# para 17 entre a linha de base e as repeticoes, e juntar as duas faria
# passar por variacao entre sessoes o que e diferenca de sistema.
por_versao = {}
for r in linhas:
    por_versao.setdefault(r["aparelho"], {}).setdefault(
        r.get("android", ""), set()).add(r.get("sessao", "unica"))

sessoes_de, descartadas = {}, {}
for cod, versoes in por_versao.items():
    maior = max(versoes, key=lambda v: (len(versoes[v]), v))
    sessoes_de[cod] = versoes[maior]
    fora = {s for v, ss in versoes.items() if v != maior for s in ss}
    if fora:
        descartadas[cod] = (maior, sorted(fora))

for cod, (maior, fora) in sorted(descartadas.items()):
    print("aviso: %s tem sessoes em versoes diferentes do Android; as "
          "tabelas usam as de Android %s e deixam de fora %s"
          % (cod, maior, ", ".join(fora)))


def deste_aparelho(r):
    """Verdadeiro para a linha que pertence ao grupo de sessoes em uso."""
    return r.get("sessao", "unica") in sessoes_de.get(r["aparelho"], set())


linhas = [r for r in linhas if deste_aparelho(r)]


# Uma chave pode ter mais de uma linha, uma por sessao.
dado = {}
for r in linhas:
    dado.setdefault(
        (r["aparelho"], r["arquitetura"], r["precisao"], r["delegate"]),
        []).append(r)


def valores(cod, a, p, d, campo="inferencia_media_ms"):
    return [float(x[campo]) for x in dado.get((cod, a, p, d), [])
            if x.get(campo)]


def media(cod, a, p, d, campo="inferencia_media_ms"):
    v = valores(cod, a, p, d, campo)
    return sum(v) / len(v) if v else None

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
                     if any(x.get("imagens") not in (None, "", "0")
                            for x in dado.get((cod,) + c, [])))
    linhas_tab.append("%s & %s & %s & %d & %d \\\\" % (
        nome_longo(cod), soc(r), r["android"], executadas,
        len(sessoes_de[cod])))

gravar("aparelhos.tex", """\\begin{table}[H]
\\centering
\\caption{Aparelhos empregados na avaliação multidispositivo}
\\label{tab:aparelhos}
\\begin{tabular}{llccc}
\\toprule
\\textbf{Aparelho} & \\textbf{\\ac{SoC}} & \\textbf{Android} &
\\textbf{Configurações} & \\textbf{Sessões} \\\\
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
            c, g = media(cod, a, p, "CPU"), media(cod, a, p, "GPU")
            if c and g:
                celulas.append(virgula(c / g, 2) + "$\\times$")
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
    celulas = [milhar(media(cod, a, p, d)) for cod in codigos]
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

# ------------------------------------------------------------ 4. sessoes
# So faz sentido onde houve repeticao. A dispersao entre sessoes e a
# medida com que se compara qualquer diferenca entre configuracoes.
repetidos = [c for c in codigos if len(sessoes_de[c]) > 1]
if repetidos:
    corpo = []
    for i, (a, p, d) in enumerate(CONFIGS):
        celulas = []
        for cod in repetidos:
            v = valores(cod, a, p, d)
            if len(v) > 1:
                m = sum(v) / len(v)
                amplitude = max(v) - min(v)
                celulas.append("%s & %s & %s" % (
                    milhar(m), milhar(amplitude),
                    virgula(100 * amplitude / m, 1)))
            else:
                celulas.append("-- & -- & --")
        if any("--" not in c for c in celulas):
            corpo.append("%s %s & \\ac{%s} & %s \\\\"
                         % (a, p, d, " & ".join(celulas)))
        if i == 5 and corpo:
            corpo.append("\\midrule")
    cabecalho = " & ".join(
        "\\multicolumn{3}{c}{\\textbf{%s}}" % nome_curto(c) for c in repetidos)
    sub = " & ".join(["\\textbf{Média} & \\textbf{Amplitude} & \\textbf{\\%}"]
                     * len(repetidos))
    gravar("sessoes.tex", """\\begin{table}[H]
\\centering
\\caption{Variação da latência de inferência entre sessões repetidas do
mesmo aparelho, em milissegundos}
\\label{tab:sessoes}
\\begin{tabular}{ll%s}
\\toprule
\\textbf{Modelo} & \\textbf{\\textit{Delegate}} & %s \\\\
 & & %s \\\\
\\midrule
%s
\\bottomrule
\\end{tabular}
\\legend{Elaborada pela autora (2026). %s A amplitude é a diferença
entre a maior e a menor média obtidas para a mesma configuração em
sessões distintas, e a última coluna exprime essa amplitude como
percentual da média.}
\\end{table}
""" % ("rrr" * len(repetidos), cabecalho, sub, "\n".join(corpo),
       " ".join("Em %s, %d sessões sobre Android %s."
                % (nome_curto(c), len(sessoes_de[c]),
                   next(r["android"] for r in linhas if r["aparelho"] == c))
                for c in repetidos)))
else:
    print("sem repeticao de sessao; sessoes.tex nao foi gerado")
