"""
Extração dos recortes de grãos para a etapa de classificação.

Percorre as imagens do conjunto consolidado, recorta cada fruto conforme
as anotações existentes e organiza os recortes em diretórios destinados à
rotulagem manual quanto ao estágio de maturação.

IDENTIFICAÇÃO DA CULTIVAR

O nome de cada recorte incorpora a cultivar de origem, recuperada pelo
mapeamento produzido por `mapear_cultivares.py`. Essa informação é
necessária à rotulagem, uma vez que o fruto maduro apresenta coloração
vermelha em uma cultivar e amarela na outra: um fruto de tonalidade
amarela corresponde ao estágio cereja na cultivar amarela e ao estágio
verde-cana na cultivar vermelha.

CRITÉRIOS DE SELEÇÃO

Nem toda região anotada produz um recorte adequado à rotulagem. São
descartadas:

  - Regiões cujas dimensões originais sejam reduzidas, nas quais o fruto
    não apresenta definição suficiente para a distinção do estágio de
    maturação.

  - Regiões de área elevada em relação à imagem, correspondentes aos
    casos residuais de anotação agrupada, nos quais uma única caixa
    delimita mais de um fruto.

  - Regiões com baixa nitidez, avaliada pela variância do operador
    laplaciano. Recortes desfocados impedem a identificação segura da
    coloração e das bordas do fruto.

USO

    python extrair_crops.py \\
        --dataset_dir dataset_final \\
        --cultivares cultivares.csv \\
        --saida_dir crops_maturacao \\
        --amostra 2000

DEPENDÊNCIAS

    pip install pillow numpy
"""

import argparse
import csv
import random
from pathlib import Path

import numpy as np
from PIL import Image

EXTENSOES = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')


def carregar_cultivares(csv_path: Path):
    """Lê o mapeamento entre imagens e cultivares."""
    mapa = {}

    with open(csv_path, 'r', encoding='utf-8') as f:
        for linha in csv.DictReader(f):
            cultivar = linha.get('cultivar', '').strip()
            if cultivar:
                # Registra tanto o nome completo quanto sem extensão,
                # acomodando variações de referência.
                nome = linha['imagem']
                mapa[nome] = cultivar
                mapa[Path(nome).stem] = cultivar

    return mapa


def localizar_imagem(images_dir: Path, nome_base: str):
    for ext in EXTENSOES:
        candidato = images_dir / f'{nome_base}{ext}'
        if candidato.exists():
            return candidato

    encontrados = list(images_dir.rglob(f'{nome_base}.*'))
    return encontrados[0] if encontrados else None


def ler_anotacoes(txt_path: Path):
    """Lê um arquivo de anotação no formato YOLO."""
    caixas = []

    with open(txt_path, 'r') as f:
        for linha in f:
            partes = linha.strip().split()
            if len(partes) < 5:
                continue
            try:
                _, xc, yc, w, h = partes[:5]
                caixas.append((float(xc), float(yc), float(w), float(h)))
            except ValueError:
                continue

    return caixas


def recortar(imagem: Image.Image, caixa, margem: float):
    """
    Converte uma anotação normalizada em recorte, aplicando margem
    proporcional ao redor da região delimitada.
    """
    largura, altura = imagem.size
    xc, yc, w, h = caixa

    box_w = w * largura * (1 + margem)
    box_h = h * altura * (1 + margem)

    esquerda = max(0, int((xc * largura) - box_w / 2))
    superior = max(0, int((yc * altura) - box_h / 2))
    direita = min(largura, int((xc * largura) + box_w / 2))
    inferior = min(altura, int((yc * altura) + box_h / 2))

    if direita <= esquerda or inferior <= superior:
        return None

    return imagem.crop((esquerda, superior, direita, inferior))


def nitidez(imagem: Image.Image) -> float:
    """
    Estima a nitidez pela variância do operador laplaciano.

    Imagens desfocadas apresentam transições suaves entre pixels
    vizinhos, resultando em variância reduzida da segunda derivada.
    """
    cinza = np.asarray(imagem.convert('L'), dtype=np.float32)

    if cinza.shape[0] < 3 or cinza.shape[1] < 3:
        return 0.0

    laplaciano = (
        cinza[:-2, 1:-1]
        + cinza[2:, 1:-1]
        + cinza[1:-1, :-2]
        + cinza[1:-1, 2:]
        - 4 * cinza[1:-1, 1:-1]
    )

    return float(laplaciano.var())


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--dataset_dir', type=str, required=True)
    parser.add_argument('--cultivares', type=str, required=True,
                        help='Arquivo produzido por mapear_cultivares.py')
    parser.add_argument('--saida_dir', type=str, default='crops_maturacao')
    parser.add_argument('--splits', type=str, nargs='+',
                        default=['train', 'val', 'test'])

    parser.add_argument('--margem', type=float, default=0.20)
    parser.add_argument('--tamanho_saida', type=int, default=128)

    parser.add_argument('--tamanho_minimo', type=int, default=48,
                        help='Dimensão mínima, em pixels, do recorte '
                             'original.')
    parser.add_argument('--area_maxima', type=float, default=0.06,
                        help='Área normalizada máxima da caixa. Valores '
                             'superiores indicam anotação agrupada.')
    parser.add_argument('--nitidez_minima', type=float, default=80.0,
                        help='Variância laplaciana mínima. Recortes com '
                             'valor inferior são considerados desfocados.')

    parser.add_argument('--amostra', type=int, default=None)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--balancear', action='store_true',
                        help='Distribui a amostra igualmente entre as '
                             'cultivares.')
    args = parser.parse_args()

    random.seed(args.seed)

    dataset_dir = Path(args.dataset_dir)
    saida_dir = Path(args.saida_dir)
    cultivares = carregar_cultivares(Path(args.cultivares))

    print(f'Mapeamento de cultivares: {len(cultivares) // 2} imagens')

    pendentes_dir = saida_dir / 'nao_rotulados'
    pendentes_dir.mkdir(parents=True, exist_ok=True)

    for classe in ('ideal', 'nao_ideal', 'descartado'):
        (saida_dir / classe).mkdir(parents=True, exist_ok=True)

    # --- Levantamento das regiões ---
    regioes = []
    sem_cultivar = set()

    for split in args.splits:
        labels_dir = dataset_dir / split / 'labels'
        images_dir = dataset_dir / split / 'images'

        if not labels_dir.exists():
            print(f'  [aviso] {labels_dir} não encontrado, ignorando.')
            continue

        for txt_path in sorted(labels_dir.glob('*.txt')):
            img_path = localizar_imagem(images_dir, txt_path.stem)
            if img_path is None:
                continue

            cultivar = cultivares.get(img_path.name) or \
                cultivares.get(txt_path.stem)

            if cultivar is None:
                sem_cultivar.add(txt_path.stem)
                continue

            for indice, caixa in enumerate(ler_anotacoes(txt_path)):
                area = caixa[2] * caixa[3]

                # Descarta anotações agrupadas antes da abertura da imagem
                if area > args.area_maxima:
                    continue

                regioes.append(
                    (img_path, txt_path.stem, indice, caixa, split, cultivar)
                )

    print(f'Regiões elegíveis: {len(regioes)}')

    if sem_cultivar:
        print(f'  [aviso] {len(sem_cultivar)} imagens sem cultivar '
              'identificada foram ignoradas.')

    # --- Amostragem ---
    if args.amostra and args.amostra < len(regioes):
        if args.balancear:
            por_cultivar = {}
            for r in regioes:
                por_cultivar.setdefault(r[5], []).append(r)

            cota = args.amostra // len(por_cultivar)
            selecionadas = []

            for cultivar, lista in por_cultivar.items():
                escolhidas = random.sample(lista, min(cota, len(lista)))
                selecionadas.extend(escolhidas)
                print(f'  {cultivar}: {len(escolhidas)} regiões')

            regioes = selecionadas
        else:
            # Amostra ampliada, compensando os descartes por nitidez
            # aplicados durante a extração.
            regioes = random.sample(
                regioes, min(int(args.amostra * 1.6), len(regioes))
            )

    regioes.sort(key=lambda r: str(r[0]))

    # --- Extração ---
    registros = []
    descartes = {'dimensao': 0, 'nitidez': 0, 'invalido': 0}

    imagem_atual = None
    caminho_atual = None
    limite = args.amostra or len(regioes)

    for img_path, nome_base, indice, caixa, split, cultivar in regioes:
        if len(registros) >= limite:
            break

        if caminho_atual != img_path:
            if imagem_atual is not None:
                imagem_atual.close()
            imagem_atual = Image.open(img_path).convert('RGB')
            caminho_atual = img_path

        recorte = recortar(imagem_atual, caixa, args.margem)

        if recorte is None:
            descartes['invalido'] += 1
            continue

        if min(recorte.size) < args.tamanho_minimo:
            descartes['dimensao'] += 1
            continue

        valor_nitidez = nitidez(recorte)

        if valor_nitidez < args.nitidez_minima:
            descartes['nitidez'] += 1
            continue

        largura_original, altura_original = recorte.size

        recorte = recorte.resize(
            (args.tamanho_saida, args.tamanho_saida), Image.LANCZOS
        )

        # A cultivar antecede o nome, permitindo que a rotulagem seja
        # realizada com conhecimento do contexto e que os recortes sejam
        # ordenados por cultivar no gerenciador de arquivos.
        nome_saida = f'{cultivar}_{nome_base}_{indice:03d}.jpg'
        recorte.save(pendentes_dir / nome_saida, quality=92)

        registros.append({
            'arquivo': nome_saida,
            'cultivar': cultivar,
            'imagem_origem': img_path.name,
            'split_origem': split,
            'indice_caixa': indice,
            'area_normalizada': round(caixa[2] * caixa[3], 6),
            'largura_original': largura_original,
            'altura_original': altura_original,
            'nitidez': round(valor_nitidez, 1),
        })

    if imagem_atual is not None:
        imagem_atual.close()

    # --- Registro ---
    csv_path = saida_dir / 'origem_recortes.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['arquivo', 'cultivar', 'imagem_origem',
                        'split_origem', 'indice_caixa', 'area_normalizada',
                        'largura_original', 'altura_original', 'nitidez'],
        )
        writer.writeheader()
        writer.writerows(registros)

    # --- Resumo ---
    por_cultivar = {}
    for r in registros:
        por_cultivar[r['cultivar']] = por_cultivar.get(r['cultivar'], 0) + 1

    print('\n=== Resumo ===')
    print(f'Recortes gravados: {len(registros)}')
    for cultivar, quantidade in sorted(por_cultivar.items()):
        print(f'  {cultivar:<14}{quantidade:>6}')

    print('\nDescartes:')
    print(f'  dimensão insuficiente  {descartes["dimensao"]:>6}')
    print(f'  nitidez insuficiente   {descartes["nitidez"]:>6}')
    print(f'  região inválida        {descartes["invalido"]:>6}')

    print(f'\nDiretório: {saida_dir.resolve()}')
    print(f'Registro: {csv_path}')
    print(
        '\nOs recortes encontram-se em "nao_rotulados", nomeados com a '
        'cultivar de origem. A rotulagem consiste em movê-los para os '
        'diretórios "ideal", "nao_ideal" ou "descartado".'
    )
    print(
        '\nNa cultivar vermelha, o estágio cereja apresenta coloração '
        'vermelha; na cultivar amarela, coloração amarela. Recortes cuja '
        'classificação permaneça indefinida devem ser encaminhados a '
        '"descartado".'
    )


if __name__ == '__main__':
    main()