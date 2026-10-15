"""Confere o artigo contra o checklist da regra 15 do guia de escrita.

As regras foram aplicadas em 8 de outubro. Depois disso o documento
mudou: a classe passou a ``frutos'', tres figuras de bibliometria foram
regeradas, as duas curvas de precisao e revocacao viraram uma, a figura
de anotacao foi trocada e paragrafos foram reescritos. Este script
reexamina o que e verificavel por leitura do fonte, para que o texto novo
nao escape ao que ja estava conferido.

O que nao da para verificar assim fica de fora e esta nomeado no fim da
saida, para nao passar por conferido.

Uso: python3 -I conferir_regras.py <artigo.tex> [referencias.bib]
"""
import io
import os
import re
import sys
import unicodedata

caminho = sys.argv[1]
bib = sys.argv[2] if len(sys.argv) > 2 else None
texto = io.open(caminho, encoding="utf-8").read()

linhas = texto.split("\n")

# Tres figuras do referencial sao TikZ e vivem em arquivos proprios,
# trazidos por \input. Os rotulos delas estao la, nao aqui.
INCLUIDOS = ""
for inc in re.findall(r"\\input\{([^}]+)\}", texto):
    alvo = os.path.join(os.path.dirname(caminho), inc)
    if not alvo.endswith(".tex"):
        alvo += ".tex"
    if os.path.exists(alvo):
        INCLUIDOS += io.open(alvo, encoding="utf-8").read() + "\n"

# O corpo comeca em \begin{document}; antes disso e preambulo, onde
# dois-pontos e chaves fazem parte da sintaxe.
inicio = next(i for i, l in enumerate(linhas) if "\\begin{document}" in l)

ACHADOS = []


def anotar(regra, titulo, casos, limite=8):
    ACHADOS.append((regra, titulo, casos, limite))


def sem_comentario(linha):
    # Um % escapado (\%) nao abre comentario.
    saida, i = [], 0
    while i < len(linha):
        if linha[i] == "\\" and i + 1 < len(linha):
            saida.append(linha[i:i + 2]); i += 2; continue
        if linha[i] == "%":
            break
        saida.append(linha[i]); i += 1
    return "".join(saida)


def tirar_comandos(s):
    """Remove os argumentos de comandos que nao sao corpo de texto."""
    # Os de dois argumentos vem primeiro: tirar so o nome do comando
    # deixaria o segundo grupo solto, e \renewcommand{\arraystretch}{1,3}
    # passaria por numero de prosa com separador errado.
    s = re.sub(r"\\(?:resizebox|scalebox)\{[^{}]*\}\{[^{}]*\}", " ", s)
    s = re.sub(r"\\renewcommand\{[^{}]*\}\{[^{}]*\}", " ", s)
    for cmd in ("label", "ref", "cite", "textcite", "citeonline", "autocite",
                "includegraphics", "input", "acrodef", "ac", "acs", "acl",
                "url", "href", "figuraHorizontal", "figuraMedia",
                "figuraVertical", "figuraReferencialHorizontal", "legend",
                "caption", "usepackage", "documentclass", "bibliography",
                "addbibresource", "DeclareAcronym", "newcommand",
                "renewcommand", "setlength", "definecolor", "node",
                "draw", "path", "coordinate", "pgfplotstableread",
                "arraystretch", "resizebox", "scalebox", "includepdf",
                "setstretch", "vspace", "hspace", "columnwidth"):
        s = re.sub(r"\\" + cmd + r"\*?(\[[^\]]*\])?\{[^{}]*\}", " ", s)
    # \resizebox{0.94\textwidth}{!}{...} e \renewcommand{\arraystretch}{1.3}
    # deixam fatores decimais soltos, que nao sao numeros de prosa.
    s = re.sub(r"\\(?:resizebox|scalebox)\{[^{}]*\}\{[^{}]*\}", " ", s)
    s = re.sub(r"\\renewcommand\{[^{}]*\}\{[^{}]*\}", " ", s)
    s = re.sub(r"\\[a-zA-Z@]+\*?", " ", s)
    return s


# Regioes a ignorar no corpo: tikzpicture, tabular, lstlisting, verbatim.
AMBIENTES_TECNICOS = ("tikzpicture", "tabular", "lstlisting", "verbatim",
                      "pgfplots", "axis", "scope", "equation", "align",
                      "thebibliography")


def corpo_de_prosa():
    """Devolve (numero da linha, texto) das linhas de prosa corrida."""
    saida, pilha = [], []
    for n in range(inicio + 1, len(linhas)):
        bruta = sem_comentario(linhas[n])
        abre = re.findall(r"\\begin\{([a-zA-Z*]+)\}", bruta)
        fecha = re.findall(r"\\end\{([a-zA-Z*]+)\}", bruta)
        tecnico_na_linha = any(a.rstrip("*") in AMBIENTES_TECNICOS
                               for a in abre + fecha)
        for a in abre:
            pilha.append(a.rstrip("*"))
        for f in fecha:
            if f.rstrip("*") in pilha:
                pilha.reverse(); pilha.remove(f.rstrip("*")); pilha.reverse()
        if any(p in AMBIENTES_TECNICOS for p in pilha) or tecnico_na_linha:
            continue
        if re.match(r"\s*\\(section|subsection|subsubsection|caption|legend|"
                    r"label|includegraphics|figura|titulo|autor|orientador|"
                    r"palavras|keywords|maketitle|begin|end|item\b)", bruta):
            continue
        if bruta.strip():
            saida.append((n + 1, bruta))
    return saida


PROSA = corpo_de_prosa()

# ------------------------------------------------ 4.1 dois-pontos
casos = []
for n, l in PROSA:
    limpa = tirar_comandos(l)
    for m in re.finditer(r"[^\s:]:(\s|$)", limpa):
        casos.append((n, limpa[max(0, m.start() - 55):m.end() + 15].strip()))
anotar("4.1", "dois-pontos no corpo do texto", casos)

# ------------------------------------------------ 4.2 travessao
casos = [(n, tirar_comandos(l).strip()[:90]) for n, l in PROSA
         if "---" in tirar_comandos(l)]
anotar("4.2", "travessao no corpo do texto", casos)

# ------------------------------------------------ 7.1 vocabulario
VALORATIVOS = (
    r"consideravelmente|substancialmente|significativamente(?! )|"
    r"expressiv[ao]s?|bastante|extremamente|altamente|enormes?|"
    r"gigantescos?|excelentes?|otim[ao]s?|ruins?|p[eé]ssim[ao]s?|"
    r"sever[ao]s?|drastic[ao]|dr[aá]stic[ao]s?|not[aá]ve(l|is)|"
    r"impressionantes?|surpreendentes?|muito|bem (?:superior|inferior)|"
    r"grosseir[ao]s?|elevadissim[ao]|clarament[e]|evidentement[e]|"
    r"obviamente|simplesmente|praticamente|extraordinari[ao]s?"
)
casos = []
for n, l in PROSA:
    limpa = tirar_comandos(l)
    for m in re.finditer(r"\b(" + VALORATIVOS + r")\b", limpa, re.I):
        casos.append((n, limpa[max(0, m.start() - 45):m.end() + 45].strip()))
anotar("7.1", "adjetivo valorativo ou intensificador sem ancoragem", casos)

# ------------------------------------------------ 15 primeira pessoa
PRIMEIRA = (
    r"\beu\b|\bnós\b|\bmeu\b|\bminha\b|\bnosso\b|\bnossa\b|"
    r"\bnossos\b|\bnossas\b|"
    r"\b(?:realiz|observ|apresent|utiliz|desenvolv|propuse|constru|"
    r"implement|avali|conclu|verific|analis|mediu?|mostr|adot|defin|"
    r"escolh|test)(?:amos|ei|o)\b"
)
casos = []
for n, l in PROSA:
    limpa = tirar_comandos(l)
    for m in re.finditer(PRIMEIRA, limpa, re.I):
        trecho = limpa[max(0, m.start() - 40):m.end() + 40].strip()
        casos.append((n, trecho))
anotar("15", "primeira pessoa", casos)

# ------------------------------------------------ 13 marcador pendente
casos = [(n + 1, l.strip()[:90]) for n, l in enumerate(linhas)
         if re.search(r"\[PREENCHER\]|\bTODO\b|\bFIXME\b|XXX|\?\?\?", l)]
anotar("13", "marcador pendente", casos)

# ------------------------------------------------ 16 fios verticais
casos = []
for n, l in enumerate(linhas):
    m = re.search(r"\\begin\{tabular\}(\[[^\]]*\])?\{([^}]*)\}", l)
    if m and "|" in m.group(2):
        casos.append((n + 1, m.group(0)[:80]))
anotar("16", "fio vertical em tabela", casos)

# ------------------------------------------------ 17 aspas retas
casos = []
for n in range(inicio + 1, len(linhas)):
    l = sem_comentario(linhas[n])
    if '"' in l:
        casos.append((n + 1, l.strip()[:90]))
anotar("17", "aspas retas", casos)

# ------------------------------------------------ 11 separador decimal
casos = []
for n, l in PROSA:
    limpa = tirar_comandos(l)
    for m in re.finditer(r"\d+\.\d", limpa):
        trecho = limpa[max(0, m.start() - 35):m.end() + 35].strip()
        # 1.410 e 3.401 sao milhares, grafia correta em portugues.
        if re.match(r"^\d{1,3}\.\d{3}(\D|$)", limpa[m.start():]):
            continue
        casos.append((n, trecho))
anotar("11", "separador decimal com ponto", casos)

# ------------------------------------------------ 15 til antes de \ref
casos = []
for n in range(inicio + 1, len(linhas)):
    l = sem_comentario(linhas[n])
    for m in re.finditer(r"(.)\\(?:ref|autoref)\{", l):
        if m.group(1) not in "~({[-":
            casos.append((n + 1, l[max(0, m.start() - 45):m.end() + 25].strip()))
anotar("15", "falta til antes de \\ref", casos)

# ------------------------------------------------ 10 legenda e fonte
casos = []
for n in range(inicio + 1, len(linhas)):
    l = sem_comentario(linhas[n]).strip()
    m = re.match(r"\\caption\{(.*)\}\s*$", l)
    if m and m.group(1).rstrip().endswith("."):
        casos.append((n + 1, l[:90]))
anotar("10", "legenda terminada em ponto", casos)

# fonte abaixo: todo flutuante precisa de \legend
casos = []
flut = None
for n in range(inicio + 1, len(linhas)):
    l = sem_comentario(linhas[n])
    m = re.search(r"\\begin\{(figure|table|board)\}", l)
    if m:
        flut = (n + 1, m.group(1), [])
    elif flut:
        flut[2].append(l)
        if re.search(r"\\end\{" + flut[1] + r"\}", l):
            bloco = "\n".join(flut[2])
            if "\\legend" not in bloco:
                casos.append((flut[0], "%s sem \\legend" % flut[1]))
            # legenda antes do conteudo
            pos_cap = bloco.find("\\caption")
            pos_leg = bloco.find("\\legend")
            if 0 <= pos_leg < pos_cap:
                casos.append((flut[0], "%s com fonte antes da legenda" % flut[1]))
            flut = None
anotar("10", "flutuante sem fonte ou com fonte fora de lugar", casos)

# ------------------------------------------------ 9 label e referencia
rotulos, refs = {}, set()
for n in range(inicio + 1, len(linhas)):
    l = sem_comentario(linhas[n])
    for m in re.finditer(r"\\label\{([^}]+)\}", l):
        rotulos[m.group(1)] = n + 1
    for m in re.finditer(r"\\(?:ref|autoref)\{([^}]+)\}", l):
        refs.add(m.group(1))
for m in re.finditer(r"\\label\{([^}]+)\}", INCLUIDOS):
    rotulos.setdefault(m.group(1), 0)
casos = [(v, k) for k, v in sorted(rotulos.items(), key=lambda t: t[1])
         if k not in refs and not k.startswith(("sec:", "cap:", "subsec:"))]
anotar("9", "rotulo nunca referenciado", casos)
casos = [(0, r) for r in sorted(refs - set(rotulos))]
anotar("9", "referencia sem rotulo", casos)

# flutuante sem label
casos = []
for n in range(inicio + 1, len(linhas)):
    l = sem_comentario(linhas[n])
    m = re.search(r"\\begin\{(figure|table|board)\}", l)
    if m:
        bloco = "\n".join(linhas[n:n + 40])
        fim = re.search(r"\\end\{" + m.group(1) + r"\}", bloco)
        if fim:
            bloco = bloco[:fim.end()]
        if "\\label" not in bloco:
            casos.append((n + 1, "%s sem \\label" % m.group(1)))
anotar("9", "flutuante sem rotulo", casos)

# ------------------------------------------------ 5 italico indevido
PROPRIOS = ("TensorFlow Lite", "Scopus", "Pandas", "Matplotlib", "NetworkX",
            "nnPerf", "SavedModel", "Faster R-CNN", "tflite\\_flutter",
            "Ultralytics", "Flutter", "Android", "Dart", "Python", "OpenCV",
            "Roboflow", "Overleaf", "Netron")
casos = []
for n in range(inicio + 1, len(linhas)):
    l = sem_comentario(linhas[n])
    for m in re.finditer(r"\\textit\{([^{}]*)\}", l):
        dentro = m.group(1).strip()
        for p in PROPRIOS:
            if p.lower() == dentro.lower():
                casos.append((n + 1, "\\textit{%s}" % dentro))
anotar("5", "nome proprio em italico", casos)

# ------------------------------------------------ 14 recall / revocacao
casos = []
for n, l in PROSA:
    limpa = tirar_comandos(l)
    # A regra 14 admite uma glosa, na primeira ocorrencia: "revocacao
    # (\textit{recall})". So se conta o que estiver fora dela.
    fora = re.sub(r"revoca\u00e7\u00e3o\s*\(\s*\\textit\{recall\}\s*\)", " ", l)
    fora = tirar_comandos(fora)
    for m in re.finditer(r"\brecall\b", fora, re.I):
        casos.append((n, fora[max(0, m.start() - 50):m.end() + 30].strip()))
glosas = sum(1 for n in range(inicio + 1, len(linhas))
             if re.search(r"\\textit\{recall\}", sem_comentario(linhas[n])))
anotar("14", "\"recall\" fora da glosa (%d glosa(s) em \\textit)" % glosas,
       casos)

# ------------------------------------------------ 26 numero e unidade
UNID = (r"ms|s|MB|GB|KB|kB|MiB|px|pixels|FPS|fps|%|mAP|GHz|MHz|nm|mm|cm|m|"
        r"kg|g|W|mAh|bits?|bytes?")
casos = []
for n, l in PROSA:
    limpa = tirar_comandos(l)
    for m in re.finditer(r"(\d(?:[.,]\d+)?) (" + UNID + r")\b", limpa):
        casos.append((n, limpa[max(0, m.start() - 35):m.end() + 20].strip()))
anotar("26", "numero e unidade sem til", casos)

# ------------------------------------------------ 6 siglas
casos = []
for n in range(inicio + 1, len(linhas)):
    l = sem_comentario(linhas[n])
    # expansao antes da sigla, padrao que a regra 6.4 inverte
    for m in re.finditer(r"\\textit\{([A-Z][^{}]{4,60})\}\s*\(([A-Z]{2,8})\)", l):
        casos.append((n + 1, m.group(0)[:85]))
anotar("6.4", "expansao antes da sigla", casos)

# ------------------------------------------------ bibliografia citada
if bib:
    fonte = io.open(bib, encoding="utf-8").read()
    chaves = set(re.findall(r"@\w+\{([^,]+),", fonte))
    citadas = set()
    for n in range(inicio + 1, len(linhas)):
        l = sem_comentario(linhas[n])
        for m in re.finditer(r"\\[a-zA-Z]*cite[a-zA-Z]*\*?(\[[^\]]*\])*"
                             r"\{([^}]+)\}", l):
            for c in m.group(2).split(","):
                citadas.add(c.strip())
    anotar("15", "entrada da bibliografia nunca citada",
           [(0, c) for c in sorted(chaves - citadas)])
    anotar("15", "citacao sem entrada na bibliografia",
           [(0, c) for c in sorted(citadas - chaves)])

# ------------------------------------------------ 10 paragrafo de uma frase
casos = []
bloco, primeira_linha = [], None
for n, l in PROSA + [(0, "")]:
    if l.strip() and n:
        if primeira_linha is None:
            primeira_linha = n
        bloco.append(tirar_comandos(l).strip())
    else:
        if bloco:
            p = " ".join(bloco).strip()
            frases = [f for f in re.split(r"(?<=[.!?])\s+", p) if len(f) > 3]
            if len(frases) == 1 and 20 < len(p) < 300 and \
                    re.search(r"\b(Figura|Tabela|Quadro)\b", p):
                casos.append((primeira_linha, p[:100]))
        bloco, primeira_linha = [], None
# As linhas em branco nao chegam a PROSA, de modo que a deteccao acima
# so pega blocos separados por linha de comando. Refaz por paragrafo real.
casos = []
corpo = "\n".join(sem_comentario(l) for l in linhas[inicio + 1:])
for par in re.split(r"\n\s*\n", corpo):
    p = tirar_comandos(par).strip()
    p = re.sub(r"\s+", " ", p)
    if not p or p.startswith("\\"):
        continue
    frases = [f for f in re.split(r"(?<=[.!?])\s+", p) if len(f) > 3]
    if len(frases) == 1 and 20 < len(p) < 320 and \
            re.search(r"^(A |As |O |Os )?(Figura|Tabela|Quadro)", p):
        casos.append((0, p[:110]))
anotar("10", "paragrafo de uma frase que apenas anuncia ilustracao", casos)

# ------------------------------------------------------------------ saida
largura = 72
print("CONFERENCIA DO CHECKLIST DA REGRA 15")
print("=" * largura)
print("arquivo: %s" % caminho)
print("linhas: %d   corpo a partir da linha %d" % (len(linhas), inicio + 1))
print()

falhas = 0
for regra, titulo, casos, limite in ACHADOS:
    marca = "[ok]  " if not casos else "[!!]  "
    print("%sregra %-5s %s" % (marca, regra, titulo), end="")
    if casos:
        falhas += 1
        print("  — %d" % len(casos))
        for n, trecho in casos[:limite]:
            onde = "linha %-5d" % n if n else "          "
            print("          %s %s" % (onde, trecho))
        if len(casos) > limite:
            print("          ... e mais %d" % (len(casos) - limite))
    else:
        print()
print()
print("=" * largura)
print("%d de %d verificacoes com apontamento" % (falhas, len(ACHADOS)))
print()
print("Nao verificavel por leitura do fonte, continua a cargo de quem le:")
print("  - tempo verbal coerente com o status de cada etapa (regra 15)")
print("  - toda afirmacao nao original citada (regra 15)")
print("  - termo em ingles sempre em italico, caso a caso (regra 5)")
print("  - sigla definida na primeira ocorrencia real (regra 6)")
