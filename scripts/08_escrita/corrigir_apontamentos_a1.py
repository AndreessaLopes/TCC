# -*- coding: utf-8 -*-
"""Aplica os quatro ajustes levantados na revisao A1 de 2026-11-03.

1. Contradicao do moto g15 entre resumo, abstract, corpo e conclusao.
2. Limiar de 0,25 declarado como escolha a priori.
3. Sobreposicao entre a reanotacao semi-automatica e a particao de teste.
4. Assimetria do criterio de parada e regra de descarte das medicoes.
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


# ---------------------------------------------------------------- 1
trocar(
    "1a resumo",
    "O sentido do efeito do \\textit{delegate} repete-se em todos, com "
    "aceleração do YOLOv8n por fator entre 1,07 e 7,28 e ausência de ganho "
    "no YOLOv10n, ao passo que a magnitude varia por fator superior a seis "
    "entre as plataformas.",
    "O sentido do efeito do \\textit{delegate} repete-se em todos. Em 23 das "
    "24 combinações de aparelho e precisão do YOLOv8n o \\textit{delegate} "
    "reduziu a latência, por fator entre 1,07 e 7,28, com exceção da "
    "precisão INT8 no moto~g15, de razão 0,87, ao passo que no YOLOv10n não "
    "houve ganho em aparelho algum e a magnitude do efeito varia por fator "
    "superior a seis entre as plataformas.",
)

trocar(
    "1b abstract",
    "The direction of the delegate effect holds on all of them, with YOLOv8n "
    "accelerated by a factor between 1.07 and 7.28 and no gain for YOLOv10n, "
    "whereas the magnitude varies by a factor greater than six across "
    "platforms.",
    "The direction of the delegate effect holds on all of them. In 23 of the "
    "24 device and precision combinations of YOLOv8n the delegate reduced "
    "latency, by a factor between 1.07 and 7.28, the exception being INT8 on "
    "the moto g15, with a ratio of 0.87, while YOLOv10n showed no gain on "
    "any device and the magnitude varies by a factor greater than six across "
    "platforms.",
)

trocar(
    "1c corpo",
    "O YOLOv8n é acelerado em todas as plataformas, por fator entre 1,07 e "
    "7,28, ao passo que no YOLOv10n o \\textit{delegate} não produz ganho em "
    "nenhuma delas, com razões entre 0,58 e 0,97.",
    "O YOLOv8n é acelerado em 23 das 24 combinações de aparelho e precisão, "
    "por fator entre 1,07 e 7,28, ao passo que no YOLOv10n o "
    "\\textit{delegate} não produz ganho em nenhuma delas, com razões entre "
    "0,58 e 0,97.",
)

trocar(
    "1d conclusao",
    "O sentido do efeito do \\textit{delegate} \\ac{GPU} repete-se em todos "
    "eles, com aceleração do YOLOv8n por fator entre 1,07 e 7,28 e ausência "
    "de ganho no YOLOv10n, cuja variante \\ac{INT8} não executa em aparelho "
    "algum.",
    "O sentido do efeito do \\textit{delegate} \\ac{GPU} repete-se em todos "
    "eles, com aceleração do YOLOv8n em 23 das 24 combinações de aparelho e "
    "precisão, por fator entre 1,07 e 7,28, excetuada a precisão \\ac{INT8} "
    "no moto~g15, de razão 0,87, e com ausência de ganho no YOLOv10n, cuja "
    "variante \\ac{INT8} não executa em aparelho algum.",
)

# ---------------------------------------------------------------- 2
trocar(
    "2 limiar a priori",
    "O maior valor de F1 ocorre em limiar de 0,24 no YOLOv8n e de 0,27 no "
    "YOLOv10n, o que respalda o limiar de 0,25 adotado na aplicação.",
    "O limiar de 0,25 adotado na aplicação corresponde ao valor padrão da "
    "biblioteca de treinamento e foi fixado antes da avaliação. O maior "
    "valor de F1 ocorre em limiar de 0,24 no YOLOv8n e de 0,27 no YOLOv10n, "
    "de modo que a escolha prévia situa-se junto ao ótimo observado no "
    "conjunto de teste, constatação posterior que não participou da "
    "definição do limiar.",
)

# ---------------------------------------------------------------- 4b
trocar(
    "4b regra de descarte",
    "Cada execução processou as mesmas 285 imagens da partição de teste, "
    "precedida de dez inferências de aquecimento descartadas da apuração. A "
    "ordem das imagens foi mantida constante entre execuções.",
    "Cada execução processou as mesmas 285 imagens da partição de teste, "
    "precedida de dez inferências de aquecimento descartadas da apuração. A "
    "ordem das imagens foi mantida constante entre execuções. A aplicação "
    "descarta da apuração a medição cuja latência total supera o terceiro "
    "quartil acrescido de três vezes a amplitude interquartil da própria "
    "execução, critério fixado antes da coleta e destinado a excluir "
    "suspensões do processo pelo sistema operacional. O descarte ocorreu em "
    "duas configurações, com uma medição no YOLOv8n \\ac{FP32} em \\ac{GPU} "
    "e quatro no YOLOv8n \\ac{INT8} em \\ac{GPU}. A configuração YOLOv8n "
    "\\ac{FP16} em \\ac{GPU} registrou 283 medições, uma vez que duas "
    "imagens não produziram registro no arquivo de saída, ausência cuja "
    "causa não foi identificada. Esses valores explicam a coluna n da "
    "Tabela~\\ref{tab:latencia_inferencia}.",
)

# ---------------------------------------------------------------- 3 e 4a
trocar(
    "3 e 4a limitacoes",
    "\\textbf{Conjunto parcialmente anotado.}",
    "\\textbf{Anotação assistida por modelo na partição de teste.} A "
    "reanotação semi-automática descrita na "
    "Subseção~\\ref{sec:preprocessamento} incidiu sobre 836 arquivos "
    "sinalizados pela triagem, dos quais 91 pertencem à partição de teste, "
    "o que corresponde a 31,9\\% das 285 imagens e a 789 das 2.399 "
    "instâncias anotadas nessa partição. As caixas desses arquivos foram "
    "propostas por um modelo YOLOv8n auxiliar e submetidas a inspeção "
    "visual por amostragem, e não a revisão integral. Como o modelo "
    "auxiliar pertence à mesma família arquitetural de um dos modelos "
    "avaliados, parcela da referência empregada no cálculo das métricas "
    "carrega o viés indutivo dessa família, o que pode elevar as métricas "
    "de ambos os modelos e favorecer o YOLOv8n na comparação entre as duas "
    "arquiteturas. O modelo auxiliar foi treinado exclusivamente com "
    "arquivos da partição de treinamento, de modo que não houve exposição "
    "prévia às imagens de teste, porém essa separação não elimina o viés "
    "descrito.\n\n"
    "\\textbf{Critério de parada assimétrico entre as arquiteturas.} "
    "Conforme a Subseção~\\ref{sec:desempenho_deteccao}, o YOLOv8n "
    "encerrou o treinamento por parada antecipada na época 74, após 30 "
    "épocas sem superar o melhor desempenho em validação, ao passo que o "
    "YOLOv10n executou as 80 épocas configuradas e alcançou o melhor "
    "desempenho na época 79. O primeiro modelo atingiu o critério de "
    "convergência adotado e o segundo foi encerrado por limite de épocas "
    "enquanto ainda apresentava melhoria. A comparação de desempenho de "
    "detecção entre as duas arquiteturas, e as análises de quantização "
    "dela derivadas, estão condicionadas a essa assimetria.\n\n"
    "\\textbf{Conjunto parcialmente anotado.}",
)

open(ARQ, "w", encoding="utf-8").write(t)
print("\narquivo gravado")
