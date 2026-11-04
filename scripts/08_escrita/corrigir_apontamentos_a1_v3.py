# -*- coding: utf-8 -*-
"""Terceira rodada de ajustes da revisao A1, de 2026-11-04.

1. Delimita o alcance dos testes estatisticos a sessao medida e passa a
   ler a diferenca de 5% do YOLOv10n FP16 como ausencia de ganho
   demonstravel.
2. Modera a atribuicao causal da incompatibilidade e declara que os
   registros de particionamento de FP32 e FP16 nao foram coletados.
3. Restringe a recomendacao ao backend de inferencia no aparelho de
   referencia.
"""
import re
import sys

ARQ = sys.argv[1]
t = open(ARQ, encoding="utf-8").read()


def trocar(rotulo, antigo, novo):
    global t
    padrao = r"\s+".join(re.escape(p) for p in antigo.split())
    n = len(re.findall(padrao, t))
    if n != 1:
        sys.exit("FALHOU em %s: %d ocorrencias" % (rotulo, n))
    t = re.sub(padrao, lambda _: novo, t, count=1)
    print("ok  %s" % rotulo)


# ------------------------------------------------------------------ 1
trocar(
    "1a resultados, 5 por cento",
    "No YOLOv10n o mesmo \\textit{delegate} não produz ganho, pois em "
    "\\ac{FP32} a latência aumenta em 47\\% e em \\ac{FP16} supera em 5\\% a "
    "obtida em \\ac{CPU}, com intervalo de confiança que exclui a igualdade, "
    "conforme a Subseção~\\ref{sec:incerteza}. A configuração \\ac{INT8} "
    "sequer é executável.",

    "No YOLOv10n o mesmo \\textit{delegate} não produz ganho, pois em "
    "\\ac{FP32} a latência aumenta em 47\\% e em \\ac{FP16} supera em 5\\% a "
    "obtida em \\ac{CPU}. O intervalo de confiança dessa razão exclui a "
    "igualdade dentro da sessão medida, conforme a "
    "Subseção~\\ref{sec:incerteza}, porém a diferença de 5\\% situa-se abaixo "
    "da resolução do experimento estabelecida na "
    "Subseção~\\ref{sec:repetibilidade}, de modo que deve ser lida como "
    "ausência de ganho demonstrável, e não como perda reproduzível. A "
    "configuração \\ac{INT8} sequer é executável.",
)

trocar(
    "1b alcance dos testes",
    "As cinco diferenças são significativas ao nível de 5\\%, e nenhum dos "
    "intervalos contém a unidade.",

    "Dentro da sessão observada, as cinco comparações acusaram diferença "
    "entre \\ac{CPU} e \\ac{GPU} ao nível de 5\\%, e nenhum dos intervalos "
    "contém a unidade. Esses intervalos e valores de $p$ decorrem da "
    "reamostragem das medições por imagem de uma única sessão e não "
    "incorporam a variabilidade entre sessões, de modo que não sustentam "
    "inferência sobre a reprodutibilidade de diferenças pequenas. O ganho do "
    "YOLOv8n, por fator entre 3,58 e 4,72, excede com folga a resolução "
    "estabelecida na Subseção~\\ref{sec:repetibilidade}; a diferença de 5\\% "
    "do YOLOv10n em \\ac{FP16}, não.",
)

trocar(
    "1c conclusao, 5 por cento",
    "em \\ac{FP16} superou em 5\\% a obtida em \\ac{CPU}, com intervalo de "
    "confiança que exclui a igualdade, e na precisão \\ac{INT8} a execução "
    "não é possível.",

    "em \\ac{FP16} superou em 5\\% a obtida em \\ac{CPU}, diferença que se "
    "situa abaixo da resolução do experimento e indica ausência de ganho "
    "demonstrável, e não perda reproduzível, e na precisão \\ac{INT8} a "
    "execução não é possível.",
)

# ------------------------------------------------------------------ 2
trocar(
    "2a abertura em resultados",
    "A causa do comportamento descrito está na arquitetura do YOLOv10n.",
    "O comportamento descrito é consistente com a presença, no grafo "
    "exportado do YOLOv10n, de operações não suportadas pelo "
    "\\textit{delegate} \\ac{GPU} utilizado.",
)

trocar(
    "2b registros de FP32 e FP16",
    "Nas precisões \\ac{FP32} e \\ac{FP16} a execução completa, mas o custo "
    "das transferências entre \\ac{CPU} e \\ac{GPU} anula o ganho obtido nos "
    "segmentos delegados, resultando no desempenho igual ou inferior ao da "
    "execução integralmente em \\ac{CPU}.",

    "Nas precisões \\ac{FP32} e \\ac{FP16} a execução completa, e o "
    "desempenho resulta igual ou inferior ao da execução integralmente em "
    "\\ac{CPU}. O particionamento do grafo e o custo das transferências "
    "entre as duas memórias oferecem explicação mecanística para esse "
    "resultado. Os registros de delegação dessas duas precisões não foram "
    "coletados, de modo que a explicação se apoia na contagem obtida para a "
    "precisão \\ac{INT8} e na cobertura de operações declarada na "
    "documentação do \\textit{delegate}, e não em medição própria para cada "
    "uma delas.",
)

trocar(
    "2c conclusao, atribuicao causal",
    "A causa está na própria arquitetura. A supressão da etapa de \\ac{NMS}, "
    "que constitui a contribuição central do YOLOv10, é obtida por meio de "
    "operações como \\texttt{TOPK\\_V2}, \\texttt{GATHER\\_ND} e conversões "
    "para \\texttt{INT64}, que o \\textit{delegate} \\ac{GPU} do \\ac{TFLite} "
    "não suporta. O grafo é então particionado entre os dois processadores, e "
    "o custo das transferências entre suas memórias anula o ganho obtido nos "
    "segmentos delegados.",

    "O resultado é consistente com a presença, no grafo exportado, de "
    "operações não suportadas pelo \\textit{delegate} \\ac{GPU} utilizado. A "
    "supressão da etapa de \\ac{NMS}, que constitui a contribuição central do "
    "YOLOv10, é obtida por meio de operações como \\texttt{TOPK\\_V2}, "
    "\\texttt{GATHER\\_ND} e conversões para \\texttt{INT64}, não cobertas "
    "por esse \\textit{delegate}. O particionamento do grafo entre os dois "
    "processadores, e o custo das transferências entre suas memórias, "
    "oferecem explicação mecanística para a ausência de aceleração.",
)

trocar(
    "2d condicoes termicas",
    "sob condições térmicas e de carga equivalentes.",
    "com níveis de carga semelhantes e estado térmico não medido.",
)

# ------------------------------------------------------------------ 3
trocar(
    "3a resumo",
    "A configuração recomendada para a aplicação é o YOLOv8n em FP16 com "
    "\\textit{delegate} de processador gráfico.",
    "Entre as configurações de inferência avaliadas no aparelho de "
    "referência, a recomendada é o YOLOv8n em FP16 com \\textit{delegate} de "
    "processador gráfico.",
)

trocar(
    "3b abstract",
    "The recommended configuration for the application is YOLOv8n in FP16 "
    "with the GPU delegate.",
    "Among the inference configurations evaluated on the reference device, "
    "the recommended one is YOLOv8n in FP16 with the GPU delegate.",
)

trocar(
    "3c resultados",
    "Para a aplicação proposta, a configuração recomendada é \\textbf{YOLOv8n "
    "\\ac{FP16} com \\textit{delegate} \\ac{GPU}}, que apresentou latência de "
    "inferência de 69,2~ms, arquivo de 6,02~MB e contagem de detecções igual "
    "à do modelo em precisão plena no conjunto avaliado. A recomendação vale "
    "para os critérios e as condições aqui avaliados.",

    "Entre as configurações de inferência avaliadas no aparelho de "
    "referência, recomenda-se o \\textbf{YOLOv8n \\ac{FP16} com "
    "\\textit{delegate} \\ac{GPU}}, que apresentou latência de inferência de "
    "69,2~ms, arquivo de 6,02~MB e contagem de detecções igual à do modelo em "
    "precisão plena no conjunto avaliado. A recomendação incide sobre a etapa "
    "de inferência e não se estende à latência total da aplicação, dominada "
    "pela preparação da imagem, conforme a "
    "Subseção~\\ref{sec:decomposicao_latencia}.",
)

trocar(
    "3d conclusao",
    "Para a aplicação proposta, a configuração recomendada é o \\textbf{YOLOv8n "
    "em precisão \\ac{FP16} com \\textit{delegate} \\ac{GPU}}, que apresentou "
    "latência de inferência de 69,2~ms, arquivo de 6,02~MB e contagem de "
    "detecções igual à da variante em precisão plena no conjunto avaliado. A "
    "recomendação vale para os",

    "Entre as configurações de inferência avaliadas no aparelho de "
    "referência, recomenda-se o \\textbf{YOLOv8n em precisão \\ac{FP16} com "
    "\\textit{delegate} \\ac{GPU}}, que apresentou latência de inferência de "
    "69,2~ms, arquivo de 6,02~MB e contagem de detecções igual à da variante "
    "em precisão plena no conjunto avaliado. A recomendação incide sobre a "
    "etapa de inferência e não se estende à latência total da aplicação, "
    "dominada pela preparação da imagem. Ela vale para os",
)

open(ARQ, "w", encoding="utf-8").write(t)
print("\narquivo gravado")
