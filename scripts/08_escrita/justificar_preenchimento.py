"""Registra no texto por que a Tabela 5 usa preenchimento quadrado.

O diagnostico conferir_origem_tabela5.py reproduziu os valores anteriores
da Tabela 5 sobre o conjunto de teste com rect=True, o padrao da
biblioteca, nos quatro indicadores. Os valores nao estavam errados, e a
medicao atual difere deles por adotar rect=False.

A opcao nao e arbitraria e por isso passa a constar do texto. As variantes
convertidas para TFLite tem forma de entrada fixa, de modo que o
agrupamento retangular nao se aplica a elas, e a comparacao entre a
tabela dos modelos treinados e a das variantes so atribui a conversao o
que vem da conversao se ambas forem medidas sob o mesmo preenchimento. O
preenchimento quadrado tambem reproduz o pre-processamento da aplicacao
no aparelho.

Os valores obtidos sob o padrao da biblioteca ficam registrados no proprio
paragrafo, para que quem repetir a medicao com as opcoes padrao encontre
a diferenca explicada em vez de aparente divergencia.

Uso: python3 -I justificar_preenchimento.py <artigo.tex>
"""
import io
import re
import sys

caminho = sys.argv[1]
t = io.open(caminho, encoding="utf-8").read()
feito = []


def trocar(rotulo, antigo, novo):
    global t
    if t.count(antigo) != 1:
        sys.exit("FALHOU em %s: %d ocorrencias\n  %r"
                 % (rotulo, t.count(antigo), antigo[:90]))
    t = t.replace(antigo, novo)
    feito.append(rotulo)


def trocar_fluido(rotulo, antigo, novo):
    global t
    padrao = r"\s+".join(re.escape(p) for p in antigo.split())
    if len(re.findall(padrao, t)) != 1:
        sys.exit("FALHOU em %s: %d ocorrencias\n  %r"
                 % (rotulo, len(re.findall(padrao, t)), antigo[:90]))
    t = re.sub(padrao, lambda _: novo, t, count=1)
    feito.append(rotulo)


# ------------------------------------- rotulo na subsecao das variantes
trocar(
    "rotulo da validacao dos convertidos",
    r"\subsection{Validação dos Modelos Convertidos}",
    "\\subsection{Validação dos Modelos Convertidos}\n"
    "\\label{sec:validacao_convertidos}",
)

# ------------------------------------- fonte da tabela, entrada quadrada
trocar("fonte da tabela, entrada quadrada",
       "com entrada de\n960~pixels",
       "com entrada quadrada de\n960~pixels")

# ------------------------------------- paragrafo com a justificativa
trocar_fluido(
    "justificativa do preenchimento",
    "0,0034 para o YOLOv8n na primeira e de 0,0083 para o YOLOv10n na "
    "segunda, diferenças da mesma ordem das anteriores.",
    """0,0034 para o YOLOv8n na primeira e de 0,0083 para o YOLOv10n na
segunda, diferenças da mesma ordem das anteriores.

Os indicadores acima foram obtidos com preenchimento das imagens até o
quadrado de 960~pixels, e não com o agrupamento retangular por lote que a
biblioteca de avaliação adota por padrão. A escolha tem duas razões. A
primeira é que as variantes convertidas, avaliadas na
Subseção~\\ref{sec:validacao_convertidos}, operam com forma de entrada
fixa, de modo que o agrupamento retangular não se aplica a elas, e medir
ambas as tabelas sob o mesmo preenchimento é o que permite atribuir à
conversão a diferença entre elas. A segunda é que o preenchimento
quadrado reproduz o pré-processamento executado pela aplicação no
aparelho, descrito na Subseção~\\ref{sec:decomposicao_latencia}. Sob o
agrupamento retangular, os mesmos pesos sobre o mesmo conjunto de teste
resultam em \\ac{mAP}@0,50 de 0,6497 no YOLOv8n e 0,6442 no YOLOv10n,
diferença que decorre do preenchimento e não dos modelos.""",
)

io.open(caminho, "w", encoding="utf-8").write(t)
for f in feito:
    print("ok  %s" % f)
print("\n%d trocas, %s gravado" % (len(feito), caminho))
