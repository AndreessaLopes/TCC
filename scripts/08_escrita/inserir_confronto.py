"""Incorpora ao texto o confronto das deteccoes com as anotacoes.

A revocacao por faixa de tamanho confirma a direcao do efeito atribuido
aos objetos pequenos e, ao mesmo tempo, mostra que a faixa pequena reune
70 das 2.399 instancias, de modo que nao responde pela maior parte do
deficit. O texto passa a dizer isso, em lugar de atribuir a revocacao ao
tamanho sem medir.

O confronto entre as variantes FP32 e INT8 confirma a hipotese de falsos
positivos que o texto deixava em aberto, e a confirma com numeros: o
acrescimo de 143 deteccoes do YOLOv8n decompoe-se em 172 falsos positivos
a mais e 29 verdadeiros positivos a menos.

Uso: python3 -I inserir_confronto.py <artigo.tex>
"""
import io
import re
import sys

caminho = sys.argv[1]
t = io.open(caminho, encoding="utf-8").read()
feito = []


def trocar(rotulo, antigo, novo):
    global t
    padrao = r"\s+".join(re.escape(p) for p in antigo.split())
    n = len(re.findall(padrao, t))
    if n != 1:
        sys.exit("FALHOU em %s: %d ocorrencias\n  %r" % (rotulo, n, antigo[:90]))
    t = re.sub(padrao, lambda _: novo, t, count=1)
    feito.append(rotulo)


# ================================================ revocacao por tamanho
trocar(
    "revocacao por faixa de tamanho",
    "situação que penaliza a correspondência entre predições e anotações "
    "independentemente da detecção efetiva dos frutos.",
    """situação que penaliza a correspondência entre predições e
anotações independentemente da detecção efetiva dos frutos.

A Tabela~\\ref{tab:tamanho} quantifica o primeiro desses fatores, ao decompor a
revocação por faixa de tamanho da instância anotada, com os limites
convencionais de 32 e 96~pixels de lado aplicados à área que a caixa ocupa na
entrada de 960~pixels.

\\input{tabelas/tamanho.tex}

A revocação cresce com o tamanho da instância nas duas arquiteturas, de 0,386 a
0,698 no YOLOv8n e de 0,286 a 0,678 no YOLOv10n, o que confirma a direção do
efeito atribuído às dimensões do objeto. A faixa pequena, contudo, reúne 70 das
2.399 instâncias anotadas, de modo que não responde pela maior parte do
déficit. As instâncias de tamanho médio, que correspondem ao fruto típico nas
imagens coletadas, concentram 1.276 anotações e respondem por 537 das 898 não
detectadas pelo YOLOv8n. O tamanho do objeto orienta a dificuldade sem
esgotá-la, o que atribui peso aos dois fatores seguintes.""",
)

# ================================================ falsos positivos do INT8
trocar(
    "confirmacao dos falsos positivos",
    "sugere a introdução de falsos positivos pelo erro de quantização, o que é "
    "compatível com a redução de revocação observada na "
    "Tabela~\\ref{tab:validacao_tflite} e com o fato de a calibração ter sido "
    "realizada sobre o subconjunto de validação. Avaliar essa hipótese "
    "exigiria confrontar as detecções com as anotações de referência, o que "
    "não foi conduzido neste trabalho.",
    """sugere a introdução de falsos positivos pelo erro de
quantização, o que é compatível com a redução de revocação observada na
Tabela~\\ref{tab:validacao_tflite} e com o fato de a calibração ter sido
realizada sobre o subconjunto de validação. O confronto das detecções com as
anotações de referência, conduzido em ambiente de desenvolvimento sobre as
mesmas 285 imagens e com o limiar de confiança da aplicação, confirma a
hipótese. A variante \\ac{FP32} do YOLOv8n produz 2.415 detecções, das quais
1.502 correspondem a instâncias anotadas, ao passo que a \\ac{INT8} produz
2.558, das quais 1.473. O acréscimo de 143 detecções decompõe-se em 172 falsos
positivos a mais e 29 verdadeiros positivos a menos, e a precisão cai de 0,622
para 0,576. No YOLOv10n o mesmo confronto registra acréscimo de 13 detecções e
de 3 falsos positivos, coerente com a degradação menor relatada na
Subseção~\\ref{sec:validacao_convertidos}.""",
)

io.open(caminho, "w", encoding="utf-8").write(t)
for f in feito:
    print("ok  %s" % f)
print("\n%d trocas, %s gravado" % (len(feito), caminho))
