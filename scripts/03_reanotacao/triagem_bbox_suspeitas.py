"""
Triagem de bounding boxes suspeitas em dataset YOLO (grão de café).

Com base na análise anterior (histograma bimodal), este script classifica
cada anotação em três categorias por tamanho de bounding box:

    - NORMAL        : área <  limiar_cacho                 (grão individual, ok)
    - PROVAVEL_CACHO: limiar_cacho <= área < limiar_erro    (provável cacho/grupo)
    - PROVAVEL_ERRO  : área >= limiar_erro                  (provável erro de anotação,
                                                              ex.: caixa cobrindo a imagem toda)

Os limiares default (0.15 e 0.95) foram escolhidos com base na distribuição
observada (pico de "grão" em ~0.0075, pico de "cacho" em ~0.294, e casos de
área ~1.0 isolados). Ajuste com --limiar_cacho e --limiar_erro se necessário.

O script NÃO apaga nem modifica nada automaticamente — ele apenas:
  1. Lista todos os arquivos .txt que contêm ao menos uma caixa suspeita.
  2. Copia (não move) os .txt e, se você informar --images_dir, também as
     imagens correspondentes, para pastas de revisão separadas.
  3. Gera um relatório CSV com o detalhe de cada caixa suspeita encontrada.

Uso básico (só listar, sem copiar nada):
    python triagem_bbox_suspeitas.py --labels_dir dataset_24_06/labels

Uso completo (copiar labels + imagens para revisão):
    python triagem_bbox_suspeitas.py \
        --labels_dir dataset_24_06/labels \
        --images_dir dataset_24_06/images \
        --saida_dir revisao_anotacoes
"""

import argparse
import csv
import shutil
from pathlib import Path


CATEGORIAS = ("provavel_erro", "provavel_cacho")


def encontrar_imagem_correspondente(images_dir: Path, nome_base: str):
    """Procura a imagem correspondente ao .txt, testando extensões comuns."""
    for ext in (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"):
        candidato = images_dir / f"{nome_base}{ext}"
        if candidato.exists():
            return candidato
    # busca recursiva como fallback (caso images_dir tenha subpastas train/val/test)
    encontrados = list(images_dir.rglob(f"{nome_base}.*"))
    return encontrados[0] if encontrados else None


def classificar_arquivo(txt_path: Path, limiar_cacho: float, limiar_erro: float):
    """
    Lê um arquivo de anotação YOLO e retorna:
        categoria_do_arquivo: None | "provavel_cacho" | "provavel_erro"
        detalhes: lista de dicts com cada caixa suspeita encontrada
    A categoria do arquivo é a mais severa entre suas caixas
    (provavel_erro > provavel_cacho > normal).
    """
    pior_categoria = None
    detalhes = []

    with open(txt_path, "r") as f:
        linhas = [l.strip() for l in f if l.strip()]

    for i, linha in enumerate(linhas):
        partes = linha.split()
        if len(partes) < 5:
            continue
        try:
            classe, xc, yc, w, h = partes[:5]
            w, h = float(w), float(h)
        except ValueError:
            continue

        area = w * h

        if area >= limiar_erro:
            categoria = "provavel_erro"
        elif area >= limiar_cacho:
            categoria = "provavel_cacho"
        else:
            categoria = None

        if categoria:
            detalhes.append(
                {
                    "arquivo": txt_path.name,
                    "linha": i + 1,
                    "classe": classe,
                    "largura": w,
                    "altura": h,
                    "area": round(area, 6),
                    "categoria": categoria,
                }
            )
            if categoria == "provavel_erro":
                pior_categoria = "provavel_erro"
            elif categoria == "provavel_cacho" and pior_categoria != "provavel_erro":
                pior_categoria = "provavel_cacho"

    return pior_categoria, detalhes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels_dir", type=str, required=True,
                        help="Diretório raiz com os .txt de anotação YOLO (busca recursiva).")
    parser.add_argument("--images_dir", type=str, default=None,
                        help="Diretório raiz das imagens correspondentes (opcional, para copiar junto).")
    parser.add_argument("--saida_dir", type=str, default="revisao_anotacoes",
                        help="Pasta onde os arquivos suspeitos serão copiados para revisão.")
    parser.add_argument("--limiar_cacho", type=float, default=0.15,
                        help="Área normalizada mínima para classificar como 'provável cacho'.")
    parser.add_argument("--limiar_erro", type=float, default=0.95,
                        help="Área normalizada mínima para classificar como 'provável erro de anotação'.")
    parser.add_argument("--copiar", action="store_true",
                        help="Se informado, copia os arquivos suspeitos para --saida_dir. "
                             "Sem essa flag, o script só gera o relatório CSV e imprime o resumo.")
    args = parser.parse_args()

    labels_dir = Path(args.labels_dir)
    images_dir = Path(args.images_dir) if args.images_dir else None
    saida_dir = Path(args.saida_dir)

    txt_files = sorted(labels_dir.rglob("*.txt"))
    if not txt_files:
        raise FileNotFoundError(f"Nenhum .txt encontrado em {labels_dir}")

    todos_detalhes = []
    contagem = {"provavel_erro": 0, "provavel_cacho": 0}
    arquivos_por_categoria = {"provavel_erro": [], "provavel_cacho": []}

    for txt_path in txt_files:
        categoria, detalhes = classificar_arquivo(txt_path, args.limiar_cacho, args.limiar_erro)
        todos_detalhes.extend(detalhes)
        if categoria:
            contagem[categoria] += 1
            arquivos_por_categoria[categoria].append(txt_path)

    # Relatório CSV com todas as caixas suspeitas
    csv_path = saida_dir / "relatorio_bboxes_suspeitas.csv" if args.copiar else Path("relatorio_bboxes_suspeitas.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["arquivo", "linha", "classe", "largura", "altura", "area", "categoria"]
        )
        writer.writeheader()
        writer.writerows(todos_detalhes)

    print("=== Resumo da triagem ===")
    print(f"Total de arquivos de anotação analisados: {len(txt_files)}")
    print(f"Arquivos com caixa 'provável erro' (área >= {args.limiar_erro}): {contagem['provavel_erro']}")
    print(f"Arquivos com caixa 'provável cacho' ({args.limiar_cacho} <= área < {args.limiar_erro}): {contagem['provavel_cacho']}")
    print(f"Relatório detalhado salvo em: {csv_path}")

    if not args.copiar:
        print("\n(Rode novamente com --copiar --images_dir <pasta_imagens> para "
              "organizar os arquivos suspeitos em pastas de revisão.)")
        return

    # Copia labels (e imagens, se disponíveis) para pastas de revisão
    for categoria in CATEGORIAS:
        destino_labels = saida_dir / categoria / "labels"
        destino_labels.mkdir(parents=True, exist_ok=True)
        destino_imagens = None
        if images_dir:
            destino_imagens = saida_dir / categoria / "images"
            destino_imagens.mkdir(parents=True, exist_ok=True)

        for txt_path in arquivos_por_categoria[categoria]:
            shutil.copy2(txt_path, destino_labels / txt_path.name)

            if images_dir:
                nome_base = txt_path.stem
                img_path = encontrar_imagem_correspondente(images_dir, nome_base)
                if img_path:
                    shutil.copy2(img_path, destino_imagens / img_path.name)
                else:
                    print(f"  [aviso] imagem não encontrada para {nome_base}")

    print(f"\nArquivos copiados para revisão em: {saida_dir.resolve()}")
    print("Estrutura gerada:")
    print(f"  {saida_dir}/provavel_erro/labels (+ images, se informado)")
    print(f"  {saida_dir}/provavel_cacho/labels (+ images, se informado)")
    print(f"  {saida_dir}/relatorio_bboxes_suspeitas.csv")


if __name__ == "__main__":
    main()