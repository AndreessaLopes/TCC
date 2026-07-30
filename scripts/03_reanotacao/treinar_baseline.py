"""
Etapa 2 do pipeline de reanotação semi-automática.

Treina um modelo YOLOv8n "baseline" usando apenas o dataset limpo (sem
imagens de cacho), gerado pela Etapa 1 (organizar_dataset_limpo.py).

Esse modelo NÃO é o modelo final da sua pesquisa — ele serve como
ferramenta auxiliar para sugerir bounding boxes nas imagens problemáticas
(Etapa 3). Por isso os hiperparâmetros aqui priorizam velocidade de
treinamento sobre desempenho máximo; ajuste --epochs se quiser mais
qualidade nas sugestões.

Uso:
    python treinar_baseline.py --data_yaml dataset_baseline/data.yaml
"""

import argparse

from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data_yaml", type=str, required=True,
                        help="Caminho para o data.yaml gerado na Etapa 1.")
    parser.add_argument("--modelo_base", type=str, default="yolov8n.pt",
                        help="Pesos pré-treinados de partida (COCO).")
    parser.add_argument("--epochs", type=int, default=80,
                        help="Número de épocas. 80 costuma bastar para um baseline "
                             "usado só para pré-anotação (não precisa ser o treino final).")
    parser.add_argument("--imgsz", type=int, default=960)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--lr0", type=float, default=0.003)
    parser.add_argument("--optimizer", type=str, default="AdamW")
    parser.add_argument("--project", type=str, default="runs_baseline")
    parser.add_argument("--name", type=str, default="yolov8n_baseline_grao")
    args = parser.parse_args()

    modelo = YOLO(args.modelo_base)

    resultados = modelo.train(
        data=args.data_yaml,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        lr0=args.lr0,
        optimizer=args.optimizer,
        project=args.project,
        name=args.name,
    )

    print("\n=== Treinamento concluído ===")
    print(f"Pesos do melhor modelo salvos em: {args.project}/{args.name}/weights/best.pt")
    print("Use esse caminho no --modelo do script gerar_preanotacoes_cacho.py (Etapa 3).")


if __name__ == "__main__":
    main()