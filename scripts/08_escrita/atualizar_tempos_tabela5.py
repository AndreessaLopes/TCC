"""Fecha a Tabela 5 com os tempos medidos em tres execucoes.

A tabela atribuia ao YOLOv10n vantagem em todos os indicadores de custo,
a partir de leitura unica. Medido tres vezes sob o preenchimento quadrado,
o tempo de inferencia fica entre 7,56 e 8,94 ms no YOLOv8n e entre 9,90 e
10,54 ms no YOLOv10n. As faixas nao se sobrepoem e a diferenca entre as
arquiteturas supera a variacao entre execucoes de cada uma, de modo que a
vantagem do YOLOv10n na inferencia nao se sustenta nessa configuracao.

Sob o agrupamento retangular a ordem se inverte, 8,7 contra 7,7 ms, o que
e registrado no texto por mostrar que a comparacao depende do
preenchimento. A vantagem no pos-processamento permanece, com razao media
de 4,1 vezes em lugar das 6,3 antes reportadas.

Uso: python3 -I atualizar_tempos_tabela5.py <artigo.tex>
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


# ----------------------------------------------- linhas de tempo
trocar("linha do tempo de inferencia",
       "Tempo de inferência (ms) & 9,2 & 8,7",
       "Tempo de inferência (ms) & 8,32 & 10,20")

trocar("linha do tempo de pos-processamento",
       "Tempo de pós-processamento (ms) & 1,9 & 0,3",
       "Tempo de pós-processamento (ms) & 1,95 & 0,48")

# ----------------------------------------------- fonte da tabela
trocar_fluido(
    "fonte da tabela com os tempos",
    r"de 0,700, conforme registro em \texttt{resultados/csv/metricas\_teste.csv}.}",
    """de 0,700, conforme registro em
\\texttt{resultados/csv/metricas\\_teste.csv}. Os tempos são a média de três
execuções, registradas em \\texttt{resultados/csv/tempos\\_teste.csv}.}""",
)

# ----------------------------------------------- abertura do paragrafo
trocar_fluido(
    "abertura do paragrafo de custo",
    "No que se refere ao custo computacional, o YOLOv10n apresentou vantagem "
    "em todos os indicadores medidos.",
    """No que se refere ao custo computacional, o YOLOv10n apresentou vantagem
nos indicadores derivados da arquitetura e no pós-processamento, e
desvantagem no tempo de inferência.""",
)

trocar_fluido(
    "razao do pos-processamento",
    "A maior diferença foi observada no tempo de pós-processamento, "
    "aproximadamente 6,3 vezes menor no YOLOv10n.",
    """A maior diferença entre as
vantagens foi observada no tempo de pós-processamento, em média 4,1 vezes
menor no YOLOv10n.""",
)

# ----------------------------------------------- paragrafo da inferencia
trocar_fluido(
    "paragrafo sobre o tempo de inferencia",
    "elimina o processamento associado à filtragem de detecções redundantes.",
    """elimina o processamento associado à filtragem de detecções redundantes.

O tempo de inferência não acompanha essa vantagem. As três execuções
situam-se entre 7,56 e 8,94~ms no YOLOv8n e entre 9,90 e 10,54~ms no
YOLOv10n, de modo que as faixas não se sobrepõem e a diferença entre as
arquiteturas supera a variação entre execuções de cada uma. O resultado
depende do preenchimento adotado, uma vez que sob o agrupamento retangular
da biblioteca a ordem se inverte, com 8,7~ms no YOLOv8n e 7,7~ms no
YOLOv10n. Como a aplicação no aparelho preenche a imagem até o quadrado, a
medição com preenchimento quadrado é a que corresponde ao uso previsto.
Trata-se, de todo modo, de medição em processador gráfico de ambiente de
desenvolvimento, cuja relação com o comportamento em processador móvel
constitui objeto da avaliação experimental.""",
)

# ----------------------------------------------- conclusao
trocar("razao do pos-processamento na conclusao",
       "de aproximadamente 6,3 vezes em ambiente de desenvolvimento",
       "de aproximadamente 4,1 vezes em ambiente de desenvolvimento")

# ----------------------------------------------- resumo e abstract
trocar("resumo, custo computacional",
       "respectivamente, com custo computacional inferior no YOLOv10n.",
       "respectivamente, com menor número de parâmetros e operações no "
       "YOLOv10n.")

trocar_fluido("abstract, custo computacional",
              "with lower computational cost for YOLOv10n.",
              "with\n    fewer parameters and operations for YOLOv10n.")

io.open(caminho, "w", encoding="utf-8").write(t)
for f in feito:
    print("ok  %s" % f)
print("\n%d trocas, %s gravado" % (len(feito), caminho))
