"""Alinha titulo, resumo, abstract e objetivo ao escopo executado.

O orientador aprovou a retirada de "maturacao" do titulo. A deteccao foi
conduzida com classe unica, de modo que o trabalho localiza frutos sem
determinar o estagio de cada um, e o titulo, o resumo, o abstract e o
objetivo geral passam a dizer isso. A motivacao permanece a avaliacao da
maturacao, agora declarada como tal e nao como entrega.

Com o titulo alinhado, a subsecao que justifica a delimitacao deixa de
precisar da terceira razao, que era de escopo e respondia a diferenca
entre titulo e conteudo.

Acrescenta tres correcoes apontadas na revisao. A derivacao das 323
comparacoes passa a constar. A afirmacao de que sensores termicos exigem
permissao privilegiada e incorreta para a temperatura da bateria, que e
acessivel por interface publica, e passa a distinguir os dois casos. E o
pico de memoria sai da justificativa da recomendacao, uma vez que a
propria secao de resultados registra que a medida nao isola o
interpretador.

Uso: python3 -I alinhar_titulo_e_escopo.py <artigo.tex>
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


# =================================================== titulo
trocar(
    "titulo",
    "\\titulo{Desempenho e Estabilidade de Modelos YOLO para Detecção da "
    "Maturação de Frutos de Café em \\textit{Smartphones}: comparação entre "
    "\\textit{delegates} TFLite}",
    "\\titulo{Desempenho e Estabilidade de Modelos YOLO para Detecção de "
    "Frutos de Café em \\textit{Smartphones}: comparação entre "
    "\\textit{delegates} TFLite}",
)

# =================================================== resumo
trocar(
    "resumo, escopo",
    "visando à detecção da maturação de frutos de café em dispositivos "
    "móveis.",
    "visando à detecção de frutos de café em dispositivos móveis.",
)

trocar(
    "resumo, delimitacao ao final",
    "A configuração recomendada para a aplicação é o YOLOv8n em FP16 com "
    "\\textit{delegate} de processador gráfico.",
    "A configuração recomendada para a aplicação é o YOLOv8n em FP16 com "
    "\\textit{delegate} de processador gráfico. A detecção foi conduzida com "
    "classe única, de modo que a classificação do estágio de maturação a "
    "partir dos frutos detectados constitui continuidade e não integra o "
    "escopo deste trabalho.",
)

# =================================================== abstract
trocar(
    "abstract, escopo",
    "detection models converted to TensorFlow Lite for the detection of "
    "coffee fruit ripeness on mobile devices.",
    """detection models converted to TensorFlow Lite for the detection of
    coffee fruits on mobile devices.""",
)

trocar(
    "abstract, delimitacao ao final",
    "The recommended configuration for the application is YOLOv8n in FP16 "
    "with the GPU delegate.",
    """The recommended configuration for the application is YOLOv8n in FP16
    with the GPU delegate. Detection was carried out with a single class, so
    classifying the ripeness stage of the detected fruits is left as
    continuation and is outside the scope of this work.""",
)

# =================================================== introducao e objetivo
trocar(
    "introducao, proposta",
    "visando à detecção da maturação de frutos de café em",
    "visando à detecção de frutos de café em",
)

trocar(
    "objetivo geral",
    "executados por meio do \\ac{TFLite} para a detecção da maturação de "
    "frutos de café em \\textit{smartphones} Android.",
    """executados por meio do \\ac{TFLite} para a detecção de frutos de café em
\\textit{smartphones} Android. A detecção é conduzida com classe única, de
modo que localiza os frutos sem determinar o estágio de maturação de cada um,
etapa que permanece como continuidade.""",
)

# =================================================== derivacao das comparacoes
trocar(
    "derivacao das comparacoes",
    "imagem, perfazendo 312 concordâncias em 323 comparações.",
    """imagem, perfazendo 312 concordâncias em 323 comparações. O total de
comparações é a soma, sobre as onze configurações, das imagens presentes em
todos os aparelhos, uma vez que cada imagem produz uma comparação entre os
oito aparelhos. As configurações diferem quanto ao número de imagens comuns
porque medições descartadas não entram na comparação, conforme a
Subseção~\\ref{sec:coleta_multidispositivo}.""",
)

# =================================================== temperatura
trocar(
    "acesso a temperatura",
    "Registra-se que a temperatura do dispositivo não pôde ser incorporada ao "
    "conjunto de métricas coletadas automaticamente. As interfaces de acesso "
    "a sensores térmicos no sistema Android requerem permissões de nível "
    "privilegiado, não disponíveis a aplicações comuns, e não são expostas "
    "pelo \\textit{framework} utilizado.",
    """Registra-se que a temperatura do dispositivo não foi incorporada ao
conjunto de métricas coletadas automaticamente. A temperatura da bateria é
acessível a aplicações comuns por interface pública do sistema, ao passo que a
temperatura do \\ac{SoC}, que seria o indicador direto de limitação térmica,
não é exposta. A primeira não foi coletada porque a aplicação já estava em uso
pelos voluntários quando a necessidade se mostrou, e constitui instrumentação
a incluir em coletas futuras.""",
)

# =================================================== memoria na recomendacao
trocar(
    "memoria fora da recomendacao, resultados",
    "saída equivalente à do modelo em precisão plena e o menor pico de "
    "memória entre todas as configurações medidas.",
    "saída equivalente à do modelo em precisão plena.",
)

trocar(
    "memoria fora da recomendacao, conclusao",
    "saída equivalente à da variante em precisão plena e o menor pico de "
    "memória entre as configurações avaliadas.",
    "saída equivalente à da variante em precisão plena.",
)

# =================================================== 5.4 condensada
trocar(
    "5.4, motivacao em lugar de problema declarado",
    "Cabe expor a razão dessa delimitação, uma vez que o problema de origem, "
    "enunciado na Seção~\\ref{sec:introducao}, é a avaliação da maturação.",
    """Cabe expor a razão dessa delimitação, uma vez que a motivação do
trabalho, enunciada na Seção~\\ref{sec:introducao}, é a avaliação da
maturação.""",
)

trocar(
    "5.4, terceira razao removida",
    "A terceira razão é de escopo. O objeto declarado deste trabalho é a "
    "comparação entre \\textit{delegates} do \\ac{TFLite} quanto a desempenho "
    "e estabilidade, e essa comparação não depende do número de classes do "
    "modelo. A classe única mantém o problema de detecção estável enquanto "
    "variam arquitetura, precisão numérica e mecanismo de aceleração, que são "
    "os fatores sob exame.",
    """A classe única mantém ainda o problema de detecção estável enquanto
variam arquitetura, precisão numérica e mecanismo de aceleração, que são os
fatores sob exame.""",
)

io.open(caminho, "w", encoding="utf-8").write(t)
for f in feito:
    print("ok  %s" % f)
print("\n%d trocas, %s gravado" % (len(feito), caminho))
