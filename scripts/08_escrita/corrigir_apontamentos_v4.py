"""Atende os apontamentos procedentes da segunda revisao, sobre a v4.

Quatro pontos dizem respeito a distancia entre o que o texto afirma e o
que as medicoes sustentam, e todos se corrigem no proprio texto.

O primeiro e o consumo energetico, que consta dos objetivos especificos
como criterio de comparacao, enquanto a secao de resultados registra que
a resolucao de 1% do indicador de bateria nao discrimina entre as
configuracoes. O objetivo passa a falar em registrar o consumo na
resolucao disponivel, e nao em compara-lo.

O segundo e a recomendacao do YOLOv8n FP16 com delegate GPU, apresentada
sem a ressalva de que essa mesma configuracao apresentou deriva de 46,4%
ao longo de uma sessao no aparelho de referencia.

O terceiro e o alcance da coleta em sete aparelhos, que decorre de 30
imagens por execucao, com numero variavel de sessoes e um exemplar por
modelo, e por isso sustenta a direcao do efeito e nao estimativa de
magnitude por fabricante.

O quarto e a palavra equivalente aplicada ao desempenho de deteccao, que
sugere teste de equivalencia estatistica nao realizado. Passa a
proximidade, com registro explicito de que nao houve teste.

Uso: python3 -I corrigir_apontamentos_v4.py <artigo.tex>
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


# ======================================= objetivo sobre o consumo
trocar(
    "objetivo especifico do consumo energetico",
    "comparar os modelos quanto à acurácia, latência, estabilidade, consumo "
    "energético e tamanho do arquivo gerado;",
    "comparar os modelos quanto à acurácia, latência, estabilidade e tamanho "
    "do arquivo gerado; registrar o consumo energético na resolução permitida "
    "pelo indicador de bateria do sistema;",
)

# ======================================= ressalva na recomendacao
trocar_fluido(
    "ressalva na recomendacao do capitulo de resultados",
    "saída equivalente à do modelo em precisão plena e o menor pico de memória "
    "entre todas as configurações medidas.",
    """saída equivalente à do modelo em precisão plena e o menor pico
de memória entre todas as configurações medidas. A recomendação vale para os
critérios e as condições aqui avaliados. A estabilidade ao longo de sessões
prolongadas permanece como ressalva, uma vez que essa mesma configuração
apresentou deriva de 46,4\\% entre o primeiro e o terceiro terço da execução,
conforme a Tabela~\\ref{tab:deriva}.""",
)

trocar_fluido(
    "ressalva na recomendacao da conclusao",
    "saída equivalente à da variante em precisão plena e o menor pico de "
    "memória entre as configurações avaliadas.",
    """saída equivalente à da variante em precisão plena e o menor
pico de memória entre as configurações avaliadas. A recomendação vale para os
critérios e as condições avaliados, e a estabilidade ao longo de sessões
prolongadas permanece como ressalva, dada a deriva de 46,4\\% registrada nessa
configuração no aparelho de referência.""",
)

# ======================================= alcance da coleta multidispositivo
trocar_fluido(
    "limite da coleta em sete aparelhos",
    "resultado de plataforma e não propriedade do modelo. Em dez das onze "
    "configurações executáveis o número de detecções coincide em todos os "
    "aparelhos, imagem por imagem.",
    """resultado de plataforma e não propriedade do modelo. Em dez
das onze configurações executáveis o número de detecções coincide em todos os
aparelhos, imagem por imagem. Esses resultados têm caráter exploratório, uma
vez que decorrem de execuções sobre 30 imagens, com número variável de sessões
entre os aparelhos e um exemplar de cada modelo, de modo que sustentam a
direção do efeito e não estimativas de magnitude por fabricante ou por
plataforma.""",
)

# ======================================= proximidade em lugar de equivalencia
trocar_fluido(
    "proximidade no capitulo de resultados",
    "Os resultados indicam desempenho de detecção equivalente entre as duas "
    "arquiteturas.",
    "Os resultados indicam desempenho de detecção próximo entre as duas\n"
    "arquiteturas.",
)

trocar_fluido(
    "ausencia de teste de equivalencia",
    "magnitude insuficiente para caracterizar superioridade de uma arquitetura "
    "sobre a outra, considerando que o treinamento foi conduzido em execução "
    "única por modelo.",
    """magnitude insuficiente para caracterizar superioridade de
uma arquitetura sobre a outra, considerando que o treinamento foi conduzido em
execução única por modelo. A proximidade não foi submetida a teste de
equivalência estatística, de modo que o que se afirma é a ausência de evidência
de superioridade, e não a demonstração de igualdade.""",
)

trocar_fluido(
    "proximidade junto as curvas",
    "o que é coerente com a equivalência de desempenho observada na "
    "Tabela~\\ref{tab:resultados_deteccao}.",
    "o que é coerente com a proximidade de desempenho observada na\n"
    "Tabela~\\ref{tab:resultados_deteccao}.",
)

trocar(
    "proximidade na conclusao",
    "Os modelos treinados apresentaram desempenho de detecção equivalente, com",
    "Os modelos treinados apresentaram desempenho de detecção próximo, com",
)

io.open(caminho, "w", encoding="utf-8").write(t)
for f in feito:
    print("ok  %s" % f)
print("\n%d trocas, %s gravado" % (len(feito), caminho))
