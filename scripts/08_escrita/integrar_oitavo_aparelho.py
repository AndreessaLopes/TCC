"""Integra ao texto o oitavo aparelho, um Redmi 13C.

A coleta acrescenta as onze configuracoes executaveis, com dez
aquecimentos, 30 imagens, nenhum descarte e primeira configuracao
iniciada com 80% de bateria, de modo que nao ha desvio de protocolo a
registrar.

Tres resultados mudam de valor. O menor ganho do delegate GPU no YOLOv8n
passa de 1,48 para 1,07, observado no proprio Redmi 13C em INT8. A razao
entre o maior e o menor ganho passa a superar seis. O par de
concordancias passa de 310 em 321 para 312 em 323, numero que o
conferir_concordancia.py apura e que corrige contagem manual anterior; os
demais valores daquela analise, as 26 imagens comuns, as 11 divergencias
e o total de 275 deteccoes, foram reproduzidos sem alteracao.

Um resultado novo aparece. O Redmi 13C e o Redmi Note 9 empregam o mesmo
SoC, o que o conjunto ainda nao tinha, e a comparacao entre os dois
separa o que decorre do chipset do que decorre do aparelho e da versao do
sistema.

Uso: python3 -I integrar_oitavo_aparelho.py <artigo.tex>
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


def trocar_todas(rotulo, antigo, novo, esperado):
    global t
    padrao = r"\s+".join(re.escape(p) for p in antigo.split())
    achados = len(re.findall(padrao, t))
    if achados != esperado:
        sys.exit("FALHOU em %s: %d ocorrencias, esperava %d"
                 % (rotulo, achados, esperado))
    t = re.sub(padrao, lambda _: novo, t)
    feito.append(rotulo)


def trocar_fluido(rotulo, antigo, novo):
    global t
    padrao = r"\s+".join(re.escape(p) for p in antigo.split())
    if len(re.findall(padrao, t)) != 1:
        sys.exit("FALHOU em %s: %d ocorrencias\n  %r"
                 % (rotulo, len(re.findall(padrao, t)), antigo[:90]))
    t = re.sub(padrao, lambda _: novo, t, count=1)
    feito.append(rotulo)


# ================================================ apresentacao do conjunto
trocar_fluido(
    "apresentacao do conjunto de aparelhos",
    "A Tabela~\\ref{tab:aparelhos} apresenta os sete aparelhos em que foi "
    "conduzida a coleta",
    "A Tabela~\\ref{tab:aparelhos} apresenta os oito aparelhos em que foi\n"
    "conduzida a coleta",
)

trocar_fluido(
    "pares de aparelhos",
    "Dois pares de aparelhos compartilham o mesmo identificador de "
    "\\textit{hardware} ou o mesmo fornecedor com modelos distintos, o que "
    "permite distinguir o que decorre do fornecedor do que decorre do "
    "aparelho.",
    """Três aparelhos
compartilham o mesmo identificador de \\textit{hardware}, dois deles
compartilham também o mesmo \\ac{SoC} segundo a especificação do fabricante e
outros compartilham o fornecedor com modelos distintos, o que permite
distinguir o que decorre do \\textit{chipset} do que decorre do aparelho.""",
)

# ================================================ razoes entre delegates
trocar_fluido(
    "sentido do efeito e faixa de ganho",
    "\\textit{delegate} \\ac{GPU} é o mesmo nos sete aparelhos. O YOLOv8n é "
    "acelerado em todas as plataformas, por fator entre 1,48 e 7,28,",
    "\\textit{delegate} \\ac{GPU} é o mesmo nos oito aparelhos. O YOLOv8n é\n"
    "acelerado em todas as plataformas, por fator entre 1,07 e 7,28,",
)

trocar_fluido(
    "amplitude da magnitude do ganho",
    "A magnitude do ganho varia por fator superior a quatro entre o maior e o "
    "menor valor observado e acompanha a faixa de desempenho do aparelho,",
    """A magnitude do ganho varia por fator superior a seis entre o
maior e o menor valor observado, de 1,07 a 7,28, e acompanha a faixa de
desempenho do aparelho,""",
)

# ================================================ mesmo SoC, aparelhos distintos
trocar_fluido(
    "comparacao entre aparelhos de mesmo SoC",
    "decorre da cobertura de operações do \\textit{delegate} e não de "
    "característica do aparelho de referência.",
    """decorre da cobertura de operações do \\textit{delegate} e não
de característica do aparelho de referência.

O Redmi~13C e o Redmi Note~9 empregam o mesmo \\ac{SoC}, o Helio~G85, e
executam versões distintas do Android, 15 e 12. A comparação entre os dois
separa o que decorre do \\textit{chipset} do que decorre do restante da
plataforma. A latência do YOLOv8n \\ac{FP32} em \\ac{GPU} é de 515,1~ms no
primeiro e de 514,5~ms no segundo, diferença de 0,1\\%. Na mesma configuração
em \\ac{CPU}, os valores são de 902,8~ms e 1.076,1~ms, de modo que o segundo é
19,2\\% mais lento. No YOLOv10n \\ac{FP32} em \\ac{GPU}, em que o grafo é
particionado entre os dois processadores, a distância alcança fator de 2,25. O
\\ac{SoC} compartilhado reproduz, portanto, a latência do trecho que o
\\textit{delegate} executa por inteiro, ao passo que as demais configurações
permanecem sensíveis ao aparelho e à versão do sistema.""",
)

# ================================================ concordancia das deteccoes
trocar_fluido(
    "par de concordancias",
    "imagem, perfazendo 310 concordâncias em 321 comparações.",
    "imagem, perfazendo 312 concordâncias em 323 comparações.",
)

trocar_fluido(
    "imagens comuns aos aparelhos",
    "das 26 imagens comuns aos sete aparelhos apresentam contagens distintas,",
    "das 26 imagens comuns aos oito aparelhos apresentam contagens distintas,",
)

trocar_fluido(
    "contagens identicas em CPU",
    "que a mesma quantização executada em \\ac{CPU} produz contagens idênticas "
    "nos sete aparelhos.",
    """que a mesma quantização executada em \\ac{CPU} produz contagens
idênticas nos oito aparelhos.""",
)

trocar_fluido(
    "total acumulado nas 26 imagens",
    "é de 275 detecções em todos os sete aparelhos,",
    "é de 275 detecções em todos os oito aparelhos,",
)

# ================================================ dispersao
trocar_fluido(
    "dispersao nos demais aparelhos",
    "Nos seis demais a relação se inverte,",
    "Nos sete demais a relação se inverte,",
)

# ================================================ resumo, abstract, conclusao
trocar_fluido(
    "resumo",
    "A avaliação foi então estendida a sete aparelhos de três fornecedores",
    "A avaliação foi então estendida a oito aparelhos de três fornecedores",
)

trocar_fluido(
    "abstract",
    "The evaluation was then extended to seven devices from three",
    "The evaluation was then extended to eight devices from three",
)

trocar_fluido(
    "conclusao, extensao da avaliacao",
    "A extensão da avaliação a sete aparelhos, descrita na "
    "Subseção~\\ref{sec:multidispositivo}, verificou o alcance desse "
    "resultado.",
    """A extensão da avaliação a oito aparelhos, descrita na
Subseção~\\ref{sec:multidispositivo}, verificou o alcance desse resultado.""",
)

trocar_todas(
    "faixa de ganho no resumo e na conclusao",
    "com aceleração do YOLOv8n por fator entre 1,48 e 7,28",
    "com aceleração do YOLOv8n por fator entre 1,07 e 7,28",
    2,
)

trocar_fluido(
    "conclusao, amplitude",
    "A magnitude, por outro lado, varia por fator superior a quatro entre as "
    "plataformas,",
    """A magnitude, por outro lado, varia por fator superior a seis entre as
plataformas,""",
)

io.open(caminho, "w", encoding="utf-8").write(t)
for f in feito:
    print("ok  %s" % f)
print("\n%d trocas, %s gravado" % (len(feito), caminho))
