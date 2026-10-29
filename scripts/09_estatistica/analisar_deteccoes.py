"""Confronta as deteccoes com as anotacoes, por tamanho de objeto.

Duas lacunas apontadas na revisao se resolvem com a mesma analise.

A primeira e a revocacao por faixa de tamanho. O trabalho relata
revocacao de 0,61 e atribui a perda a frutos pequenos, sem mostrar. Aqui
cada instancia anotada e classificada em pequena, media ou grande pela
area ocupada na entrada de 960 pixels, segundo os limites usuais de 32 e
96 pixels de lado, e a revocacao e apurada em cada faixa.

A segunda e a hipotese de falsos positivos na quantizacao INT8. O texto
observa acrescimo de 5,1% no numero de deteccoes e diz que confrontar com
as anotacoes nao foi conduzido. Aqui o confronto e feito, de modo que o
acrescimo passa a ser atribuido a falsos positivos ou a acertos.

O pareamento segue o criterio usual: deteccoes em ordem decrescente de
confianca, cada uma atribuida a anotacao ainda livre de maior sobreposicao,
desde que a interseccao sobre uniao alcance 0,50. O limiar de confianca e
o mesmo da aplicacao.

Uso, a partir da pasta ProjetoCafe:

    python analisar_deteccoes.py

Leva por volta de quinze minutos, a maior parte nas variantes INT8, que
executam em processador. Grava resultados/csv/deteccoes_por_tamanho.csv e
resultados/csv/confronto_anotacoes.csv.
"""
import csv
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
IMAGENS = os.path.join(RAIZ, "dataset_final", "test", "images")
ROTULOS = os.path.join(RAIZ, "dataset_final", "test", "labels")

ENTRADA = 960          # lado da entrada do modelo
CONFIANCA = 0.25       # mesmo limiar da aplicacao
IOU_PAREAMENTO = 0.50
LIMITES = (32 ** 2, 96 ** 2)   # pequena | media | grande

MODELOS = [
    ("YOLOv8n", "PyTorch", os.path.join(
        RAIZ, "runs", "detect", "runs_final", "yolov8n_final_grao",
        "weights", "best.pt")),
    ("YOLOv10n", "PyTorch", os.path.join(
        RAIZ, "runs", "detect", "runs_final", "yolov10n_final_grao",
        "weights", "best.pt")),
    ("YOLOv8n", "FP32", os.path.join(RAIZ, "modelos_tflite",
                                     "yolov8n_fp32.tflite")),
    ("YOLOv8n", "INT8", os.path.join(RAIZ, "modelos_tflite",
                                     "yolov8n_int8.tflite")),
    ("YOLOv10n", "FP32", os.path.join(RAIZ, "modelos_tflite",
                                      "yolov10n_fp32.tflite")),
    ("YOLOv10n", "INT8", os.path.join(RAIZ, "modelos_tflite",
                                      "yolov10n_int8.tflite")),
]


def faixa(area_na_entrada):
    if area_na_entrada < LIMITES[0]:
        return "pequena"
    if area_na_entrada <= LIMITES[1]:
        return "media"
    return "grande"


def anotacoes_da(nome, largura, altura):
    """Caixas anotadas em pixels da imagem, com a faixa de tamanho."""
    caminho = os.path.join(ROTULOS, os.path.splitext(nome)[0] + ".txt")
    caixas = []
    if not os.path.exists(caminho):
        return caixas
    # A entrada preserva proporcao, de modo que o fator e o mesmo nos dois eixos.
    fator = ENTRADA / max(largura, altura)
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            p = linha.split()
            if len(p) < 5:
                continue
            cx, cy, w, h = (float(x) for x in p[1:5])
            x1, y1 = (cx - w / 2) * largura, (cy - h / 2) * altura
            x2, y2 = (cx + w / 2) * largura, (cy + h / 2) * altura
            area_entrada = (w * largura * fator) * (h * altura * fator)
            caixas.append([x1, y1, x2, y2, faixa(area_entrada)])
    return caixas


def sobreposicao(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return 0.0
    inter = (x2 - x1) * (y2 - y1)
    ua = (a[2] - a[0]) * (a[3] - a[1])
    ub = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (ua + ub - inter)


def avaliar(pesos):
    """Percorre o conjunto de teste e devolve as contagens."""
    from ultralytics import YOLO

    modelo = YOLO(pesos)
    tp = fp = fn = 0
    por_faixa = {f: {"anotadas": 0, "encontradas": 0}
                 for f in ("pequena", "media", "grande")}

    # Sem device fixo: os modelos em PyTorch usam a placa quando disponivel e
    # as variantes TFLite executam em processador, onde unicamente executam.
    saida = modelo.predict(source=IMAGENS, imgsz=ENTRADA, conf=CONFIANCA,
                           iou=0.7, stream=True, verbose=False)
    for r in saida:
        altura, largura = r.orig_shape
        alvos = anotacoes_da(os.path.basename(r.path), largura, altura)
        for c in alvos:
            por_faixa[c[4]]["anotadas"] += 1

        caixas = r.boxes
        if caixas is None or len(caixas) == 0:
            fn += len(alvos)
            continue
        conf = [float(x) for x in caixas.conf.tolist()]
        xyxy = [[float(v) for v in b] for b in caixas.xyxy.tolist()]
        ordem = sorted(range(len(conf)), key=lambda i: conf[i], reverse=True)
        usados = set()
        for i in ordem:
            melhor, indice = 0.0, -1
            for j, alvo in enumerate(alvos):
                if j in usados:
                    continue
                v = sobreposicao(xyxy[i], alvo)
                if v > melhor:
                    melhor, indice = v, j
            if indice >= 0 and melhor >= IOU_PAREAMENTO:
                usados.add(indice)
                tp += 1
                por_faixa[alvos[indice][4]]["encontradas"] += 1
            else:
                fp += 1
        fn += len(alvos) - len(usados)
    return tp, fp, fn, por_faixa


def gravar(caminho, linhas):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    print("gravado %s" % caminho)


def main():
    if not os.path.isdir(IMAGENS):
        sys.exit("Nao encontrei %s. Execute a partir da pasta ProjetoCafe."
                 % IMAGENS)

    confronto, tamanhos = [], []
    for nome, precisao, pesos in MODELOS:
        if not os.path.exists(pesos):
            print("ausente, ignorado: %s" % pesos)
            continue
        print("avaliando %s %s ..." % (nome, precisao))
        tp, fp, fn, por_faixa = avaliar(pesos)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rev = tp / (tp + fn) if tp + fn else 0.0
        confronto.append({
            "modelo": nome, "precisao_numerica": precisao,
            "deteccoes": tp + fp, "verdadeiros_positivos": tp,
            "falsos_positivos": fp, "falsos_negativos": fn,
            "precisao": round(prec, 4), "revocacao": round(rev, 4),
            "conf": CONFIANCA, "iou_pareamento": IOU_PAREAMENTO,
        })
        print("   deteccoes %d | VP %d | FP %d | FN %d | precisao %.4f | revocacao %.4f"
              % (tp + fp, tp, fp, fn, prec, rev))
        for f in ("pequena", "media", "grande"):
            d = por_faixa[f]
            r = d["encontradas"] / d["anotadas"] if d["anotadas"] else 0.0
            tamanhos.append({"modelo": nome, "precisao_numerica": precisao,
                             "faixa": f, "anotadas": d["anotadas"],
                             "encontradas": d["encontradas"],
                             "revocacao": round(r, 4)})
            print("   %-8s anotadas %5d  encontradas %5d  revocacao %.4f"
                  % (f, d["anotadas"], d["encontradas"], r))

    if not confronto:
        sys.exit("Nenhum modelo avaliado.")
    gravar(os.path.join(RAIZ, "resultados", "csv", "confronto_anotacoes.csv"),
           confronto)
    gravar(os.path.join(RAIZ, "resultados", "csv",
                        "deteccoes_por_tamanho.csv"), tamanhos)


if __name__ == "__main__":
    main()
