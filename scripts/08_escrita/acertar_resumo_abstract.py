"""Alinha resumo e abstract aos valores do capitulo de resultados.

A integracao do oitavo aparelho alterou o menor ganho do delegate GPU no
YOLOv8n, de 1,48 para 1,07, e a razao entre o maior e o menor ganho, que
passou a superar seis. O abstract ficou com os valores antigos e o resumo
com a razao antiga, de modo que os tres textos discordavam entre si.

Acrescenta tambem o alcance da leitura sobre compatibilidade entre
operacoes e acelerador, que e inferida de duas arquiteturas, um delegate
e oito aparelhos, para que nao se leia como regra geral.

Uso: python3 -I acertar_resumo_abstract.py <artigo.tex>
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


trocar(
    "resumo, amplitude da magnitude",
    "ao passo que a magnitude varia por fator superior a quatro entre as "
    "plataformas.",
    "ao passo que a magnitude varia por fator superior a seis entre as "
    "plataformas.",
)

trocar_fluido(
    "abstract, faixa de ganho e amplitude",
    "with YOLOv8n accelerated by a factor between 1.48 and 7.28 and no gain "
    "for YOLOv10n, whereas the magnitude varies by a factor greater than "
    "four across platforms.",
    """with YOLOv8n accelerated by a factor between 1.07 and 7.28 and no gain
    for YOLOv10n, whereas the magnitude varies by a factor greater than
    six across platforms.""",
)

trocar_fluido(
    "alcance da leitura sobre compatibilidade",
    "mas a compatibilidade entre as operações que ele emprega e aquelas que o "
    "acelerador implementa.",
    """mas a compatibilidade entre as operações que ele emprega e aquelas que o
acelerador implementa. O alcance dessa leitura é o das condições examinadas,
duas arquiteturas, um \\textit{delegate} e oito aparelhos. O que os dados
sustentam é o mecanismo, segundo o qual operações não cobertas pelo acelerador
forçam o particionamento do grafo e anulam o ganho obtido nos segmentos
delegados. Verificar se a mesma leitura se estende a outras arquiteturas, a
outros aceleradores e a outras implementações exige medição própria.""",
)

io.open(caminho, "w", encoding="utf-8").write(t)
for f in feito:
    print("ok  %s" % f)
print("\n%d trocas, %s gravado" % (len(feito), caminho))
