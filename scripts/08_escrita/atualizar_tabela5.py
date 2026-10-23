"""Substitui os indicadores de deteccao da Tabela 5 por medicao registrada.

Os valores anteriores, 0,650 e 0,644 de mAP@0,50, vieram das pastas val2
e val3 de 28 de julho, que guardam apenas graficos, sem as configuracoes
da execucao. O avaliar_teste.py mede sobre a particao de teste com
configuracoes gravadas junto do resultado, em
resultados/csv/metricas_teste.csv.

A troca inverte duas afirmacoes do texto. A precisao, antes atribuida ao
YOLOv10n, e superior no YOLOv8n, e a revocacao, antes tratada como
empate, favorece o YOLOv10n por 0,0083. As demais mudam de magnitude sem
mudar de sentido.

As linhas de custo computacional nao sao tocadas aqui, por dependerem de
medicao de tempo ainda sem registro.

Uso: python3 -I atualizar_tabela5.py <artigo.tex>
"""
import io
import re
import sys

caminho = sys.argv[1]
t = io.open(caminho, encoding="utf-8").read()
feito = []


def trocar(rotulo, antigo, novo):
    """Troca literal, exigindo ocorrencia unica."""
    global t
    if t.count(antigo) != 1:
        sys.exit("FALHOU em %s: %d ocorrencias\n  %r"
                 % (rotulo, t.count(antigo), antigo[:90]))
    t = t.replace(antigo, novo)
    feito.append(rotulo)


def trocar_fluido(rotulo, antigo, novo):
    """Troca tolerante a quebras de linha, exigindo ocorrencia unica."""
    global t
    padrao = r"\s+".join(re.escape(p) for p in antigo.split())
    achados = re.findall(padrao, t)
    if len(achados) != 1:
        sys.exit("FALHOU em %s: %d ocorrencias\n  %r"
                 % (rotulo, len(achados), antigo[:90]))
    t = re.sub(padrao, lambda _: novo, t, count=1)
    feito.append(rotulo)


# ======================================================= linhas da tabela
trocar("linha do mAP@0,50",
       r"\ac{mAP}@0,50 & 0,650 & 0,644",
       r"\ac{mAP}@0,50 & 0,6455 & 0,6419")

trocar("linha do mAP@0,50-0,95",
       r"\ac{mAP}@0,50--0,95 & 0,360 & 0,375",
       r"\ac{mAP}@0,50--0,95 & 0,3610 & 0,3736")

trocar("linha da precisao",
       "Precisão & 0,619 & 0,633",
       "Precisão & 0,6340 & 0,6306")

trocar("linha da revocacao",
       "Revocação & 0,626 & 0,625",
       "Revocação & 0,6132 & 0,6215")

# ================================================== procedencia na fonte
trocar_fluido(
    "fonte da tabela com a procedencia",
    r"\legend{Elaborada pela autora (2026).} \end{table} Os resultados indicam",
    r"""\legend{Elaborada pela autora (2026). Os indicadores de detecção foram
medidos sobre as 285 imagens do conjunto de teste, com entrada de
960~pixels, limiar de confiança de 0,001 e limiar de interseção sobre união
de 0,700, conforme registro em \texttt{resultados/csv/metricas\_teste.csv}.}
\end{table}

Os resultados indicam""",
)

# ===================================================== magnitudes no texto
trocar("diferenca no mAP@0,50",
       "foi de 0,006 em favor do",
       "foi de 0,0036 em favor do")

trocar("diferenca no mAP@0,50-0,95",
       "0,015, indicando maior precisão no ajuste",
       "0,0126, indicando maior precisão no ajuste")

trocar_fluido(
    "precisao e revocacao, sentido invertido",
    "O YOLOv10n também apresentou precisão superior, enquanto os valores de "
    "revocação diferem em 0,001.",
    """A precisão e a revocação
distribuem-se de forma complementar entre as arquiteturas, com vantagem de
0,0034 para o YOLOv8n na primeira e de 0,0083 para o YOLOv10n na segunda,
diferenças da mesma ordem das anteriores.""",
)

# ============================================ resumo, abstract e quadro
trocar("resumo",
       "mAP@0,50 de 0,650 e 0,644 no conjunto de teste",
       "mAP@0,50 de 0,646 e 0,642 no conjunto de teste")

trocar("abstract",
       "mAP@0.50 of 0.650 and 0.644 on the test set",
       "mAP@0.50 of 0.646 and 0.642 on the test set")

trocar("quadro dos objetivos",
       r"\ac{mAP}@0,50 de 0,650 e 0,644 no",
       r"\ac{mAP}@0,50 de 0,646 e 0,642 no")

# ================================================= conclusao e maturacao
trocar(
    "conclusao, desempenho de deteccao",
    r"\ac{mAP}@0,50 de 0,650 para o YOLOv8n e 0,644 para o YOLOv10n",
    r"\ac{mAP}@0,50 de 0,646 para o YOLOv8n e 0,642 para o YOLOv10n",
)

trocar(
    "conclusao, preservacao na conversao",
    "diferenças inferiores a 0,005 nas variantes em precisão plena",
    "diferenças inferiores a 0,002 nas variantes em precisão plena",
)

trocar_fluido(
    "revocacao na subsecao da maturacao",
    "A revocação obtida é de 0,626 no YOLOv8n sobre o conjunto de teste, de "
    "modo que cerca de um terço dos frutos anotados não é localizado.",
    "A revocação obtida é de 0,6132 no YOLOv8n sobre o conjunto de teste, de "
    "modo que aproximadamente 39\\% dos frutos anotados não são localizados.",
)

io.open(caminho, "w", encoding="utf-8").write(t)
for f in feito:
    print("ok  %s" % f)
print("\n%d trocas, %s gravado" % (len(feito), caminho))
