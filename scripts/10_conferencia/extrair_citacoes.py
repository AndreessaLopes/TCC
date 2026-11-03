"""Lista as frases do texto que trazem citacao.

A conferencia de citacoes pergunta, para cada frase citada, se a obra
sustenta o que a frase afirma. O primeiro passo e saber quais sao as
frases e quais obras cada uma invoca.

Percorre o fonte fora do preambulo, separa o texto em frases e, para
cada frase que traga comando de citacao, registra a secao em que esta, a
linha, a frase e as chaves invocadas. Comandos cobertos: \\cite,
\\textcite, \\parencite, \\citeonline e \\citefonte, com ou sem
argumento opcional.

Uso: python3 -I extrair_citacoes.py <artigo.tex> <saida.json>
"""
import io
import json
import re
import sys

entrada, saida = sys.argv[1], sys.argv[2]
texto = io.open(entrada, encoding="utf-8").read()

# O corpo comeca em \begin{document}; o preambulo traz resumo e abstract,
# que tambem valem a conferencia, de modo que ficam incluidos.
inicio = texto.find("\\begin{document}")
if inicio < 0:
    sys.exit("FALHOU: nao achei \\begin{document}")

CITACAO = re.compile(
    r"\\(cite|textcite|parencite|citeonline|citefonte|citeauthor|citeyear)"
    r"(?:\[[^\]]*\])*\{([^}]*)\}")
SECAO = re.compile(r"\\(section|subsection|subsubsection)\*?\{([^}]*)\}")

linhas = texto.split("\n")
secao_atual = "preâmbulo"
registros = []

# Reconstroi o texto mantendo a linha de origem de cada caractere.
for numero, linha in enumerate(linhas, start=1):
    m = SECAO.search(linha)
    if m:
        secao_atual = re.sub(r"\\[a-zA-Z]+|[{}]", "", m.group(2)).strip()
        continue
    if linha.lstrip().startswith("%"):
        continue
    if not CITACAO.search(linha):
        continue
    # Divide em frases por ponto final seguido de espaco ou fim de linha,
    # preservando as abreviacoes mais comuns do texto.
    protegido = linha
    for abrev in ("Dr.", "Prof.", "Fig.", "p.", "al.", "Inc.", "Ltd."):
        protegido = protegido.replace(abrev, abrev.replace(".", "\x00"))
    partes = re.split(r"(?<=\.)\s+", protegido)
    for parte in partes:
        frase = parte.replace("\x00", ".").strip()
        chaves = []
        for m in CITACAO.finditer(frase):
            for k in m.group(2).split(","):
                k = k.strip()
                if k and k not in chaves:
                    chaves.append(k)
        if chaves:
            registros.append({"id": "", "secao": secao_atual,
                              "linha": numero, "frase": frase,
                              "chaves": chaves})

for i, r in enumerate(registros, start=1):
    r["id"] = "f%03d" % i

io.open(saida, "w", encoding="utf-8").write(
    json.dumps(registros, ensure_ascii=False, indent=2))

pares = sum(len(r["chaves"]) for r in registros)
print("%d frases com citacao, %d pares frase e obra" % (len(registros), pares))
print("gravado %s" % saida)

print("\npor secao:")
contagem = {}
for r in registros:
    contagem[r["secao"]] = contagem.get(r["secao"], 0) + len(r["chaves"])
for s in sorted(contagem, key=lambda x: -contagem[x]):
    print("  %-44s %3d" % (s[:44], contagem[s]))

print("\npor obra:")
por_obra = {}
for r in registros:
    for k in r["chaves"]:
        por_obra[k] = por_obra.get(k, 0) + 1
for k in sorted(por_obra, key=lambda x: (-por_obra[x], x)):
    print("  %-32s %3d" % (k, por_obra[k]))
