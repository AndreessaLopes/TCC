"""
Etapa 3 do pipeline de reanotação semi-automática.

Para cada arquivo sinalizado como "provavel_cacho" ou "provavel_erro"
(pelo triagem_bbox_suspeitas.py):

    1. Remove APENAS as linhas de anotação que foram sinalizadas como
       suspeitas (mantém, se existirem, outras caixas boas já anotadas
       na mesma imagem — ex.: os grãos individuais em verde que vimos
       na inspeção visual).
    2. Roda o modelo baseline (treinado na Etapa 2) sobre a imagem inteira,
       para sugerir caixas de grão individual.
    3. Descarta sugestões que sobrepõem (IoU alto) as caixas já mantidas,
       para não duplicar anotação.
    4. Salva o arquivo .txt resultante (caixas mantidas + sugestões novas)
       pronto para importação no MakeSense.ai como pré-anotação, junto
       com a imagem correspondente.

Arquivos em que sobrarem ZERO caixas (nem mantidas, nem sugeridas pelo
modelo) são listados à parte em "manual_review_necessaria.txt", pois
provavelmente precisam de anotação manual completa (o baseline não
conseguiu detectar nada de aproveitável ali).

IMPORTANTE: o resultado gerado por este script é uma PRÉ-ANOTAÇÃO, não
uma anotação final. Revise visualmente no MakeSense.ai antes de usar no
treinamento final — o modelo baseline é imperfeito, especialmente em
cenas densas.

Uso:
    python gerar_preanotacoes_cacho.py \
        --labels_dir dataset_24_06/labels \
        --images_dir dataset_24_06/images \
        --relatorio_csv relatorio_bboxes_suspeitas.csv \
        --modelo runs_baseline/yolov8n_baseline_grao/weights/best.pt \
        --saida_dir preanotacoes_cacho \
        --conf 0.25
"""

import argparse
import csv
import shutil
from collections import defaultdict
from pathlib import Path

from ultralytics import YOLO


def carregar_linhas_sinalizadas(csv_path: Path):
    """Retorna dict: nome_arquivo -> conjunto de números de linha sinalizados (1-indexed)."""
    mapa = defaultdict(set)
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapa[row["arquivo"]].add(int(row["linha"]))
    return mapa


def encontrar_imagem_correspondente(images_dir: Path, nome_base: str):
    for ext in (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"):
        candidato = images_dir / f"{nome_base}{ext}"
        if candidato.exists():
            return candidato
    encontrados = list(images_dir.rglob(f"{nome_base}.*"))
    return encontrados[0] if encontrados else None


def ler_caixas_mantidas(txt_path: Path, linhas_suspeitas: set):
    """Lê o arquivo original e retorna só as caixas cujas linhas NÃO foram sinalizadas."""
    mantidas = []
    with open(txt_path, "r") as f:
        linhas = [l.strip() for l in f if l.strip()]

    for i, linha in enumerate(linhas):
        numero_linha = i + 1
        if numero_linha in linhas_suspeitas:
            continue
        partes = linha.split()
        if len(partes) < 5:
            continue
        try:
            classe, xc, yc, w, h = partes[:5]
            mantidas.append((classe, float(xc), float(yc), float(w), float(h)))
        except ValueError:
            continue

    return mantidas


def iou_xywhn(box_a, box_b):
    """Calcula IoU entre duas caixas no formato (xc, yc, w, h) normalizado."""
    ax0, ay0 = box_a[0] - box_a[2] / 2, box_a[1] - box_a[3] / 2
    ax1, ay1 = box_a[0] + box_a[2] / 2, box_a[1] + box_a[3] / 2
    bx0, by0 = box_b[0] - box_b[2] / 2, box_b[1] - box_b[3] / 2
    bx1, by1 = box_b[0] + box_b[2] / 2, box_b[1] + box_b[3] / 2

    ix0, iy0 = max(ax0, bx0), max(ay0, by0)
    ix1, iy1 = min(ax1, bx1), min(ay1, by1)

    inter_w = max(0.0, ix1 - ix0)
    inter_h = max(0.0, iy1 - iy0)
    inter = inter_w * inter_h

    area_a = (ax1 - ax0) * (ay1 - ay0)
    area_b = (bx1 - bx0) * (by1 - by0)
    uniao = area_a + area_b - inter

    return inter / uniao if uniao > 0 else 0.0


def sobrepoe_alguma(caixa_nova, caixas_existentes, limiar_iou=0.4):
    for existente in caixas_existentes:
        if iou_xywhn(caixa_nova[1:], existente[1:]) >= limiar_iou:
            return True
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels_dir", type=str, required=True)
    parser.add_argument("--images_dir", type=str, required=True)
    parser.add_argument("--relatorio_csv", type=str, required=True)
    parser.add_argument("--modelo", type=str, required=True,
                        help="Caminho para o best.pt treinado na Etapa 2.")
    parser.add_argument("--saida_dir", type=str, default="preanotacoes_cacho")
    parser.add_argument("--conf", type=float, default=0.25,
                        help="Confiança mínima para aceitar uma sugestão do modelo.")
    parser.add_argument("--iou_dedup", type=float, default=0.4,
                        help="IoU acima do qual uma sugestão é considerada duplicata "
                             "de uma caixa já mantida e descartada.")
    parser.add_argument("--imgsz", type=int, default=960)
    parser.add_argument("--iou_nms", type=float, default=0.7,
                        help="Limiar de IoU do NMS na inferencia. Valores MAIS ALTOS "
                             "(ex.: 0.85-0.9) preservam mais detecoes separadas em "
                             "frutos proximos/encostados, reduzindo o agrupamento "
                             "indevido de varios graos numa unica caixa.")
    args = parser.parse_args()

    labels_dir = Path(args.labels_dir)
    images_dir = Path(args.images_dir)
    saida_dir = Path(args.saida_dir)
    (saida_dir / "labels").mkdir(parents=True, exist_ok=True)
    (saida_dir / "images").mkdir(parents=True, exist_ok=True)

    linhas_sinalizadas = carregar_linhas_sinalizadas(Path(args.relatorio_csv))
    modelo = YOLO(args.modelo)

    total = len(linhas_sinalizadas)
    sem_caixas = []
    resumo_contagem = []

    for i, (nome_arquivo, linhas_suspeitas) in enumerate(linhas_sinalizadas.items(), start=1):
        txt_path = None
        candidatos = list(labels_dir.rglob(nome_arquivo))
        if candidatos:
            txt_path = candidatos[0]
        else:
            print(f"  [aviso] {nome_arquivo} não encontrado em {labels_dir}, pulando.")
            continue

        nome_base = txt_path.stem
        img_path = encontrar_imagem_correspondente(images_dir, nome_base)
        if img_path is None:
            print(f"  [aviso] imagem não encontrada para {nome_base}, pulando.")
            continue

        caixas_mantidas = ler_caixas_mantidas(txt_path, linhas_suspeitas)

        resultado = modelo.predict(source=str(img_path), imgsz=args.imgsz,
                                    conf=args.conf, iou=args.iou_nms, verbose=False)[0]

        sugestoes = []
        if resultado.boxes is not None:
            for box in resultado.boxes:
                xc, yc, w, h = box.xywhn[0].tolist()
                classe = int(box.cls[0].item())
                candidata = (str(classe), xc, yc, w, h)
                if not sobrepoe_alguma(candidata, caixas_mantidas, args.iou_dedup):
                    sugestoes.append(candidata)

        caixas_finais = caixas_mantidas + sugestoes

        if not caixas_finais:
            sem_caixas.append(nome_arquivo)
        else:
            linhas_saida = [
                f"{c} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}" for c, xc, yc, w, h in caixas_finais
            ]
            (saida_dir / "labels" / txt_path.name).write_text("\n".join(linhas_saida) + "\n")

        shutil.copy2(img_path, saida_dir / "images" / img_path.name)

        resumo_contagem.append((nome_arquivo, len(caixas_mantidas), len(sugestoes)))

        if i % 50 == 0 or i == total:
            print(f"  processado {i}/{total}...")

    if sem_caixas:
        (saida_dir / "manual_review_necessaria.txt").write_text("\n".join(sem_caixas))

    total_mantidas = sum(m for _, m, _ in resumo_contagem)
    total_sugeridas = sum(s for _, _, s in resumo_contagem)

    print("\n=== Resumo da geração de pré-anotações ===")
    print(f"Arquivos processados: {len(resumo_contagem)}")
    print(f"Caixas boas mantidas (não sinalizadas): {total_mantidas}")
    print(f"Caixas sugeridas pelo modelo baseline:   {total_sugeridas}")
    print(f"Arquivos sem NENHUMA caixa (precisam de anotação manual completa): {len(sem_caixas)}")
    if sem_caixas:
        print(f"  -> lista salva em: {saida_dir / 'manual_review_necessaria.txt'}")
    print(f"\nResultado salvo em: {saida_dir.resolve()}")
    print("Próximo passo: importe a pasta 'labels' + 'images' no MakeSense.ai como "
          "pré-anotação (formato YOLO) e revise cada imagem manualmente antes de "
          "usar no dataset de treinamento final.")


if __name__ == "__main__":
    main()