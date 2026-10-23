"""Atende os apontamentos procedentes da revisao da versao v3.

Tres entre os dez apontamentos de forma se confirmaram na conferencia.

O primeiro e a citacao de Ye, Xue e Xu, acrescentada hoje para sustentar
a subsecao sobre a classificacao da maturacao, que ficou isolada ali sem
passar pelo referencial. Entra no texto dos trabalhos relacionados e no
quadro comparativo, ao lado de Kazama e outros, que ja estavam nos dois
lugares.

O segundo e o arredondamento. O resumo, o abstract, o quadro de objetivos
e a conclusao traziam tres casas decimais enquanto a Tabela 5 traz quatro,
o que obriga o leitor a verificar se os numeros sao os mesmos. Passam a
trazer os mesmos valores.

O terceiro e a ressalva sobre estabilidade. A subsecao que afirma maior
dispersao em GPU so era delimitada mais adiante, na sintese do capitulo e
na conclusao. A ressalva passa a constar onde a afirmacao e feita.

Os dados de Ye, Xue e Xu foram conferidos na fonte. O limiar de IoU do
mAP relatado nao consta do resumo do artigo, de modo que o texto reporta
o valor sem atribuir limiar.

Uso: python3 -I corrigir_apontamentos_v3.py <artigo.tex>
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


# =============================== Ye, Xue e Xu no referencial
trocar_fluido(
    "paragrafo sobre o ASD-YOLO",
    "Os resultados evidenciam a dificuldade da classificação em campo, "
    "especialmente pela proximidade visual entre estágios de maturação.",
    """Os resultados evidenciam a dificuldade da classificação em
campo, especialmente pela proximidade visual entre estágios de maturação.

Na mesma direção, \\textcite{Ye2025ASD} propuseram o ASD-YOLO, construído
sobre o YOLOv7 com a introdução de atenção L-Norm, do módulo SPD-Conv e do
redimensionador DySample, voltado à detecção da maturação de frutos de café
em cenários com oclusão entre folhas e frutos. O trabalho reporta revocação
de 78,4\\%, precisão de 69,8\\% e \\ac{mAP} de 80,1\\%, com ganho de 2,1
pontos percentuais sobre o YOLOv7. A avaliação foi conduzida em ambiente de
desenvolvimento, sem medição de execução em \\textit{smartphones}, de modo
que o custo da arquitetura proposta em processadores móveis permanece não
verificado.""",
)

trocar_fluido(
    "linha do ASD-YOLO no quadro comparativo",
    r"""2024 & \textcite{Wang2024YOLOv10} & YOLOv10 para detecção em tempo real de ponta a ponta, sem supressão não máxima.""",
    """2025 & \\textcite{Ye2025ASD} & ASD-YOLO, sobre o YOLOv7, com atenção
L-Norm, SPD-Conv e DySample, para detecção da maturação de frutos de café sob
oclusão. & Obteve \\ac{mAP} de 80,1\\%, precisão de 69,8\\% e revocação de
78,4\\%; não avaliou execução em \\textit{smartphones}. & Indica que a
classificação de maturação parte de detectores ajustados a esse fim. \\\\
\\midrule
2024 & \\textcite{Wang2024YOLOv10} & YOLOv10 para detecção em tempo real de
ponta a ponta, sem supressão não máxima.""",
)

# =============================== arredondamento uniforme
trocar("resumo",
       "mAP@0,50 de 0,646 e 0,642 no conjunto de teste",
       "mAP@0,50 de 0,6455 e 0,6419 no conjunto de teste")

trocar("abstract",
       "mAP@0.50 of 0.646 and 0.642 on the test set",
       "mAP@0.50 of 0.6455 and 0.6419 on the test set")

trocar("quadro dos objetivos",
       r"\ac{mAP}@0,50 de 0,646 e 0,642 no",
       r"\ac{mAP}@0,50 de 0,6455 e 0,6419 no")

trocar("conclusao",
       r"\ac{mAP}@0,50 de 0,646 para o YOLOv8n e 0,642 para o YOLOv10n",
       r"\ac{mAP}@0,50 de 0,6455 para o YOLOv8n e 0,6419 para o YOLOv10n")

# =============================== ressalva junto da afirmacao
trocar_fluido(
    "ressalva na subsecao de estabilidade",
    "ao passo que a mais estável, YOLOv8n \\ac{INT8} em \\ac{CPU}, com 10,6\\%, "
    "figura entre as mais lentas.",
    """ao passo que a mais estável, YOLOv8n \\ac{INT8} em \\ac{CPU}, com
10,6\\%, figura entre as mais lentas. Essa relação descreve o aparelho de
referência e não se reproduz nos demais, conforme a
Subseção~\\ref{sec:dispersao_multidispositivo}.""",
)

io.open(caminho, "w", encoding="utf-8").write(t)
for f in feito:
    print("ok  %s" % f)
print("\n%d trocas, %s gravado" % (len(feito), caminho))
