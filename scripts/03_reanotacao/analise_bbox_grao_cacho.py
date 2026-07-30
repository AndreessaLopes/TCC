"""
Análise de distribuição de tamanho das bounding boxes em um dataset YOLO.

Objetivo: identificar se há mistura de anotações "grão individual" (caixas
pequenas) e "cacho" (caixas grandes envolvendo vários frutos), o que pode
prejudicar o treinamento de detecção de objetos com classe única.

Como usar:
    python analise_bbox_grao_cacho.py --labels_dir /caminho/para/labels

Estrutura esperada: um diretório contendo arquivos .txt no formato YOLO,
um por imagem, com linhas: <classe> <x_center> <y_center> <largura> <altura>
(todos os valores normalizados entre 0 e 1).

Se as anotações estiverem em subpastas (train/val/test), passe o diretório
raiz que contém todas elas — o script varre recursivamente.
"""

import argparse
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def coletar_bboxes(labels_dir: Path):
    """Lê todos os .txt YOLO e retorna listas de área, largura e altura normalizadas."""
    areas, larguras, alturas, arquivos_por_box = [], [], [], []

    txt_files = list(labels_dir.rglob("*.txt"))
    if not txt_files:
        raise FileNotFoundError(
            f"Nenhum arquivo .txt encontrado em {labels_dir}. "
            "Confira o caminho informado."
        )

    for txt_path in txt_files:
        with open(txt_path, "r") as f:
            linhas = [l.strip() for l in f if l.strip()]

        for linha in linhas:
            partes = linha.split()
            if len(partes) < 5:
                continue  # linha malformada, ignora
            try:
                _, _, _, w, h = partes[:5]
                w, h = float(w), float(h)
            except ValueError:
                continue

            area = w * h
            areas.append(area)
            larguras.append(w)
            alturas.append(h)
            arquivos_por_box.append(txt_path.name)

    return (
        np.array(areas),
        np.array(larguras),
        np.array(alturas),
        arquivos_por_box,
    )


def resumo_estatistico(areas: np.ndarray):
    print("\n=== Estatísticas de área das bounding boxes (normalizada) ===")
    print(f"Total de caixas analisadas: {len(areas)}")
    print(f"Média:            {areas.mean():.6f}")
    print(f"Mediana:          {np.median(areas):.6f}")
    print(f"Desvio padrão:    {areas.std():.6f}")
    print(f"Mínimo:           {areas.min():.6f}")
    print(f"Máximo:           {areas.max():.6f}")
    print(f"Percentil 90:     {np.percentile(areas, 90):.6f}")
    print(f"Percentil 99:     {np.percentile(areas, 99):.6f}")


def detectar_bimodalidade(areas: np.ndarray, n_bins: int = 60):
    """
    Heurística simples: monta o histograma em escala log e verifica se
    existem dois picos (modas) bem separados, o que sugere duas populações
    distintas de tamanho de objeto (ex.: grão vs cacho).
    """
    log_areas = np.log10(areas[areas > 0])
    hist, edges = np.histogram(log_areas, bins=n_bins)

    # Suavização simples (média móvel) para reduzir ruído no histograma
    janela = 3
    hist_suave = np.convolve(hist, np.ones(janela) / janela, mode="same")

    # Encontra picos locais: pontos maiores que os vizinhos imediatos
    picos = []
    for i in range(1, len(hist_suave) - 1):
        if hist_suave[i] > hist_suave[i - 1] and hist_suave[i] > hist_suave[i + 1]:
            if hist_suave[i] > 0.1 * hist_suave.max():  # ignora picos irrelevantes
                picos.append((edges[i], hist_suave[i]))

    print("\n=== Verificação de bimodalidade (heurística) ===")
    if len(picos) >= 2:
        print(f"Foram encontrados {len(picos)} picos na distribuição de área (log10):")
        for centro, altura in picos:
            area_aprox = 10 ** centro
            print(f"  - pico em área ~ {area_aprox:.5f} (contagem suavizada: {altura:.1f})")
        print(
            "\n>> Isso é um indício de que há pelo menos duas populações de "
            "tamanho de objeto no dataset (ex.: grão individual vs cacho). "
            "Recomenda-se inspecionar visualmente as imagens nos extremos "
            "da distribuição (ver seção de exemplos abaixo)."
        )
    else:
        print(
            "Não foi detectada bimodalidade clara pela heurística. "
            "Ainda assim, vale checar o histograma gerado visualmente, "
            "pois a heurística pode não capturar todos os casos."
        )


def listar_exemplos_extremos(areas, arquivos, top_n=15):
    """Lista os arquivos com as maiores caixas (prováveis cachos) para inspeção manual."""
    idx_ordenado = np.argsort(areas)[::-1]
    print(f"\n=== Top {top_n} maiores bounding boxes (prováveis 'cachos') ===")
    vistos = set()
    count = 0
    for i in idx_ordenado:
        nome = arquivos[i]
        if nome in vistos:
            continue
        vistos.add(nome)
        print(f"  {nome}  -> área normalizada = {areas[i]:.5f}")
        count += 1
        if count >= top_n:
            break


def plotar_histograma(areas: np.ndarray, saida: Path):
    plt.figure(figsize=(9, 5))
    plt.hist(np.log10(areas[areas > 0]), bins=60, color="#3b7dd8", edgecolor="black")
    plt.xlabel("log10(área normalizada da bounding box)")
    plt.ylabel("Número de caixas")
    plt.title("Distribuição de tamanho das bounding boxes (escala log)")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(saida, dpi=150)
    print(f"\nHistograma salvo em: {saida}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--labels_dir",
        type=str,
        required=True,
        help="Diretório contendo os arquivos .txt de anotação YOLO (busca recursiva).",
    )
    parser.add_argument(
        "--saida_grafico",
        type=str,
        default="histograma_bboxes.png",
        help="Caminho do arquivo de imagem para salvar o histograma.",
    )
    parser.add_argument(
        "--top_n",
        type=int,
        default=15,
        help="Quantidade de exemplos extremos (maiores caixas) a listar.",
    )
    args = parser.parse_args()

    labels_dir = Path(args.labels_dir)
    areas, larguras, alturas, arquivos = coletar_bboxes(labels_dir)

    resumo_estatistico(areas)
    detectar_bimodalidade(areas)
    listar_exemplos_extremos(areas, arquivos, top_n=args.top_n)
    plotar_histograma(areas, Path(args.saida_grafico))


if __name__ == "__main__":
    main()