# -*- coding: utf-8 -*-
"""Segunda rodada de ajustes da revisao A1, de 2026-11-04.

1. Elimina a alegacao de que o efeito se repete em todos, que convivia com
   a excecao do moto g15.
2. Modera a conclusao da analise de sensibilidade da anotacao assistida.
3. Substitui as afirmacoes de saida preservada e equivalente por contagem
   de deteccoes semelhante no conjunto avaliado.
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


# --------------------------------------------------------------- 1
trocar(
    "1a resumo",
    "O sentido do efeito do \\textit{delegate} repete-se em todos. Em 23 das "
    "24 combinações de aparelho e precisão do YOLOv8n o \\textit{delegate} "
    "reduziu a latência, por fator entre 1,07 e 7,28, com exceção da "
    "precisão INT8 no moto~g15, de razão 0,87, ao passo que no YOLOv10n não "
    "houve ganho em aparelho algum e a magnitude do efeito varia por fator "
    "superior a seis entre as plataformas.",

    "No YOLOv10n a ausência de ganho do \\textit{delegate} ocorreu em todos "
    "os aparelhos. No YOLOv8n houve redução de latência em 23 das 24 "
    "combinações de aparelho e precisão, por fator entre 1,07 e 7,28, e a "
    "exceção foi a precisão INT8 no moto~g15, com razão de 0,87, ao passo "
    "que a magnitude do efeito varia por fator superior a seis entre as "
    "plataformas.",
)

trocar(
    "1b abstract",
    "The direction of the delegate effect holds on all of them. In 23 of the "
    "24 device and precision combinations of YOLOv8n the delegate reduced "
    "latency, by a factor between 1.07 and 7.28, the exception being INT8 on "
    "the moto g15, with a ratio of 0.87, while YOLOv10n showed no gain on "
    "any device and the magnitude varies by a factor greater than six across "
    "platforms.",

    "YOLOv10n showed no delegate gain on any device. YOLOv8n had reduced "
    "latency in 23 of the 24 device and precision combinations, by a factor "
    "between 1.07 and 7.28, the exception being INT8 on the moto g15, with a "
    "ratio of 0.87, while the magnitude varies by a factor greater than six "
    "across platforms.",
)

trocar(
    "1c resultados",
    "O sentido do efeito do \\textit{delegate} \\ac{GPU} é o mesmo nos oito "
    "aparelhos. O YOLOv8n é acelerado em 23 das 24 combinações de aparelho e "
    "precisão, por fator entre 1,07 e 7,28, ao passo que no YOLOv10n o "
    "\\textit{delegate} não produz ganho em nenhuma delas, com razões entre "
    "0,58 e 0,97.",

    "No YOLOv10n o \\textit{delegate} \\ac{GPU} não produz ganho em aparelho "
    "algum, com razões entre 0,58 e 0,97. No YOLOv8n há redução de latência "
    "em 23 das 24 combinações de aparelho e precisão, por fator entre 1,07 e "
    "7,28.",
)

trocar(
    "1d conclusao",
    "O sentido do efeito do \\textit{delegate} \\ac{GPU} repete-se em todos "
    "eles, com aceleração do YOLOv8n em 23 das 24 combinações de aparelho e "
    "precisão, por fator entre 1,07 e 7,28, excetuada a precisão \\ac{INT8} "
    "no moto~g15, de razão 0,87, e com ausência de ganho no YOLOv10n, cuja "
    "variante \\ac{INT8} não executa em aparelho algum.",

    "No YOLOv10n a ausência de ganho do \\textit{delegate} \\ac{GPU} ocorre "
    "em todos eles, e a variante \\ac{INT8} não executa em aparelho algum. "
    "No YOLOv8n há aceleração em 23 das 24 combinações de aparelho e "
    "precisão, por fator entre 1,07 e 7,28, excetuada a precisão \\ac{INT8} "
    "no moto~g15, de razão 0,87.",
)

# --------------------------------------------------------------- 2
trocar(
    "2 moderar sensibilidade",
    "O \\ac{mAP}@0,50 não diminui no subconjunto não afetado, e sim aumenta "
    "em 0,0102 no YOLOv8n e em 0,0022 no YOLOv10n, de modo que o indicador "
    "principal não decorre da anotação assistida.",

    "O \\ac{mAP}@0,50 não diminui no subconjunto não afetado, e sim aumenta "
    "em 0,0102 no YOLOv8n e em 0,0022 no YOLOv10n.",
)

trocar(
    "2b ressalva causal",
    "Quanto ao viés de família, a retirada das imagens anotadas pelo modelo "
    "auxiliar deveria desfavorecer o YOLOv8n, e o observado é o contrário. A "
    "diferença no \\ac{mAP}@0,50 amplia-se de 0,0036 para 0,0116 em favor do "
    "YOLOv8n, e a vantagem do YOLOv10n no \\ac{mAP}@0,50:0,95 reduz-se de "
    "0,0126 para 0,0082. A verificação confronta conjuntos de imagens "
    "distintos, uma vez que os arquivos afetados foram sinalizados por "
    "apresentarem anotação agrupada e correspondem a cenas mais densas, de "
    "modo que parte da variação observada decorre dessa diferença de "
    "composição e não da forma de anotação.",

    "Quanto ao viés de família, a retirada das imagens anotadas pelo modelo "
    "auxiliar deveria desfavorecer o YOLOv8n, e o observado tem sinal "
    "oposto. A diferença no \\ac{mAP}@0,50 amplia-se de 0,0036 para 0,0116 "
    "em favor do YOLOv8n, e a vantagem do YOLOv10n no \\ac{mAP}@0,50:0,95 "
    "reduz-se de 0,0126 para 0,0082. A verificação confronta, contudo, "
    "conjuntos de imagens distintos, uma vez que os arquivos afetados foram "
    "sinalizados por apresentarem anotação agrupada e correspondem a cenas "
    "mais densas. A comparação não isola, portanto, o efeito causal da "
    "anotação assistida, e o que se pode afirmar é que a exclusão das "
    "imagens afetadas não produziu redução do \\ac{mAP}@0,50 nem "
    "deslocamento favorável ao YOLOv8n. A verificação conclusiva exige "
    "revisão manual integral das 285 imagens de teste, de preferência por "
    "avaliadores independentes, procedimento não conduzido neste trabalho.",
)

# --------------------------------------------------------------- 5
trocar(
    "5a resumo FP16",
    "A quantização FP16 preservou a saída dos modelos pela metade do tamanho "
    "de arquivo, enquanto a INT8 alterou o número de detecções.",
    "A quantização FP16 manteve o número de detecções pela metade do tamanho "
    "de arquivo, enquanto a INT8 o alterou.",
)

trocar(
    "5b abstract FP16",
    "FP16 quantisation preserved the models' output at half the file size, "
    "while INT8 changed the number of detections.",
    "FP16 quantisation kept the number of detections at half the file size, "
    "while INT8 changed it.",
)

trocar(
    "5c resultados FP16",
    "A quantização \\ac{FP16} preserva a saída dos modelos.",
    "A quantização \\ac{FP16} mantém o número de detecções no conjunto "
    "avaliado.",
)

trocar(
    "5d equivalencia entre delegates",
    "A equivalência numérica entre \\textit{delegates} está, portanto, "
    "preservada.",
    "As contagens agregadas entre \\textit{delegates} mantêm-se, portanto, "
    "semelhantes no conjunto avaliado. A aplicação registra o número de "
    "detecções, e não as caixas, as confianças e a correspondência com as "
    "anotações, de modo que a semelhança verificada é de contagem agregada e "
    "não de identidade de saída.",
)

trocar(
    "5e sintese FP16",
    "A terceira é que a quantização \\ac{FP16} preserva a saída dos modelos "
    "pela metade do espaço em disco, enquanto a quantização \\ac{INT8} "
    "introduz variação no número de detecções, com indício de falsos "
    "positivos.",
    "A terceira é que a quantização \\ac{FP16} mantém o número de detecções "
    "pela metade do espaço em disco, enquanto a quantização \\ac{INT8} "
    "introduz variação nessa contagem, com indício de falsos positivos.",
)

trocar(
    "5f recomendacao resultados",
    "latência de inferência de 69,2~ms, arquivo de 6,02~MB, saída "
    "equivalente à do modelo em precisão plena. A recomendação vale para os",
    "latência de inferência de 69,2~ms, arquivo de 6,02~MB e contagem de "
    "detecções igual à do modelo em precisão plena no conjunto avaliado. A "
    "recomendação vale para os",
)

trocar(
    "5g conclusao FP16",
    "A precisão \\ac{FP16} preservou a saída dos modelos, pois no YOLOv8n em "
    "\\ac{CPU} as variantes \\ac{FP32} e \\ac{FP16} produziram exatamente o "
    "mesmo número de detecções sobre as 285 imagens, pela metade do tamanho "
    "de arquivo.",
    "A precisão \\ac{FP16} manteve o número de detecções, pois no YOLOv8n em "
    "\\ac{CPU} as variantes \\ac{FP32} e \\ac{FP16} produziram exatamente o "
    "mesmo total sobre as 285 imagens, pela metade do tamanho de arquivo.",
)

trocar(
    "5h recomendacao conclusao",
    "latência de inferência de 69,2~ms, arquivo de 6,02~MB, saída "
    "equivalente à da variante em precisão plena. A recomendação vale para os",
    "latência de inferência de 69,2~ms, arquivo de 6,02~MB e contagem de "
    "detecções igual à da variante em precisão plena no conjunto avaliado. A "
    "recomendação vale para os",
)

open(ARQ, "w", encoding="utf-8").write(t)
print("\narquivo gravado")
