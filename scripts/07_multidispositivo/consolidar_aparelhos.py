"""Consolida as medicoes recebidas de diferentes aparelhos.

Le todos os arquivos de lote de uma pasta, agrupa por aparelho e por
configuracao e grava uma tabela unica. Serve a coleta em dispositivos de
terceiros, em que cada pessoa devolve ate doze arquivos.

Verifica tambem o que pode invalidar uma comparacao: aparelhos que nao
rodaram o mesmo conjunto de imagens, execucoes interrompidas e medicoes
iniciadas com bateria baixa.

Uso: python3 -I consolidar_aparelhos.py <pasta com os csv> <saida.csv>
"""
import csv
import os
import re
import statistics as st
import sys
from collections import defaultdict

entrada, saida = sys.argv[1], sys.argv[2]

ORDEM_PRECISAO = {"FP32": 0, "FP16": 1, "INT8": 2}


def ler(caminho):
    # A tabela consolidada costuma ficar na mesma pasta dos lotes. Como ela
    # nao tem cabecalho comentado nem a coluna "arquivo" na primeira
    # posicao, so se lem as linhas que vem depois do cabecalho de medicao.
    cab, linhas, no_corpo = {}, [], False
    with open(caminho, encoding="utf-8", errors="replace") as f:
        for linha in f:
            if linha.startswith("#"):
                m = re.match(r"# ([^:]+): (.+)", linha.strip())
                if m:
                    cab[m.group(1)] = m.group(2).strip()
            elif linha.startswith("arquivo,"):
                no_corpo = True
            elif no_corpo and linha.strip():
                c = linha.strip().split(",")
                if len(c) >= 8:
                    linhas.append({
                        "arquivo": c[0],
                        "deteccoes": int(c[1]),
                        "pre": float(c[2]),
                        "inf": float(c[3]),
                        "pos": float(c[4]),
                        "tot": float(c[5]),
                        "mem": int(c[6]),
                        "descartada": c[7] == "1",
                    })
    # As descartadas ficam na lista para que a comparacao entre aparelhos
    # saiba quais imagens foram tentadas; as estatisticas usam so as validas.
    return cab, linhas


def validas(linhas):
    return [l for l in linhas if not l["descartada"]]


registros = []
for raiz, _, arquivos in os.walk(entrada):
    for nome in sorted(arquivos):
        if not nome.lower().endswith(".csv"):
            continue
        cab, linhas = ler(os.path.join(raiz, nome))
        if "Configuracao" not in cab or not validas(linhas):
            print("ignorado (sem medicoes): %s" % nome)
            continue
        registros.append((cab, linhas, nome))

if not registros:
    sys.exit("Nenhum arquivo de lote valido em %s" % entrada)

# ------------------------------------------------------------- aparelhos
por_aparelho = defaultdict(list)
for cab, linhas, nome in registros:
    chave = (cab.get("Fabricante", "?"), cab.get("Aparelho", "?"),
             cab.get("Placa", "?"))
    por_aparelho[chave].append((cab, linhas, nome))

print("aparelhos encontrados: %d\n" % len(por_aparelho))

alertas = []
linhas_saida = []

for (fab, apar, placa), itens in sorted(por_aparelho.items()):
    # Compara as imagens tentadas. Uma medicao descartada nao muda o
    # conjunto sobre o qual a configuracao rodou, so reduz a amostra.
    conjuntos = {tuple(sorted(l["arquivo"] for l in linhas))
                 for _, linhas, _ in itens}
    n_imgs = sorted({len(linhas) for _, linhas, _ in itens})
    descartes = [(c["Configuracao"], sum(1 for l in linhas if l["descartada"]))
                 for c, linhas, _ in itens]

    print("%s %s (placa %s) — Android %s — %d configuracoes"
          % (fab, apar, placa,
             itens[0][0].get("Android", "?"), len(itens)))

    if len(conjuntos) > 1:
        alertas.append("%s %s: as configuracoes nao rodaram sobre o mesmo "
                       "conjunto de imagens (%s)" % (fab, apar, n_imgs))

    for config, n in descartes:
        if n:
            alertas.append("%s %s / %s: %d medicao(oes) descartada(s)"
                           % (fab, apar, config, n))

    for cab, linhas, nome in sorted(
            itens, key=lambda t: (t[0]["Configuracao"].split(" · ")[0],
                                  ORDEM_PRECISAO.get(
                                      t[0]["Configuracao"].split(" · ")[1], 9),
                                  t[0]["Configuracao"].split(" · ")[2])):
        arq, prec, deleg = cab["Configuracao"].split(" · ")

        if "ATENCAO" in " ".join(cab.keys()):
            alertas.append("%s %s / %s: execucao interrompida"
                           % (fab, apar, cab["Configuracao"]))

        bateria = cab.get("Bateria inicial", "").replace(" %", "")
        if bateria.isdigit() and int(bateria) < 20:
            alertas.append("%s %s / %s: iniciada com %s%% de bateria, nivel "
                           "em que o sistema costuma limitar o desempenho"
                           % (fab, apar, cab["Configuracao"], bateria))

        linhas_saida.append({
            "fabricante": fab,
            "aparelho": apar,
            "placa": placa,
            "hardware": cab.get("Hardware", ""),
            "android": cab.get("Android", ""),
            "arquitetura": arq,
            "precisao": prec,
            "delegate": deleg,
            "imagens": len(validas(linhas)),
            "latencia_media_ms": round(st.mean(l["tot"] for l in validas(linhas)), 2),
            "latencia_desvio_ms": round(
                st.pstdev(l["tot"] for l in validas(linhas)), 2),
            "inferencia_media_ms": round(st.mean(l["inf"] for l in validas(linhas)), 2),
            "preprocessamento_ms": round(st.mean(l["pre"] for l in validas(linhas)), 2),
            "posprocessamento_ms": round(st.mean(l["pos"] for l in validas(linhas)), 2),
            "memoria_pico_mb": max(l["mem"] for l in validas(linhas)),
            "deteccoes_total": sum(l["deteccoes"] for l in validas(linhas)),
            "bateria_consumida": cab.get("Bateria consumida", ""),
            "arquivo": nome,
        })

    # O protocolo pede 80% no inicio. Durante o varrimento a bateria cai,
    # e cobrar 80% de cada configuracao acusaria toda coleta completa.
    primeira = min(itens, key=lambda t: t[0].get("Inicio", ""))[0]
    inicial = primeira.get("Bateria inicial", "").replace(" %", "")
    if inicial.isdigit() and int(inicial) < 80:
        alertas.append("%s %s: a coleta comecou com %s%% de bateria"
                       % (fab, apar, inicial))

    # Configuracoes ausentes, que nao executaram no aparelho.
    presentes = {c["Configuracao"] for c, _, _ in itens}
    todas = {"%s · %s · %s" % (a, p, d)
             for a in ("YOLOv8n", "YOLOv10n")
             for p in ("FP32", "FP16", "INT8")
             for d in ("CPU", "GPU")}
    for falta in sorted(todas - presentes):
        print("   nao executou: %s" % falta)
        linhas_saida.append({
            "fabricante": fab, "aparelho": apar, "placa": placa,
            "hardware": itens[0][0].get("Hardware", ""),
            "android": itens[0][0].get("Android", ""),
            "arquitetura": falta.split(" · ")[0],
            "precisao": falta.split(" · ")[1],
            "delegate": falta.split(" · ")[2],
            "imagens": 0, "latencia_media_ms": "", "latencia_desvio_ms": "",
            "inferencia_media_ms": "", "preprocessamento_ms": "",
            "posprocessamento_ms": "", "memoria_pico_mb": "",
            "deteccoes_total": "", "bateria_consumida": "",
            "arquivo": "nao executou",
        })
    print()

with open(saida, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(linhas_saida[0].keys()))
    w.writeheader()
    w.writerows(linhas_saida)

print("gravado %s  (%d linhas)" % (saida, len(linhas_saida)))

if alertas:
    print("\nAtencao:")
    for a in sorted(set(alertas)):
        print("  - %s" % a)
