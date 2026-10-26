"""Compara, imagem a imagem, o numero de deteccoes entre aparelhos.

O trabalho afirma que em dez das onze configuracoes executaveis o numero
de deteccoes coincide em todos os aparelhos. Este script recalcula essa
contagem a partir dos arquivos de lote, de modo que o numero citado no
texto tenha procedencia.

Para cada configuracao, considera as imagens presentes em todos os
aparelhos e verifica se a contagem de deteccoes coincide em todos eles.
Medicoes descartadas ficam de fora, como na analise ja publicada no
trabalho. Com --com-descartadas elas entram, o que amplia o conjunto
comum, uma vez que o descarte diz respeito ao tempo de execucao e nao a
saida do modelo.

Quando um aparelho tem mais de uma sessao, as sessoes sao conferidas
entre si antes de qualquer comparacao entre aparelhos.

Uso: python3 -I conferir_concordancia.py <pasta multidispositivo> [--com-descartadas] [aparelho a excluir]
"""
import csv
import io
import os
import sys

entrada = sys.argv[1]
argumentos = sys.argv[2:]
com_descartadas = "--com-descartadas" in argumentos
excluir = {a for a in argumentos if not a.startswith("--")}

# ----------------------------------------------- leitura
# contagem[(configuracao, aparelho)][imagem] = numero de deteccoes
contagem = {}
aparelhos = set()

for raiz, _, arquivos in os.walk(entrada):
    for nome in sorted(arquivos):
        if not nome.startswith("lote_") or not nome.endswith(".csv"):
            continue
        caminho = os.path.join(raiz, nome)
        meta, corpo, no_corpo = {}, [], False
        with io.open(caminho, encoding="utf-8") as f:
            for linha in f:
                if linha.startswith("#"):
                    if ":" in linha:
                        k, v = linha[1:].split(":", 1)
                        meta[k.strip()] = v.strip()
                elif linha.startswith("arquivo,"):
                    no_corpo = True
                elif no_corpo and linha.strip():
                    corpo.append(linha.rstrip("\n"))
        apar = meta.get("Aparelho", "?")
        if apar in excluir:
            continue
        aparelhos.add(apar)
        cfg = meta.get("Configuracao", "?")
        por_imagem = {}
        for linha in csv.reader(corpo):
            if len(linha) < 2:
                continue
            if not com_descartadas and len(linha) > 7 and linha[7] == "1":
                continue
            por_imagem[linha[0]] = int(linha[1])
        chave = (cfg, apar)
        if chave in contagem:
            # Sessoes do mesmo aparelho precisam coincidir entre si.
            antes = contagem[chave]
            comuns = set(antes) & set(por_imagem)
            divergentes = [i for i in comuns if antes[i] != por_imagem[i]]
            if divergentes:
                sys.exit("FALHOU: %s em %s diverge entre sessoes em %d imagens"
                         % (cfg, apar, len(divergentes)))
            antes.update(por_imagem)
        else:
            contagem[chave] = por_imagem

# ----------------------------------------------- comparacao
configuracoes = sorted({c for c, _ in contagem})
total_comp = total_conc = 0
print("%-24s %7s %7s %9s %s" % ("configuracao", "imagens", "iguais",
                                "aparelhos", "total de deteccoes"))
divergentes_por_cfg = {}
for cfg in configuracoes:
    meus = {a: v for (c, a), v in contagem.items() if c == cfg}
    if len(meus) < 2:
        continue
    comuns = set.intersection(*(set(v) for v in meus.values()))
    iguais = [i for i in sorted(comuns)
              if len({v[i] for v in meus.values()}) == 1]
    total_comp += len(comuns)
    total_conc += len(iguais)
    divergentes_por_cfg[cfg] = len(comuns) - len(iguais)
    soma = sum(next(iter(meus.values()))[i] for i in sorted(comuns)) \
        if len(comuns) == len(iguais) else None
    print("%-24s %7d %7d %9d %s"
          % (cfg, len(comuns), len(iguais), len(meus),
             soma if soma is not None else "divergente"))

print("\naparelhos considerados: %d  (%s)"
      % (len(aparelhos), ", ".join(sorted(aparelhos))))
print("configuracoes com coincidencia integral: %d de %d"
      % (sum(1 for v in divergentes_por_cfg.values() if v == 0),
         len(divergentes_por_cfg)))
print("concordancias: %d em %d comparacoes" % (total_conc, total_comp))
for cfg, n in divergentes_por_cfg.items():
    if not n:
        continue
    print("  %s diverge em %d imagens" % (cfg, n))
    meus = {a: v for (c, a), v in contagem.items() if c == cfg}
    comuns = sorted(set.intersection(*(set(v) for v in meus.values())))
    for apar in sorted(meus):
        print("    %-12s total de %d deteccoes em %d imagens"
              % (apar, sum(meus[apar][i] for i in comuns), len(comuns)))
