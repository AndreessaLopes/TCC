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
    cab, linhas = {}, []
    with open(caminho, encoding="utf-8", errors="replace") as f:
        for linha in f:
            if linha.startswith("#"):
                m = re.match(r"# ([^:]+): (.+)", linha.strip())
                if m:
                    cab[m.group(1)] = m.group(2).strip()
            elif linha.strip() and not linha.startswith("arquivo"):
                c = linha.strip().split(",")
                if len(c) >= 8 and c[7] != "1":
                    linhas.append({
                        "arquivo": c[0],
                        "deteccoes": int(c[1]),
                        "pre": float(c[2]),
                        "inf": float(c[3]),
                        "pos": float(c[4]),
                        "tot": float(c[5]),
                        "mem": int(c[6]),
                    })
    return cab, linhas


registros = []
for raiz, _, arquivos in os.walk(entrada):
    for nome in sorted(arquivos):
        if not nome.lower().endswith(".csv"):
            continue
        cab, linhas = ler(os.path.join(raiz, nome))
        if "Configuracao" not in cab or not linhas:
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
    conjuntos = {tuple(sorted(l["arquivo"] for l in linhas))
                 for _, linhas, _ in itens}
    n_imgs = sorted({len(linhas) for _, linhas, _ in itens})

    print("%s %s (placa %s) — Android %s — %d configuracoes"
          % (fab, apar, placa,
             itens[0][0].get("Android", "?"), len(itens)))

    if len(conjuntos) > 1:
        alertas.append("%s %s: as configuracoes nao rodaram sobre o mesmo "
                       "conjunto de imagens (%s)" % (fab, apar, n_imgs))

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
        if bateria.isdigit() and int(bateria) < 80:
            alertas.append("%s %s / %s: iniciada com %s%% de bateria"
                           % (fab, apar, cab["Configuracao"], bateria))

        linhas_saida.append({
            "fabricante": fab,
            "aparelho": apar,
            "placa": placa,
            "android": cab.get("Android", ""),
            "arquitetura": arq,
            "precisao": prec,
            "delegate": deleg,
            "imagens": len(linhas),
            "latencia_media_ms": round(st.mean(l["tot"] for l in linhas), 2),
            "latencia_desvio_ms": round(
                st.pstdev(l["tot"] for l in linhas), 2),
            "inferencia_media_ms": round(st.mean(l["inf"] for l in linhas), 2),
            "preprocessamento_ms": round(st.mean(l["pre"] for l in linhas), 2),
            "posprocessamento_ms": round(st.mean(l["pos"] for l in linhas), 2),
            "memoria_pico_mb": max(l["mem"] for l in linhas),
            "deteccoes_total": sum(l["deteccoes"] for l in linhas),
            "bateria_consumida": cab.get("Bateria consumida", ""),
            "arquivo": nome,
        })

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
