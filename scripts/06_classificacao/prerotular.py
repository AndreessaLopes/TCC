
"""
Pré-rotulagem cromática dos recortes de frutos de café.

Atribui a cada recorte um escore contínuo de maturação, calculado a partir
da distribuição de matiz na região central da imagem, e propõe a classe
"ideal" aos recortes cuja assinatura cromática é inequívoca. Nenhum arquivo
é movido: a saída é um registro em disco que a ferramenta de rotulagem
consome para ordenar a fila e apresentar a proposta ao anotador.

FUNDAMENTO

O estágio cereja apresenta coloração saturada e específica da cultivar —
vermelha na cultivar vermelha, amarela na cultivar amarela — que se destaca
com nitidez da folhagem circundante. Essa separação cromática é suficiente
para uma proposta automática confiável.

Os estágios verde e verde-cana, em contrapartida, ocupam faixa de matiz
praticamente coincidente com a das folhas de café. A distinção entre um
fruto verde e a folhagem de fundo depende de forma e textura, não de cor,
e não é recuperável por análise cromática. Por essa razão nenhuma proposta
é emitida para a classe não ideal: esses recortes são encaminhados à
inspeção visual, ordenados pelo escore, de modo que recortes de aparência
semelhante permaneçam adjacentes na fila.

ESCORE

    escore = fração de pixels na cor madura da cultivar
             − fração de pixels na faixa verde

Varia de +1 (integralmente maduro) a −1 (integralmente verde). Recortes sem
cor dominante — desfocados ou subexpostos — recebem escore indefinido e são
posicionados ao final da fila.

USO

    python prerotular.py --diretorio crops_maturacao

    Opcional:
      --limiar 0.55       Escore mínimo para propor a classe ideal.
      --contato           Gera folhas de contato para conferência.

SAÍDA

    crops_maturacao/prerotulagem.csv

DEPENDÊNCIAS

    pip install pillow numpy
"""

import argparse
import csv
from pathlib import Path

import numpy as np
from PIL import Image

EXTENSOES = {'.jpg', '.jpeg', '.png'}

# Faixas de matiz, em graus
FAIXA_VERMELHO = (330, 20)   # envolve a origem
FAIXA_LARANJA = (20, 48)
FAIXA_AMARELO = (48, 72)
FAIXA_VERDE = (72, 170)

SATURACAO_MINIMA = 0.28
VALOR_MINIMO = 0.16
FRACAO_UTIL_MINIMA = 0.12
RAIO_NUCLEO = 0.50

# Fração cromática mínima exigida para emitir proposta. Recortes cuja cor
# se concentra em poucos pixels — tipicamente reflexos sobre folhagem —
# produzem escore elevado sem que haja fruto presente.
FRACAO_UTIL_PROPOSTA = 0.30

ESCORE_INDEFINIDO = -9.0


def converter_hsv(arr):
    """Converte um arranjo RGB normalizado em matiz, saturação e valor."""
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    maximo = arr.max(axis=-1)
    minimo = arr.min(axis=-1)
    amplitude = maximo - minimo

    matiz = np.zeros_like(maximo)
    valido = amplitude > 1e-6

    indice = (maximo == r) & valido
    matiz[indice] = (60 * ((g[indice] - b[indice]) / amplitude[indice])) % 360

    indice = (maximo == g) & valido
    matiz[indice] = 60 * ((b[indice] - r[indice]) / amplitude[indice]) + 120

    indice = (maximo == b) & valido
    matiz[indice] = 60 * ((r[indice] - g[indice]) / amplitude[indice]) + 240

    saturacao = np.divide(
        amplitude, maximo, out=np.zeros_like(maximo), where=maximo > 1e-6
    )

    return matiz, saturacao, maximo


def medir(caminho: Path):
    """Extrai as frações de matiz da região central do recorte."""
    try:
        imagem = Image.open(caminho).convert('RGB')
    except Exception:
        return None

    arr = np.asarray(imagem, dtype=np.float32) / 255.0
    altura, largura = arr.shape[:2]

    matiz, saturacao, valor = converter_hsv(arr)

    # Núcleo central: onde o fruto anotado se concentra
    linhas, colunas = np.mgrid[0:altura, 0:largura]
    raio = np.sqrt(
        ((linhas - altura / 2) / (altura / 2)) ** 2
        + ((colunas - largura / 2) / (largura / 2)) ** 2
    )
    nucleo = raio < RAIO_NUCLEO

    util = nucleo & (saturacao > SATURACAO_MINIMA) & (valor > VALOR_MINIMO)
    fracao = float(util.mean() / max(nucleo.mean(), 1e-6))

    if fracao < FRACAO_UTIL_MINIMA:
        return None

    matiz_util = matiz[util]
    valor_util = valor[util]

    return {
        'fracao_util': fracao,
        'vermelho': float(((matiz_util < FAIXA_VERMELHO[1])
                           | (matiz_util > FAIXA_VERMELHO[0])).mean()),
        'laranja': float(((matiz_util >= FAIXA_LARANJA[0])
                          & (matiz_util < FAIXA_LARANJA[1])).mean()),
        'amarelo': float(((matiz_util >= FAIXA_AMARELO[0])
                          & (matiz_util < FAIXA_AMARELO[1])).mean()),
        'verde': float(((matiz_util >= FAIXA_VERDE[0])
                        & (matiz_util < FAIXA_VERDE[1])).mean()),
        'escuro': float((valor_util < 0.33).mean()),
    }


def calcular_escore(medidas, cultivar):
    """Retorna o escore de maturação e as frações que o compõem."""
    if medidas is None:
        return ESCORE_INDEFINIDO, 0.0, 0.0

    if cultivar == 'vermelhas':
        # O laranja participa com peso reduzido: é transição para o cereja
        maduro = medidas['vermelho'] + 0.6 * medidas['laranja']
    else:
        maduro = medidas['laranja'] + medidas['amarelo']

    verde = medidas['verde']
    escore = float(np.clip(maduro - verde, -1.0, 1.0))

    return escore, maduro, verde


def propor(escore, maduro, fracao_util, limiar):
    """Emite proposta apenas quando a assinatura cromática é inequívoca."""
    if escore >= limiar and maduro >= 0.45 \
            and fracao_util >= FRACAO_UTIL_PROPOSTA:
        return 'ideal'
    return ''


def gerar_folha_contato(registros, destino, titulo_campo, quantidade=30):
    """Gera uma folha de contato amostrada ao longo da ordenação."""
    from PIL import ImageDraw

    if not registros:
        return

    passo = max(1, (len(registros) - 1) // max(quantidade - 1, 1))
    amostra = registros[::passo][:quantidade]

    colunas, lado = 6, 128
    linhas = (len(amostra) + colunas - 1) // colunas

    folha = Image.new('RGB', (colunas * lado, linhas * (lado + 14)), (25, 25, 25))
    desenho = ImageDraw.Draw(folha)

    for i, registro in enumerate(amostra):
        x = (i % colunas) * lado
        y = (i // colunas) * (lado + 14)
        try:
            folha.paste(Image.open(registro['caminho']).resize((lado, lado)), (x, y))
        except Exception:
            continue
        desenho.text((x + 2, y + lado + 1), registro[titulo_campo][:20], fill='white')

    folha.save(destino)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--diretorio', type=str, default='crops_maturacao',
                        help='Diretório contendo a subpasta nao_rotulados.')
    parser.add_argument('--limiar', type=float, default=0.55,
                        help='Escore mínimo para propor a classe ideal.')
    parser.add_argument('--contato', action='store_true',
                        help='Gera folhas de contato para conferência.')
    args = parser.parse_args()

    diretorio = Path(args.diretorio)
    pendentes = diretorio / 'nao_rotulados'

    if not pendentes.exists():
        raise SystemExit(
            f'Diretório não encontrado: {pendentes}\n'
            'Execute extrair_crops.py antes da pré-rotulagem.'
        )

    arquivos = sorted(
        p for p in pendentes.glob('*') if p.suffix.lower() in EXTENSOES
    )

    if not arquivos:
        raise SystemExit(f'Nenhum recorte encontrado em {pendentes}')

    print(f'Recortes encontrados: {len(arquivos)}')
    print('Analisando...')

    registros = []
    for i, caminho in enumerate(arquivos, 1):
        cultivar = caminho.name.split('_')[0]
        medidas = medir(caminho)
        escore, maduro, verde = calcular_escore(medidas, cultivar)
        fracao_util = medidas['fracao_util'] if medidas else 0.0

        registros.append({
            'caminho': caminho,
            'arquivo': caminho.name,
            'cultivar': cultivar,
            'escore': escore,
            'maduro': maduro,
            'verde': verde,
            'proposta': propor(escore, maduro, fracao_util, args.limiar),
            'rotulo': f'{cultivar[:3]} {escore:+.2f}',
        })

        if i % 250 == 0:
            print(f'  {i}/{len(arquivos)}')

    # Ordenação decrescente: recortes semelhantes tornam-se adjacentes
    registros.sort(key=lambda r: -r['escore'])

    saida = diretorio / 'prerotulagem.csv'
    with open(saida, 'w', newline='', encoding='utf-8') as f:
        escritor = csv.writer(f)
        escritor.writerow(
            ['ordem', 'arquivo', 'cultivar', 'escore', 'frac_maduro',
             'frac_verde', 'proposta']
        )
        for ordem, r in enumerate(registros, 1):
            escritor.writerow([
                ordem, r['arquivo'], r['cultivar'],
                f"{r['escore']:.4f}", f"{r['maduro']:.4f}",
                f"{r['verde']:.4f}", r['proposta'],
            ])

    propostos = sum(1 for r in registros if r['proposta'] == 'ideal')
    indefinidos = sum(1 for r in registros if r['escore'] == ESCORE_INDEFINIDO)

    print()
    print('=' * 52)
    print(f'Total analisado          {len(registros):5d}')
    print(f'Proposta "ideal"         {propostos:5d}'
          f'  ({propostos / len(registros) * 100:.1f}%)')
    print(f'Sem proposta             {len(registros) - propostos:5d}'
          f'  ({(len(registros) - propostos) / len(registros) * 100:.1f}%)')
    print(f'  dos quais indefinidos  {indefinidos:5d}')
    print('=' * 52)
    print(f'\nRegistro gravado em {saida}')
    print('Execute rotulador.py no mesmo diretório para revisar.')

    if args.contato:
        gerar_folha_contato(registros, diretorio / 'contato_ordenado.png',
                            'rotulo')
        print(f'Folha de contato em {diretorio / "contato_ordenado.png"}')


if __name__ == '__main__':
    main()