# -*- coding: utf-8 -*-
"""Acrescenta a sensibilidade ao descarte de medicoes e delimita o escopo
dos intervalos de confianca."""
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


trocar(
    "sensibilidade ao descarte",
    "A configuração YOLOv8n \\ac{FP16} em \\ac{GPU} registrou 283 medições, "
    "uma vez que duas imagens não produziram registro no arquivo de saída, "
    "ausência cuja causa não foi identificada. Esses valores explicam a "
    "coluna n da Tabela~\\ref{tab:latencia_inferencia}.",

    "A configuração YOLOv8n \\ac{FP16} em \\ac{GPU} registrou 283 medições, "
    "uma vez que duas imagens não produziram registro no arquivo de saída, "
    "ausência cuja causa não foi identificada e que permanece classificada "
    "como dado faltante. Esses valores explicam a coluna n da "
    "Tabela~\\ref{tab:latencia_inferencia}.\n\n"
    "O efeito do descarte sobre os indicadores de latência de inferência "
    "consta da Tabela~\\ref{tab:descartes}. As medições excluídas "
    "apresentam latência de inferência compatível com a distribuição da "
    "própria execução, entre 53,41~ms e 152,42~ms, e latência total entre "
    "3.379,43~ms e 4.271,73~ms, da ordem do dobro da média da execução. O "
    "descarte altera a média da latência de inferência em até 0,1~ms, o p95 "
    "em até 0,7~ms e o coeficiente de variação em até 0,1 ponto percentual, "
    "de modo que não melhora de forma apreciável os indicadores de "
    "estabilidade da inferência. O critério incide sobre a latência total "
    "porque a anomalia que ele visa, a suspensão do processo pelo sistema "
    "operacional, manifesta-se na preparação da imagem e não na inferência, "
    "leitura compatível com os valores observados.\n\n"
    "\\input{tabelas/descartes.tex}\n",
)

trocar(
    "escopo dos intervalos",
    "intervalo de confiança de cada uma, obtido por reamostragem com "
    "reposição sobre as imagens medidas. A largura dos intervalos situa-se "
    "entre 2,5\\% e 6,5\\% da respectiva média.",

    "intervalo de confiança de cada uma, obtido por reamostragem com "
    "reposição sobre as imagens medidas. A largura dos intervalos situa-se "
    "entre 2,5\\% e 6,5\\% da respectiva média. Esses intervalos quantificam "
    "a variação entre imagens dentro de uma mesma execução, uma vez que a "
    "reamostragem incide sobre as imagens de uma única sessão por "
    "configuração. Não incorporam, portanto, a variação entre sessões, cuja "
    "ordem de grandeza consta da Tabela~\\ref{tab:sessoes} e alcança 38,0\\%, "
    "de modo que a largura aqui reportada não deve ser lida como incerteza "
    "da latência de uma nova execução.",
)

open(ARQ, "w", encoding="utf-8").write(t)
print("arquivo gravado")
