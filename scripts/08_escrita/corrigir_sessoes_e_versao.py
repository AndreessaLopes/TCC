"""Acerta o relato das sessoes repetidas e a versao do sistema.

A Tabela 16 foi regerada quando a quarta sessao entrou, mas o texto ao
redor ficou com os numeros de quando eram tres. A auditoria dos arquivos
de medicao mostra que o aparelho de referencia tem cinco sessoes, uma
sob Android 16, de 13 de outubro, e quatro sob Android 17, de 19 e 21 de
outubro, e que a tabela usa as quatro da versao mais recente.

Tres valores do texto nao correspondiam a tabela. A maior amplitude e de
38,0% e ocorre no YOLOv8n em FP16 com delegate de CPU, e nao 32,1% em
INT8 com GPU. A faixa das execucoes em CPU e de 3,7% a 38,0%, e nao de
2,3% a 24,2%. A faixa em GPU termina em 32,0%.

Com os valores corretos, a leitura de que a variacao entre execucoes
acompanha a menor estabilidade do delegate GPU deixa de se sustentar,
uma vez que a maior amplitude esta em CPU. A frase passa a registrar que
essa medida nao separa os dois delegates.

A contradicao entre Android 16, declarado na descricao do aparelho, e
Android 17, registrado na tabela de aparelhos, decorre de atualizacao do
sistema entre as duas coletas e passa a constar.

Uso: python3 -I corrigir_sessoes_e_versao.py <artigo.tex>
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


# ------------------------------------------- metodologia, sessoes repetidas
trocar(
    "metodologia, numero e condicoes das sessoes",
    "No aparelho de referência a varredura foi repetida em três sessões "
    "realizadas na mesma noite, com intervalos de 40 e 46~minutos entre elas "
    "e carga entre 99\\% e 83\\%, com a finalidade de estimar a variação entre "
    "execuções de uma mesma configuração.",
    """No aparelho de referência a varredura foi repetida em quatro
sessões, três delas na mesma noite, com intervalos de 40 e 46~minutos entre os
respectivos inícios, e uma conduzida dois dias antes, com carga entre 100\\% e
83\\% ao longo das quatro, com a finalidade de estimar a variação entre
execuções de uma mesma configuração. Uma sessão anterior, executada antes da
atualização do sistema operacional do aparelho, ficou de fora dessa
comparação, para que as quatro consideradas se refiram à mesma versão.""",
)

# ------------------------------------------- versao do sistema do aparelho
trocar(
    "atualizacao do sistema no aparelho de referencia",
    "e sistema operacional Android~16.",
    """e sistema operacional Android~16. O aparelho foi atualizado para o
Android~17 entre a avaliação sobre o conjunto completo e a coleta em múltiplos
dispositivos, de modo que a Tabela~\\ref{tab:aparelhos} registra a versão
vigente durante esta última.""",
)

# ------------------------------------------- resultados, amplitude maxima
trocar(
    "resultados, numero de sessoes e amplitude maxima",
    "A variação da latência de inferência entre as três sessões realizadas no "
    "aparelho de referência consta da Tabela~\\ref{tab:sessoes}. A amplitude "
    "entre a maior e a menor média obtidas para a mesma configuração "
    "corresponde a 18,6\\% da média na mediana das onze configurações e "
    "alcança 32,1\\% no YOLOv8n em \\ac{INT8} com \\textit{delegate} \\ac{GPU}.",
    """A variação da latência de inferência entre as quatro sessões
realizadas no aparelho de referência consta da Tabela~\\ref{tab:sessoes}. A
amplitude entre a maior e a menor média obtidas para a mesma configuração
corresponde a 18,6\\% da média na mediana das onze configurações e alcança
38,0\\% no YOLOv8n em \\ac{FP16} com \\textit{delegate} de \\ac{CPU}.""",
)

# ------------------------------------------- resultados, faixas por delegate
trocar(
    "resultados, faixas por delegate",
    "As configurações executadas em \\ac{CPU} apresentam amplitude entre "
    "2,3\\% e 24,2\\%, ao passo que as executadas em \\ac{GPU} situam-se entre "
    "7,3\\% e 32,1\\%, o que é coerente com a menor estabilidade do "
    "\\textit{delegate} \\ac{GPU} registrada na Subseção~\\ref{sec:estabilidade}.",
    """As configurações executadas em \\ac{CPU} apresentam amplitude entre
3,7\\% e 38,0\\%, ao passo que as executadas em \\ac{GPU} situam-se entre
7,3\\% e 32,0\\%. A variação entre execuções não separa, portanto, os dois
\\textit{delegates}, ao contrário da dispersão medida dentro de uma única
execução, registrada na Subseção~\\ref{sec:estabilidade}.""",
)

# ------------------------------------------- limitacoes
trocar(
    "limitacoes, amplitude maxima",
    "na mediana das onze configurações e alcança 32,1\\%",
    "na mediana das onze configurações e alcança 38,0\\%",
)

io.open(caminho, "w", encoding="utf-8").write(t)
for f in feito:
    print("ok  %s" % f)
print("\n%d trocas, %s gravado" % (len(feito), caminho))
