"""Liga o achado do preenchimento a conclusao de alcance geral.

A conclusao sustenta que indicadores de custo medidos em ambiente de
desenvolvimento nao predizem o desempenho em dispositivo movel quando ha
aceleracao por hardware, e apoia isso em duas previsoes que nao se
confirmaram. A Subsecao 4.3 registra que a ordem entre as arquiteturas
quanto ao tempo de inferencia se inverte conforme o preenchimento da
entrada, dentro do proprio ambiente de desenvolvimento. As duas coisas
estavam escritas em lugares separados.

Acrescenta o rotulo da subsecao, para que a conclusao possa remeter a ela,
e um paragrafo que usa o achado como terceira evidencia.

Uso: python3 -I amarrar_preenchimento_conclusao.py <artigo.tex>
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


trocar(
    "rotulo da subsecao de desempenho",
    r"\subsection{Desempenho dos Modelos de Detecção}",
    "\\subsection{Desempenho dos Modelos de Detecção}\n"
    "\\label{sec:desempenho_deteccao}",
)

trocar_fluido(
    "terceira evidencia na conclusao",
    "O fator determinante não é o volume de computação exigido pelo modelo, "
    "mas a compatibilidade entre as operações que ele emprega e aquelas que o "
    "acelerador implementa.",
    """O fator determinante não é o volume de computação exigido pelo modelo,
mas a compatibilidade entre as operações que ele emprega e aquelas que o
acelerador implementa.

Uma terceira observação, de porte menor, aponta no mesmo sentido e antecede
a saída do modelo do ambiente de treinamento. Conforme a
Subseção~\\ref{sec:desempenho_deteccao}, a ordem entre as duas arquiteturas
quanto ao tempo de inferência depende do preenchimento aplicado às imagens.
Sob o agrupamento retangular por lote, o YOLOv10n é mais rápido. Sob o
preenchimento quadrado que a aplicação executa no aparelho, é mais lento, e
as faixas das três execuções de cada arquitetura não se sobrepõem. A
comparação entre arquiteturas não constitui, portanto, propriedade das
arquiteturas tomadas isoladamente, e sim do conjunto formado por elas, pelo
preenchimento da entrada e pelo processador que as executa. É a mesma
dependência que a comparação entre \\textit{delegates} evidencia, observável
já dentro do ambiente de desenvolvimento.""",
)

io.open(caminho, "w", encoding="utf-8").write(t)
for f in feito:
    print("ok  %s" % f)
print("\n%d trocas, %s gravado" % (len(feito), caminho))
