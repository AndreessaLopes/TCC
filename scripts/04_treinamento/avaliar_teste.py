"""Mede os modelos treinados sobre a particao de teste.

A Tabela 5 do trabalho reporta mAP, precisao e revocacao das duas
arquiteturas. Os valores publicados vieram de uma execucao cujas
configuracoes nao ficaram registradas, e uma remedicao posterior
divergiu na terceira casa decimal. Divergencia dessa ordem costuma vir
de diferenca de ajuste, e nao de erro, de modo que trocar um numero por
outro sem registrar como cada um foi obtido piora a rastreabilidade em
vez de melhorar.

Este script existe para encerrar isso. Grava o resultado e as
configuracoes usadas no mesmo arquivo, de modo que a tabela passa a ter
procedencia conferivel.

O corpo fica sob guarda de modulo principal e o carregamento de dados
roda sem processos auxiliares. No Windows o DataLoader abre processos
filhos por spawn, que reimportam o modulo; sem a guarda, cada filho
recomeca a medicao e o programa termina em erro. E a mesma razao pela
qual o treinar_final.py usa workers igual a zero.

Uso, a partir da pasta ProjetoCafe:

    python avaliar_teste.py

Grava resultados/csv/metricas_teste.csv.
"""
import csv
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(RAIZ, "dataset_final", "data.yaml")

MODELOS = {
    "YOLOv8n": os.path.join(RAIZ, "runs", "detect", "runs_final",
                            "yolov8n_final_grao", "weights", "best.pt"),
    "YOLOv10n": os.path.join(RAIZ, "runs", "detect", "runs_final",
                             "yolov10n_final_grao", "weights", "best.pt"),
}

# Os mesmos ajustes do treinamento, no que se aplica a avaliacao. Ficam
# explicitos aqui porque sao eles que explicam diferenca na terceira casa
# decimal entre uma medicao e outra.
AJUSTES = dict(imgsz=960, batch=8, conf=0.001, iou=0.7, rect=False,
               split="test", workers=0, plots=False, verbose=False)


def main():
    try:
        from ultralytics import YOLO
    except ImportError:
        sys.exit("Este script precisa da biblioteca ultralytics, que esta "
                 "no ambiente em que o treinamento rodou.")

    if not os.path.exists(DADOS):
        sys.exit("Nao encontrei %s. Execute a partir da pasta ProjetoCafe."
                 % DADOS)

    linhas = []
    for nome, pesos in MODELOS.items():
        if not os.path.exists(pesos):
            sys.exit("Nao encontrei os pesos: %s" % pesos)
        print("medindo %s ..." % nome)
        m = YOLO(pesos).val(data=DADOS, **AJUSTES)
        c = m.box
        linhas.append({
            "modelo": nome,
            "pesos": os.path.relpath(pesos, RAIZ),
            "map50": round(float(c.map50), 4),
            "map50_95": round(float(c.map), 4),
            "precisao": round(float(c.mp), 4),
            "revocacao": round(float(c.mr), 4),
            **{k: v for k, v in AJUSTES.items() if k != "plots"},
        })

    saida = os.path.join(RAIZ, "resultados", "csv", "metricas_teste.csv")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    with open(saida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)

    print("\ngravado %s\n" % saida)
    print("%-10s %9s %12s %10s %11s"
          % ("modelo", "mAP@0,50", "mAP@0,50-95", "precisao", "revocacao"))
    for r in linhas:
        print("%-10s %9.4f %12.4f %10.4f %11.4f"
              % (r["modelo"], r["map50"], r["map50_95"], r["precisao"],
                 r["revocacao"]))


if __name__ == "__main__":
    main()
