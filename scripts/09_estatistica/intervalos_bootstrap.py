"""Estima incerteza das latencias por reamostragem.

As tabelas de latencia reportam media e desvio sem indicar a precisao da
propria estimativa, e o texto compara configuracoes sem teste. Como cada
execucao registra a latencia de cada imagem, a incerteza da media e a
significancia das diferencas podem ser estimadas a partir dos dados ja
coletados, sem repetir medicao.

O intervalo de confianca da media sai de reamostragem com reposicao sobre
as imagens, com 10.000 reamostras e percentis 2,5 e 97,5. A comparacao
entre delegates usa a razao entre as medias, que e a grandeza reportada
no trabalho, com intervalo obtido por reamostragem conjunta, e um teste
de permutacao sobre a diferenca das medias, com correcao de Holm para as
comparacoes multiplas.

Medicoes descartadas ficam de fora, como nas demais analises de tempo.

Uso: python3 -I intervalos_bootstrap.py <pasta medicoes> <saida.csv>
"""
import csv
import io
import os
import sys

import numpy as np

REAMOSTRAS = 10000
SEMENTE = 20261029

entrada, saida = sys.argv[1], sys.argv[2]
aleatorio = np.random.default_rng(SEMENTE)


def ler(caminho):
    """Devolve (configuracao, vetor de latencias de inferencia)."""
    meta, valores, no_corpo = {}, [], False
    with io.open(caminho, encoding="utf-8", errors="replace") as f:
        leitor = csv.reader(f)
        for linha in leitor:
            if not linha:
                continue
            if linha[0].startswith("#"):
                bruto = ",".join(linha)[1:]
                if ":" in bruto:
                    k, v = bruto.split(":", 1)
                    meta[k.strip()] = v.strip()
                continue
            if linha[0] == "arquivo":
                no_corpo = True
                continue
            if no_corpo and len(linha) > 7 and linha[7] != "1":
                valores.append(float(linha[3]))
    return meta.get("Configuracao", "?"), np.array(valores)


def ic_media(x):
    idx = aleatorio.integers(0, len(x), size=(REAMOSTRAS, len(x)))
    medias = x[idx].mean(axis=1)
    return float(np.percentile(medias, 2.5)), float(np.percentile(medias, 97.5))


def ic_razao(a, b):
    """Intervalo da razao entre as medias de a e de b."""
    ia = aleatorio.integers(0, len(a), size=(REAMOSTRAS, len(a)))
    ib = aleatorio.integers(0, len(b), size=(REAMOSTRAS, len(b)))
    razoes = a[ia].mean(axis=1) / b[ib].mean(axis=1)
    return float(np.percentile(razoes, 2.5)), float(np.percentile(razoes, 97.5))


def p_permutacao(a, b):
    """Teste bilateral sobre a diferenca das medias."""
    juntos = np.concatenate([a, b])
    n = len(a)
    observado = abs(a.mean() - b.mean())
    conta = 0
    for _ in range(REAMOSTRAS):
        aleatorio.shuffle(juntos)
        if abs(juntos[:n].mean() - juntos[n:].mean()) >= observado:
            conta += 1
    return (conta + 1) / (REAMOSTRAS + 1)


def holm(ps):
    """Correcao de Holm, devolve os p ajustados na ordem de entrada."""
    ordem = sorted(range(len(ps)), key=lambda i: ps[i])
    ajustados = [0.0] * len(ps)
    anterior = 0.0
    for posicao, i in enumerate(ordem):
        valor = (len(ps) - posicao) * ps[i]
        anterior = max(anterior, min(valor, 1.0))
        ajustados[i] = anterior
    return ajustados


# ------------------------------------------------------------ leitura
medidas = {}
for nome in sorted(os.listdir(entrada)):
    if nome.startswith("lote_") and nome.endswith(".csv"):
        cfg, v = ler(os.path.join(entrada, nome))
        if len(v):
            medidas[cfg] = v

if not medidas:
    sys.exit("FALHOU: nenhuma medicao lida em %s" % entrada)

# ------------------------------------------------- intervalos por configuracao
linhas = []
print("%-24s %5s %9s %22s" % ("configuracao", "n", "media", "IC95% da media"))
for cfg in sorted(medidas):
    v = medidas[cfg]
    lo, hi = ic_media(v)
    linhas.append({"configuracao": cfg, "n": len(v),
                   "media_ms": round(float(v.mean()), 2),
                   "ic_inferior_ms": round(lo, 2), "ic_superior_ms": round(hi, 2),
                   "desvio_ms": round(float(v.std(ddof=1)), 2),
                   "p25_ms": round(float(np.percentile(v, 25)), 2),
                   "mediana_ms": round(float(np.median(v)), 2),
                   "p75_ms": round(float(np.percentile(v, 75)), 2)})
    print("%-24s %5d %9.2f   [%8.2f ; %8.2f]"
          % (cfg, len(v), v.mean(), lo, hi))

# ------------------------------------------------- comparacao entre delegates
pares, ps = [], []
for cfg in sorted(medidas):
    if "CPU" not in cfg:
        continue
    alvo = cfg.replace("CPU", "GPU")
    if alvo not in medidas:
        continue
    a, b = medidas[cfg], medidas[alvo]
    pares.append((cfg.replace(" · CPU", ""), a, b))
    ps.append(p_permutacao(a.copy(), b.copy()))

ajustados = holm(ps)
print("\n%-22s %8s %22s %10s %10s"
      % ("modelo e precisao", "razao", "IC95% da razao", "p", "p Holm"))
comparacoes = []
for (rotulo, a, b), p, pa in zip(pares, ps, ajustados):
    razao = float(a.mean() / b.mean())
    lo, hi = ic_razao(a, b)
    comparacoes.append({"configuracao": rotulo, "razao_cpu_gpu": round(razao, 3),
                        "ic_inferior": round(lo, 3), "ic_superior": round(hi, 3),
                        "p": round(p, 5), "p_holm": round(pa, 5)})
    print("%-22s %8.2f   [%7.2f ; %7.2f] %10.5f %10.5f"
          % (rotulo, razao, lo, hi, p, pa))

with io.open(saida, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
    w.writeheader()
    w.writerows(linhas)
alvo2 = saida.replace(".csv", "_razoes.csv")
with io.open(alvo2, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(comparacoes[0].keys()))
    w.writeheader()
    w.writerows(comparacoes)
print("\ngravados %s e %s" % (saida, alvo2))
