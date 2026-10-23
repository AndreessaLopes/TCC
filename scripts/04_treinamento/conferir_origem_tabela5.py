"""Identifica com que configuracao os valores da Tabela 5 foram obtidos.

A tabela reporta mAP@0,50 de 0,650 e 0,644, atribuidos ao conjunto de
teste. A medicao registrada em avaliar_teste.py da 0,6455 e 0,6419 sobre
o teste, com rect=False e imgsz=960.

Duas hipoteses explicam a diferenca. A primeira e a particao: os valores
podem ter vindo da validacao, e nao do teste. A segunda e o
redimensionamento: o metodo val do ultralytics usa rect=True por padrao,
que agrupa imagens por proporcao em vez de completar o quadrado, e isso
desloca o mAP na terceira casa decimal.

Este script percorre as duas hipoteses e aponta qual reproduz os valores
publicados. Nao grava nada e nao altera nenhum arquivo.

Uso, a partir da pasta ProjetoCafe:

    python conferir_origem_tabela5.py
"""
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(RAIZ, "dataset_final", "data.yaml")

MODELOS = {
    "YOLOv8n": (os.path.join(RAIZ, "runs", "detect", "runs_final",
                             "yolov8n_final_grao", "weights", "best.pt"), 0.650),
    "YOLOv10n": (os.path.join(RAIZ, "runs", "detect", "runs_final",
                              "yolov10n_final_grao", "weights", "best.pt"), 0.644),
}

CASOS = [
    ("teste, rect=True", dict(split="test", rect=True)),
    ("validacao, rect=True", dict(split="val", rect=True)),
]

BASE = dict(imgsz=960, batch=8, conf=0.001, iou=0.7, workers=0,
            plots=False, verbose=False)


def main():
    from ultralytics import YOLO

    achados = []
    for rotulo, extra in CASOS:
        print("\n--- %s ---" % rotulo)
        for nome, (pesos, publicado) in MODELOS.items():
            m = YOLO(pesos).val(data=DADOS, **dict(BASE, **extra))
            obtido = float(m.box.map50)
            bate = abs(obtido - publicado) < 0.0005
            achados.append((rotulo, nome, obtido, publicado, bate))
            print("%-9s mAP@0,50 = %.4f   publicado %.3f   %s"
                  % (nome, obtido, publicado, "CONFERE" if bate else "difere"))

    print("\n==================== conclusao ====================")
    for rotulo in dict.fromkeys(r for r, _, _, _, _ in achados):
        do_caso = [a for a in achados if a[0] == rotulo]
        if all(a[4] for a in do_caso):
            print("Os valores da Tabela 5 foram obtidos com: %s" % rotulo)
            break
    else:
        print("Nenhuma das duas hipoteses reproduz os dois valores.")
        print("Valores medidos:")
        for rotulo, nome, obtido, publicado, _ in achados:
            print("  %-22s %-9s %.4f (publicado %.3f)"
                  % (rotulo, nome, obtido, publicado))


if __name__ == "__main__":
    main()
