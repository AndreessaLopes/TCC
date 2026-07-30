"""
Treinamento FINAL dos modelos de deteccao (YOLOv8n e YOLOv10) sobre o
dataset consolidado, seguindo o protocolo experimental descrito na
metodologia do TCC:

    - Entrada: 960 x 960 pixels
    - Otimizador: AdamW
    - Taxa de aprendizado inicial: 0.003
    - Epocas: 120
    - Pesos iniciais: pre-treinados em COCO (transfer learning / fine-tuning)
    - Classe unica: 'grao'

AJUSTES PARA O HARDWARE (Ryzen 5 5500, 16 GB RAM, RTX 3060 8 GB VRAM):

    - batch = 8 (em vez de 16): com imgsz=960 e 8 GB de VRAM, batch 16
      causou CUDA out of memory nos testes. Se ocorrer OOM mesmo assim,
      reduza para 4 com --batch 4.
    - workers = 0: evita o erro CUDNN_STATUS_BAD_PARAM_STREAM_MISMATCH
      causado pelo multiprocessing do DataLoader no Windows.
    - amp = False: mesma razao acima (precisao mista + Windows).
    - cache = False: com 16 GB de RAM, cachear ~2.100 imagens de alta
      resolucao em memoria pode causar swap e travar o sistema.

IMPORTANTE sobre o batch reduzido: batch menor altera a dinamica de
treinamento em relacao ao batch 16 descrito no texto atual do TCC. Vale
atualizar a metodologia para refletir o batch efetivamente usado (8), ou
justificar a restricao de memoria da GPU - a banca costuma considerar isso
uma limitacao legitima e bem documentada.

USO:

    # treinar so o YOLOv8n
    python treinar_final.py --data_yaml dataset_final/data.yaml --modelos yolov8n

    # treinar so o YOLOv10
    python treinar_final.py --data_yaml dataset_final/data.yaml --modelos yolov10n

    # treinar os dois em sequencia (recomendado: deixe rodando de uma vez)
    python treinar_final.py --data_yaml dataset_final/data.yaml --modelos yolov8n yolov10n

    # se der CUDA out of memory
    python treinar_final.py --data_yaml dataset_final/data.yaml --modelos yolov8n --batch 4
"""

import argparse
import time
from pathlib import Path

from ultralytics import YOLO


# Mapeamento entre o nome curto informado na linha de comando e o
# checkpoint pre-treinado correspondente (baixado automaticamente pelo
# Ultralytics na primeira execucao).
CHECKPOINTS = {
    "yolov8n": "yolov8n.pt",
    "yolov10n": "yolov10n.pt",
    "yolov10s": "yolov10s.pt",
}


def treinar_um_modelo(nome_modelo: str, args) -> dict:
    checkpoint = CHECKPOINTS[nome_modelo]
    run_name = f"{nome_modelo}_final_grao"

    print("\n" + "=" * 70)
    print(f"INICIANDO TREINAMENTO: {nome_modelo}  (checkpoint: {checkpoint})")
    print(f"imgsz={args.imgsz} | batch={args.batch} | epochs={args.epochs} | "
          f"optimizer={args.optimizer} | lr0={args.lr0}")
    print("=" * 70 + "\n")

    inicio = time.time()
    modelo = YOLO(checkpoint)

    modelo.train(
        data=args.data_yaml,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        lr0=args.lr0,
        optimizer=args.optimizer,
        project=args.project,
        name=run_name,
        workers=args.workers,
        amp=args.amp,
        cache=False,
        patience=args.patience,
        seed=args.seed,
        # Aumento de dados conforme descrito na metodologia (seccao 3.3):
        # ajustes de brilho/saturacao/matiz, espelhamento horizontal,
        # rotacoes e translacoes pequenas, escala e mosaico.
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        fliplr=0.5,
        flipud=0.0,
        degrees=5.0,
        translate=0.1,
        scale=0.5,
        mosaic=1.0,
    )

    duracao_min = (time.time() - inicio) / 60

    # Avaliacao no conjunto de TESTE (o train() acima valida no split de val).
    print(f"\n--- Avaliando {nome_modelo} no conjunto de teste ---")
    metricas_teste = modelo.val(
        data=args.data_yaml,
        split="test",
        imgsz=args.imgsz,
        batch=args.batch,
        workers=args.workers,
    )

    resultado = {
        "modelo": nome_modelo,
        "duracao_min": duracao_min,
        "pesos": f"{args.project}/{run_name}/weights/best.pt",
        "map50": float(metricas_teste.box.map50),
        "map50_95": float(metricas_teste.box.map),
        "precisao": float(metricas_teste.box.mp),
        "recall": float(metricas_teste.box.mr),
    }
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data_yaml", type=str, required=True,
                        help="Caminho para dataset_final/data.yaml")
    parser.add_argument("--modelos", type=str, nargs="+", default=["yolov8n"],
                        choices=sorted(CHECKPOINTS.keys()),
                        help="Um ou mais modelos a treinar, em sequencia.")

    # Parametros do protocolo metodologico
    parser.add_argument("--epochs", type=int, default=120)
    parser.add_argument("--imgsz", type=int, default=960)
    parser.add_argument("--lr0", type=float, default=0.003)
    parser.add_argument("--optimizer", type=str, default="AdamW")

    # Ajustes de hardware (RTX 3060 8 GB / Windows)
    parser.add_argument("--batch", type=int, default=8,
                        help="Default 8 por limite de VRAM. Use 4 se houver CUDA OOM.")
    parser.add_argument("--workers", type=int, default=0,
                        help="0 evita erros de multiprocessing/cuDNN no Windows.")
    parser.add_argument("--amp", type=lambda v: str(v).lower() != "false", default=False,
                        help="Precisao mista. Default False (evita erro de cuDNN no Windows).")

    parser.add_argument("--patience", type=int, default=30,
                        help="Early stopping: para se nao melhorar por N epocas.")
    parser.add_argument("--seed", type=int, default=0,
                        help="Semente para reprodutibilidade dos experimentos.")
    parser.add_argument("--project", type=str, default="runs_final")
    args = parser.parse_args()

    if not Path(args.data_yaml).exists():
        raise FileNotFoundError(f"data.yaml nao encontrado: {args.data_yaml}")

    resultados = []
    for nome_modelo in args.modelos:
        try:
            resultados.append(treinar_um_modelo(nome_modelo, args))
        except Exception as erro:
            print(f"\n[ERRO] Falha ao treinar {nome_modelo}: {erro}")
            print("Se for CUDA out of memory, tente novamente com --batch 4.")
            print("Seguindo para o proximo modelo (se houver)...\n")

    if not resultados:
        print("\nNenhum modelo foi treinado com sucesso.")
        return

    print("\n" + "=" * 70)
    print("RESUMO DOS TREINAMENTOS (metricas no conjunto de TESTE)")
    print("=" * 70)
    cabecalho = f"{'Modelo':<12} {'mAP@0.50':>10} {'mAP@0.50-95':>12} {'Precisao':>10} {'Recall':>10} {'Tempo(min)':>11}"
    print(cabecalho)
    print("-" * len(cabecalho))
    for r in resultados:
        print(f"{r['modelo']:<12} {r['map50']:>10.4f} {r['map50_95']:>12.4f} "
              f"{r['precisao']:>10.4f} {r['recall']:>10.4f} {r['duracao_min']:>11.1f}")

    print("\nPesos salvos em:")
    for r in resultados:
        print(f"  {r['modelo']}: {r['pesos']}")

    print("\nProximo passo da metodologia: converter esses pesos para TFLite "
          "(FP32, FP16 e INT8) e integrar na aplicacao Android.")


if __name__ == "__main__":
    main()