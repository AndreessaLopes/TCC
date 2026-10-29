"""Incorpora ao texto a estimativa de incerteza das latencias.

A revisao aponta que o trabalho compara configuracoes sem teste e sem
intervalo. Como cada execucao registra a latencia de cada imagem, ambos
saem dos dados ja coletados. Entra uma subsecao com o intervalo de
confianca de cada media e com a comparacao entre delegates por teste de
permutacao, corrigido por Holm.

A analise corrige uma afirmacao. A latencia do YOLOv10n em FP16 com
delegate GPU era descrita como equivalente a obtida em CPU; a razao e de
0,95 com intervalo de 0,92 a 0,98, que nao contem a unidade, de modo que
a execucao em GPU e 5% mais lenta e a diferenca e distinguivel.

Uso: python3 -I inserir_estatistica.py <artigo.tex>
"""
import io
import re
import sys

caminho = sys.argv[1]
t = io.open(caminho, encoding="utf-8").read()
feito = []


def trocar(rotulo, antigo, novo):
    global t
    padrao = r"\s+".join(re.escape(p) for p in antigo.split())
    n = len(re.findall(padrao, t))
    if n != 1:
        sys.exit("FALHOU em %s: %d ocorrencias\n  %r" % (rotulo, n, antigo[:90]))
    t = re.sub(padrao, lambda _: novo, t, count=1)
    feito.append(rotulo)


# ------------------------------------------------------- sigla
trocar(
    "sigla do intervalo de confianca",
    "\\acro{GPU}[GPU]{\\textit{Graphics Processing Unit}}",
    "\\acro{GPU}[GPU]{\\textit{Graphics Processing Unit}}\n"
    "    \\acro{IC}[IC]{Intervalo de Confiança}",
)

# ------------------------------------------------------- subsecao nova
NOVA = """\\subsubsection{Precisão das estimativas e comparação entre
\\textit{delegates}}
\\label{sec:incerteza}

As médias da Tabela~\\ref{tab:latencia_inferencia} são estimativas obtidas
sobre um número finito de imagens, e a Tabela~\\ref{tab:intervalos} apresenta o
intervalo de confiança de cada uma, obtido por reamostragem com reposição
sobre as imagens medidas. A largura dos intervalos situa-se entre 2,5\\% e
6,5\\% da respectiva média.

\\input{tabelas/intervalos.tex}

A comparação entre \\textit{delegates} consta da
Tabela~\\ref{tab:razoes_ic}, que reúne a razão entre as médias, o intervalo de
confiança dessa razão e o valor de $p$ de teste de permutação bilateral,
corrigido por Holm para as cinco comparações possíveis. As cinco diferenças
são significativas ao nível de 5\\%, e nenhum dos intervalos contém a unidade.

\\input{tabelas/razoes_ic.tex}

O ganho do \\textit{delegate} \\ac{GPU} no YOLOv8n situa-se entre 3,48 e 4,90
conforme a precisão, de modo que a ordem de grandeza do efeito não depende da
incerteza das estimativas. No YOLOv10n o mesmo \\textit{delegate} produz
perda, de 32\\% em \\ac{FP32} e de 5\\% em \\ac{FP16}. A perda em \\ac{FP16},
embora pequena, é distinguível da igualdade, uma vez que o intervalo da razão,
de 0,92 a 0,98, não contém a unidade.

"""

ANCORA = "\\subsubsection{Incompatibilidade do YOLOv10n com o \\textit{delegate} GPU}"
if t.count(ANCORA) != 1:
    sys.exit("FALHOU: %d ocorrencias da ancora" % t.count(ANCORA))
if "sec:incerteza" in t:
    sys.exit("FALHOU: a subsecao ja existe")
t = t.replace(ANCORA, NOVA + ANCORA)
feito.append("subsecao de incerteza")

# ------------------------------------------------------- afirmacao corrigida
trocar(
    "sintese, FP16 deixa de ser equivalente",
    "em \\ac{FP32} a latência aumenta em 47\\% e em \\ac{FP16} permanece "
    "equivalente à obtida em \\ac{CPU}.",
    """em \\ac{FP32} a latência aumenta em 47\\% e em \\ac{FP16} supera em
5\\% a obtida em \\ac{CPU}, com intervalo de confiança que exclui a igualdade,
conforme a Subseção~\\ref{sec:incerteza}.""",
)

trocar(
    "conclusao, FP16 deixa de ser equivalente",
    "em \\ac{FP32} a latência aumentou em 47\\%, em \\ac{FP16} permaneceu "
    "equivalente à obtida em \\ac{CPU} e na precisão \\ac{INT8} a execução não "
    "é possível.",
    """em \\ac{FP32} a latência aumentou em 47\\%, em \\ac{FP16} superou em
5\\% a obtida em \\ac{CPU}, com intervalo de confiança que exclui a igualdade,
e na precisão \\ac{INT8} a execução não é possível.""",
)

io.open(caminho, "w", encoding="utf-8").write(t)
for f in feito:
    print("ok  %s" % f)
print("\n%d trocas, %s gravado" % (len(feito), caminho))
