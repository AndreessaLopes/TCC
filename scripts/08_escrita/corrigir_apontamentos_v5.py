"""Atende os apontamentos procedentes da revisao da v5.

Tres pontos, nenhum deles dependente da decisao sobre o titulo.

O primeiro e a lista de contribuicoes, no fim do referencial, escrita
quando as etapas ainda estavam por fazer. Prometia classificacao por
estagios de maturacao para indicar o momento da colheita e falava em
quantizacoes a serem aplicadas. Passa a descrever o que foi feito.

O segundo e a redacao de duas citacoes. Uma frase ficou sem verbo
principal apos a citacao, e outra concorda no plural com autor unico.

O terceiro e a interpretacao da concordancia entre aparelhos. O registro
guarda o numero de deteccoes por imagem, conferido nos CSVs de lote, e
nao as coordenadas das caixas, de modo que a coincidencia e de
quantidade. A distincao passa a constar.

Uso: python3 -I corrigir_apontamentos_v5.py <artigo.tex>
"""
import io
import re
import sys

caminho = sys.argv[1]
t = io.open(caminho, encoding="utf-8").read()
feito = []


def trocar_fluido(rotulo, antigo, novo):
    global t
    padrao = r"\s+".join(re.escape(p) for p in antigo.split())
    if len(re.findall(padrao, t)) != 1:
        sys.exit("FALHOU em %s: %d ocorrencias\n  %r"
                 % (rotulo, len(re.findall(padrao, t)), antigo[:90]))
    t = re.sub(padrao, lambda _: novo, t, count=1)
    feito.append(rotulo)


# ========================================= redacao das citacoes
trocar_fluido(
    "frase sem verbo principal apos a citacao",
    "Em 2021, \\textcite{Bazame2021Detection}, a detecção da maturação de "
    "frutos de café foi tratada como uma tarefa de detecção, classificação e "
    "mapeamento durante a colheita.",
    """Em 2021, \\textcite{Bazame2021Detection} trataram a detecção da
maturação de frutos de café como tarefa de detecção, classificação e mapeamento
durante a colheita.""",
)

trocar_fluido(
    "concordancia com autor unico",
    "Em 2023, \\textcite{Menghani2023Efficient} discutem técnicas de eficiência",
    "Em 2023, \\textcite{Menghani2023Efficient} discute técnicas de eficiência",
)

# ========================================= lista de contribuicoes
trocar_fluido(
    "segunda contribuicao, do planejado ao realizado",
    "O segundo é a orientação prática da classificação, cujo objetivo é "
    "fornecer ao produtor rural uma indicação sobre o momento adequado para a "
    "colheita, com base em estágios de maturação a serem definidos a partir de "
    "critérios agronômicos específicos para a região.",
    """O segundo é a orientação prática da aplicação, que executa a
detecção dos frutos diretamente no aparelho do produtor rural. A detecção com
classe única constitui a etapa preparatória para a avaliação da maturação, cuja
classificação por estágios não integra o escopo deste trabalho.""",
)

trocar_fluido(
    "terceira contribuicao, do planejado ao realizado",
    "a serem aplicadas aos modelos YOLOv8n e YOLOv10n, permitindo comparar o "
    "impacto de cada abordagem sobre acurácia, tamanho do modelo e latência de "
    "inferência.",
    """aplicadas aos modelos YOLOv8n e YOLOv10n, que permitiram
comparar o impacto de cada abordagem sobre acurácia, tamanho do modelo e
latência de inferência.""",
)

trocar_fluido(
    "quarta contribuicao, consumo energetico",
    "faixas de preço, medindo latência, estabilidade de execução e consumo "
    "energético.",
    """faixas de preço, com medição de latência e de estabilidade de
execução e registro do consumo energético na resolução disponível.""",
)

# ========================================= concordancia de quantidade
trocar_fluido(
    "concordancia de quantidade, nao de caixas",
    "A comparação das saídas verifica se o mesmo modelo produz as mesmas "
    "detecções em plataformas distintas. Em dez das onze configurações "
    "executáveis, o número de detecções coincide em todos os aparelhos, imagem "
    "por imagem, perfazendo 310 concordâncias em 321 comparações.",
    """A comparação das saídas verifica se o mesmo modelo produz o mesmo número
de detecções em plataformas distintas. Em dez das onze configurações
executáveis, o número de detecções coincide em todos os aparelhos, imagem por
imagem, perfazendo 310 concordâncias em 321 comparações.

A medida é de concordância de quantidade. O registro produzido pela aplicação
contém o número de detecções por imagem e não as coordenadas das caixas
delimitadoras, de modo que a coincidência das contagens não demonstra
identidade das caixas, e sim ausência de divergência no número de objetos
detectados. A verificação da sobreposição entre caixas exigiria registrar as
coordenadas em cada aparelho, o que não foi solicitado aos voluntários.""",
)

io.open(caminho, "w", encoding="utf-8").write(t)
for f in feito:
    print("ok  %s" % f)
print("\n%d trocas, %s gravado" % (len(feito), caminho))
