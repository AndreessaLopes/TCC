# -*- coding: utf-8 -*-
"""Ajusta os elementos pre-textuais ao modelo oficial de artigo do curso.

O modelo de artigo cientifico do IFMG traz resumo e palavras-chave e nao
traz abstract nem keywords. O resumo e reduzido para caber em uma pagina
com as palavras-chave, mantendo-se dentro da faixa de 150 a 500 palavras
prevista no modelo. As linhas de membro de banca passam a trazer
marcadores a preencher.
"""
import re
import sys

ARQ = sys.argv[1]
t = open(ARQ, encoding="utf-8").read()


def corpo(texto, i):
    nivel, j = 1, i
    while j < len(texto) and nivel:
        if texto[j] == "{":
            nivel += 1
        elif texto[j] == "}":
            nivel -= 1
        j += 1
    return texto[i:j - 1], j


def remover(comando):
    global t
    m = re.search(r"\\" + comando + r"\{", t)
    if not m:
        sys.exit("FALHOU, nao encontrei \\%s" % comando)
    _, fim = corpo(t, m.end())
    while fim < len(t) and t[fim] in "\n":
        fim += 1
    t = t[:m.start()] + t[fim:]
    print("ok  removido \\%s" % comando)


def substituir_corpo(comando, novo):
    global t
    m = re.search(r"\\" + comando + r"\{", t)
    if not m:
        sys.exit("FALHOU, nao encontrei \\%s" % comando)
    _, fim = corpo(t, m.end())
    t = t[:m.end()] + novo + t[fim - 1:]
    print("ok  reescrito \\%s" % comando)


RESUMO = (
    "A cafeicultura possui relevância econômica e social para o Brasil, e a "
    "identificação do estágio de maturação dos frutos apoia o planejamento da "
    "colheita. Em lavouras de campo aberto essa avaliação ainda depende da "
    "inspeção visual, sujeita a variações de iluminação, oclusão por folhas e "
    "distribuição irregular dos frutos. Ainda são limitados os estudos que "
    "avaliam a execução de modelos de detecção em \\textit{smartphones} "
    "Android reais. Este trabalho compara configurações de modelos leves de "
    "detecção de objetos convertidos para TensorFlow Lite, voltadas à "
    "detecção de frutos de café em dispositivos móveis. Foram utilizadas "
    "2.168 imagens únicas, com 17.659 instâncias anotadas, sobre as quais os "
    "modelos YOLOv8n e YOLOv10n alcançaram mAP@0,50 de 0,6455 e 0,6419 no "
    "conjunto de teste. A conversão gerou seis variantes nas precisões FP32, "
    "FP16 e INT8, e as onze configurações executáveis foram avaliadas em "
    "dispositivo Android quanto à latência, à estabilidade de execução e ao "
    "pico de memória do processo. O \\textit{delegate} de processador gráfico "
    "reduziu a latência de inferência do YOLOv8n por fator de até 4,7, "
    "enquanto no YOLOv10n não produziu ganho, pois as operações que "
    "implementam sua arquitetura sem supressão não máxima não são suportadas "
    "pelo \\textit{delegate}, o que inviabiliza a execução na precisão INT8. "
    "A quantização FP16 manteve o número de detecções pela metade do tamanho "
    "de arquivo, enquanto a INT8 o alterou. As execuções em processador "
    "gráfico apresentaram menor estabilidade, com degradação de até 57\\% ao "
    "longo de uma sessão. A avaliação foi estendida a oito aparelhos de três "
    "fornecedores de \\textit{System on Chip} sobre um subconjunto de 30 "
    "imagens, com redução de latência do YOLOv8n em 23 das 24 combinações de "
    "aparelho e precisão e ausência de ganho no YOLOv10n em todos eles. Entre "
    "as configurações de inferência avaliadas no aparelho de referência, a "
    "recomendada é o YOLOv8n em FP16 com \\textit{delegate} de processador "
    "gráfico. A detecção foi conduzida com classe única, de modo que a "
    "classificação do estágio de maturação constitui continuidade e não "
    "integra o escopo deste trabalho."
)

substituir_corpo("resumo", "\n    " + RESUMO + "\n")
remover("abstract")
remover("keywords")

antigo = ("% \\membrobanca{Fulano de Tal}{Instituição do Fulano de Tal}\n"
          "% \\membrobanca{Ciclano de Tal}{Instituição do Ciclano de Tal}")
novo = ("\\membrobanca{Membro 1 a preencher}{Instituição a preencher}\n"
        "\\membrobanca{Membro 2 a preencher}{Instituição a preencher}")
if t.count(antigo) != 1:
    sys.exit("FALHAU nas linhas de banca")
t = t.replace(antigo, novo)
print("ok  banca com marcadores")

open(ARQ, "w", encoding="utf-8").write(t)
print("\narquivo gravado")
