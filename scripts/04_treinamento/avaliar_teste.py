"""Mede os modelos treinados sobre a particao de teste.

A Tabela 5 do trabalho reporta mAP, precisao, revocacao e tempos das duas
arquiteturas. Os valores publicados vieram das pastas val2 e val3 de 28
de julho, que guardam apenas graficos, sem registro das configuracoes da
execucao. Este script grava resultado e configuracoes no mesmo arquivo,
de modo que a tabela passa a ter procedencia conferivel.

Os indicadores de qualidade nao dependem de repeticao, pois a inferencia
e deterministica. Os tempos dependem, porque variam com o estado da
maquina. O script repete a medicao tres vezes e grava cada repeticao,
para que a comparacao entre arquiteturas possa ser confrontada com a
variacao entre execucoes da mesma arquitetura, em vez de repousar sobre
uma leitura unica.

O corpo fica sob guarda de modulo principal e o carregamento de dados
roda sem processos auxiliares. No Windows o DataLoader abre processos
filhos por spawn, que reimportam o modulo; sem a guarda, cada filho
recomeca a medicao e o programa termina em erro. E a mesma razao pela
qual o treinar_final.py usa workers igual a zero.

Uso, a partir da pasta ProjetoCafe:

    python avaliar_teste.py

Leva por volta de cinco minutos. Grava resultados/csv/metricas_teste.csv
e resultados/csv/tempos_teste.csv.
"""
import csv
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(RAIZ, "dataset_final", "data.yaml")
REPETICOES = 3

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


def gravar(caminho, linhas):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)


def main():
    try:
        from ultralytics import YOLO
    except ImportError:
        sys.exit("Este script precisa da biblioteca ultralytics, que esta "
                 "no ambiente em que o treinamento rodou.")

    if not os.path.exists(DADOS):
        sys.exit("Nao encontrei %s. Execute a partir da pasta ProjetoCafe."
                 % DADOS)

    qualidade, tempos = [], []
    for nome, pesos in MODELOS.items():
        if not os.path.exists(pesos):
            sys.exit("Nao encontrei os pesos: %s" % pesos)
        for i in range(1, REPETICOES + 1):
            print("medindo %s, repeticao %d de %d ..."
                  % (nome, i, REPETICOES))
            m = YOLO(pesos).val(data=DADOS, **AJUSTES)
            v = m.speed
            tempos.append({
                "modelo": nome,
                "repeticao": i,
                "pre_ms": round(float(v["preprocess"]), 3),
                "inferencia_ms": round(float(v["inference"]), 3),
                "pos_ms": round(float(v["postprocess"]), 3),
            })
            if i == 1:
                c = m.box
                qualidade.append({
                    "modelo": nome,
                    "pesos": os.path.relpath(pesos, RAIZ),
                    "map50": round(float(c.map50), 4),
                    "map50_95": round(float(c.map), 4),
                    "precisao": round(float(c.mp), 4),
                    "revocacao": round(float(c.mr), 4),
                    **{k: v2 for k, v2 in AJUSTES.items() if k != "plots"},
                })

    gravar(os.path.join(RAIZ, "resultados", "csv", "metricas_teste.csv"),
           qualidade)
    gravar(os.path.join(RAIZ, "resultados", "csv", "tempos_teste.csv"),
           tempos)

    print("\n%-10s %9s %12s %10s %11s"
          % ("modelo", "mAP@0,50", "mAP@0,50-95", "precisao", "revocacao"))
    for r in qualidade:
        print("%-10s %9.4f %12.4f %10.4f %11.4f"
              % (r["modelo"], r["map50"], r["map50_95"], r["precisao"],
                 r["revocacao"]))

    print("\n%-10s %10s %14s %12s" % ("modelo", "pre (ms)",
                                      "inferencia (ms)", "pos (ms)"))
    for nome in MODELOS:
        meus = [t for t in tempos if t["modelo"] == nome]
        for t in meus:
            print("%-10s %10.2f %14.2f %12.2f"
                  % ("  rep %d" % t["repeticao"], t["pre_ms"],
                     t["inferencia_ms"], t["pos_ms"]))
        med = lambda c: sum(t[c] for t in meus) / len(meus)
        amp = lambda c: max(t[c] for t in meus) - min(t[c] for t in meus)
        print("%-10s %10.2f %14.2f %12.2f   <-- media de %s"
              % ("", med("pre_ms"), med("inferencia_ms"), med("pos_ms"), nome))
        print("%-10s %10.2f %14.2f %12.2f   <-- amplitude entre repeticoes"
              % ("", amp("pre_ms"), amp("inferencia_ms"), amp("pos_ms")))

    print("\ngravados metricas_teste.csv e tempos_teste.csv "
          "em resultados/csv")


if __name__ == "__main__":
    main()
