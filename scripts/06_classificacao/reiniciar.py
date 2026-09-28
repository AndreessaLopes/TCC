"""
Reinicia a rotulagem, devolvendo os recortes ao diretório de pendentes.

Move de volta para nao_rotulados todos os recortes já classificados e
preserva o registro da sessão anterior sob outro nome, de modo que nenhuma
informação seja perdida. A operação é necessária quando a rotulagem foi
iniciada sob critério diferente do que se pretende aplicar.

USO

    python reiniciar.py --diretorio crops_maturacao

    Opcional:
      --simular     Apenas relata o que seria movido, sem alterar nada.
"""

import argparse
import shutil
from datetime import datetime
from pathlib import Path

CLASSES = ('ideal', 'nao_ideal', 'descartado', 'duvida')
EXTENSOES = {'.jpg', '.jpeg', '.png'}
REGISTRO = 'rotulagem.csv'


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--diretorio', type=str, default='crops_maturacao')
    parser.add_argument('--simular', action='store_true')
    args = parser.parse_args()

    diretorio = Path(args.diretorio)
    pendentes = diretorio / 'nao_rotulados'

    if not pendentes.exists():
        raise SystemExit(f'Diretório não encontrado: {pendentes}')

    total = 0
    conflitos = []

    for classe in CLASSES:
        origem = diretorio / classe
        if not origem.exists():
            continue

        arquivos = [p for p in origem.glob('*') if p.suffix.lower() in EXTENSOES]
        print(f'{classe:12s} {len(arquivos):5d}')

        for arquivo in arquivos:
            destino = pendentes / arquivo.name

            if destino.exists():
                conflitos.append(arquivo.name)
                continue

            if not args.simular:
                shutil.move(str(arquivo), str(destino))
            total += 1

    print()

    if conflitos:
        print(f'Ignorados por já existirem em nao_rotulados: {len(conflitos)}')

    if args.simular:
        print(f'Seriam movidos {total} recortes. Nenhuma alteração realizada.')
        return

    # Preserva o registro anterior
    registro = diretorio / REGISTRO
    if registro.exists():
        marca = datetime.now().strftime('%Y%m%d_%H%M')
        arquivado = diretorio / f'rotulagem_anterior_{marca}.csv'
        registro.rename(arquivado)
        print(f'Registro anterior preservado em {arquivado.name}')

    restantes = len([p for p in pendentes.glob('*')
                     if p.suffix.lower() in EXTENSOES])

    print(f'Movidos {total} recortes de volta.')
    print(f'Pendentes agora: {restantes}')
    print()
    print('Substitua o prerotulagem.csv e execute rotulador.py.')


if __name__ == '__main__':
    main()