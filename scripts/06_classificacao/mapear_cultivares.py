"""
Mapeamento das imagens do conjunto consolidado à cultivar de origem.

O conjunto consolidado reúne imagens de duas cultivares, cuja distinção
foi preservada apenas na organização original dos diretórios. Como a
etapa de classificação da maturação depende dessa informação — o fruto
maduro apresenta coloração vermelha em uma cultivar e amarela na outra —,
faz-se necessário recuperar a correspondência entre os dois conjuntos.

ESTRATÉGIA

A correspondência é estabelecida em duas etapas. Primeiro, por nome de
arquivo, quando preservado. Em seguida, para os casos remanescentes, por
similaridade visual, empregando o mesmo procedimento de hash perceptual
adotado na curadoria do conjunto.

O uso do hash perceptual permite reconhecer imagens correspondentes ainda
que tenham sido renomeadas ou submetidas a recompressão, situação
esperada considerando as sucessivas reorganizações pelas quais o conjunto
passou.

USO

    python mapear_cultivares.py \\
        --dataset_original dataset \\
        --dataset_final dataset_final \\
        --saida cultivares.csv

DEPENDÊNCIAS

    pip install pillow imagehash
"""

import argparse
import csv
from pathlib import Path

import imagehash
from PIL import Image

EXTENSOES = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}


def listar_imagens(diretorio: Path):
    """Percorre o diretório recursivamente, reunindo os arquivos de imagem."""
    if not diretorio.exists():
        return []

    return [
        p for p in diretorio.rglob('*')
        if p.is_file() and p.suffix.lower() in EXTENSOES
    ]


def calcular_hash(caminho: Path):
    try:
        with Image.open(caminho) as img:
            return imagehash.phash(img.convert('RGB'))
    except Exception:
        return None


def similaridade(h1, h2) -> float:
    """Proporção de bits coincidentes entre dois hashes perceptuais."""
    distancia = h1 - h2
    maxima = len(h1.hash) ** 2
    return 1 - (distancia / maxima)


def identificar_split(nome: str):
    nome = nome.lower()
    for split in ('train', 'val', 'test'):
        if nome.startswith(f'{split}_'):
            return split
    return None


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--dataset_original', type=str, required=True,
                        help='Diretório contendo as subpastas por cultivar.')
    parser.add_argument('--dataset_final', type=str, required=True,
                        help='Diretório do conjunto consolidado.')
    parser.add_argument('--cultivares', type=str, nargs='+',
                        default=['amarelas', 'vermelhas'],
                        help='Nomes das subpastas correspondentes às '
                             'cultivares.')
    parser.add_argument('--saida', type=str, default='cultivares.csv')
    parser.add_argument('--limiar', type=float, default=0.90,
                        help='Similaridade mínima para que duas imagens '
                             'sejam consideradas correspondentes.')
    args = parser.parse_args()

    original_dir = Path(args.dataset_original)
    final_dir = Path(args.dataset_final)

    # --- Levantamento do conjunto original, por cultivar ---
    referencias = []

    for cultivar in args.cultivares:
        # A estrutura pode conter as imagens diretamente na pasta da
        # cultivar ou sob um subdiretório de imagens.
        candidatos = [
            original_dir / 'images' / cultivar,
            original_dir / cultivar,
        ]

        encontrado = False
        for base in candidatos:
            imagens = listar_imagens(base)
            if imagens:
                print(f'{cultivar}: {len(imagens)} imagens em {base}')
                referencias.extend((p, cultivar) for p in imagens)
                encontrado = True
                break

        if not encontrado:
            print(f'  [aviso] nenhuma imagem localizada para "{cultivar}"')

    if not referencias:
        raise SystemExit(
            'Nenhuma imagem de referência localizada. Verifique a '
            'estrutura do diretório informado em --dataset_original.'
        )

    # --- Levantamento do conjunto consolidado ---
    alvos = listar_imagens(final_dir)
    print(f'\nConjunto consolidado: {len(alvos)} imagens')

    if not alvos:
        raise SystemExit('Nenhuma imagem localizada no conjunto consolidado.')

    # --- Correspondência por nome ---
    indice_por_nome = {}
    for caminho, cultivar in referencias:
        indice_por_nome.setdefault(caminho.stem, []).append(cultivar)

    resultados = {}
    pendentes = []

    for alvo in alvos:
        cultivares = indice_por_nome.get(alvo.stem)

        if cultivares and len(set(cultivares)) == 1:
            resultados[alvo] = (cultivares[0], 'nome', 1.0)
        else:
            pendentes.append(alvo)

    print(f'Correspondências por nome: {len(resultados)}')
    print(f'Pendentes para comparação visual: {len(pendentes)}')

    # --- Correspondência por similaridade visual ---
    if pendentes:
        print('\nCalculando hashes das imagens de referência...')
        hashes_referencia = []

        for i, (caminho, cultivar) in enumerate(referencias, 1):
            h = calcular_hash(caminho)
            if h is not None:
                hashes_referencia.append((h, cultivar, caminho.name))
            if i % 200 == 0:
                print(f'  {i}/{len(referencias)}')

        print('\nComparando imagens pendentes...')

        for i, alvo in enumerate(pendentes, 1):
            h_alvo = calcular_hash(alvo)

            if h_alvo is None:
                resultados[alvo] = (None, 'falha_leitura', 0.0)
                continue

            melhor_sim = 0.0
            melhor_cultivar = None

            for h_ref, cultivar, _ in hashes_referencia:
                sim = similaridade(h_alvo, h_ref)
                if sim > melhor_sim:
                    melhor_sim = sim
                    melhor_cultivar = cultivar

            if melhor_sim >= args.limiar:
                resultados[alvo] = (melhor_cultivar, 'visual', melhor_sim)
            else:
                resultados[alvo] = (None, 'sem_correspondencia', melhor_sim)

            if i % 50 == 0:
                print(f'  {i}/{len(pendentes)}')

    # --- Registro ---
    linhas = []
    for alvo in sorted(alvos, key=lambda p: p.name):
        cultivar, metodo, sim = resultados.get(
            alvo, (None, 'nao_processado', 0.0)
        )
        linhas.append({
            'imagem': alvo.name,
            'split': identificar_split(alvo.name) or '',
            'cultivar': cultivar or '',
            'metodo': metodo,
            'similaridade': round(sim, 4),
        })

    with open(args.saida, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['imagem', 'split', 'cultivar', 'metodo',
                        'similaridade'],
        )
        writer.writeheader()
        writer.writerows(linhas)

    # --- Resumo ---
    contagem = {}
    for linha in linhas:
        chave = linha['cultivar'] or '(não identificada)'
        contagem[chave] = contagem.get(chave, 0) + 1

    metodos = {}
    for linha in linhas:
        metodos[linha['metodo']] = metodos.get(linha['metodo'], 0) + 1

    print('\n=== Resumo ===')
    print('Cultivar identificada:')
    for chave, valor in sorted(contagem.items()):
        proporcao = valor / len(linhas) * 100
        print(f'  {chave:<22} {valor:>5}  ({proporcao:.1f}%)')

    print('\nMétodo de correspondência:')
    for chave, valor in sorted(metodos.items()):
        print(f'  {chave:<22} {valor:>5}')

    print(f'\nRegistro salvo em: {args.saida}')

    nao_identificadas = contagem.get('(não identificada)', 0)
    if nao_identificadas:
        print(
            f'\n{nao_identificadas} imagens permaneceram sem cultivar '
            'atribuída. Reduzir o limiar de similaridade pode ampliar a '
            'correspondência, ao custo de eventuais atribuições incorretas.'
        )


if __name__ == '__main__':
    main()