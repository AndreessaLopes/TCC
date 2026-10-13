"""
Gera as figuras do capítulo de resultados do experimento em dispositivo móvel.

Lê os arquivos de lote exportados pela aplicação e produz três figuras em
PDF (vetorial, para inclusão no LaTeX) e PNG (para conferência).

USO

    python gerar_figuras.py --entrada metricas --saida figuras

DEPENDÊNCIAS

    pip install matplotlib
"""

import argparse
import csv
import re
import statistics as st
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Paleta categórica de dois níveis, verificada quanto à separação sob
# deficiência de visão de cores (ΔE 24,6 protanopia; 35,7 visão normal).
COR_CPU = '#1f77b4'
COR_GPU = '#ff7f0e'
TINTA = '#222222'
TINTA_FRACA = '#666666'
GRADE = '#dddddd'

plt.rcParams.update({
    'font.size': 9,
    'axes.edgecolor': TINTA_FRACA,
    'axes.labelcolor': TINTA,
    'text.color': TINTA,
    'xtick.color': TINTA_FRACA,
    'ytick.color': TINTA_FRACA,
    'axes.linewidth': 0.8,
    'figure.dpi': 110,
})


def ler_lote(caminho):
    """Extrai o cabeçalho e as medições válidas de um arquivo de lote."""
    cabecalho, medicoes = {}, []
    with open(caminho, encoding='utf-8') as f:
        for linha in f:
            if linha.startswith('#'):
                m = re.match(r'# ([^:]+): (.+)', linha.strip())
                if m:
                    cabecalho[m.group(1)] = m.group(2)
            elif linha.strip() and not linha.startswith('arquivo'):
                c = linha.strip().split(',')
                if c[7] != '1':                       # descarta outliers
                    medicoes.append({
                        'pre': float(c[2]), 'inf': float(c[3]),
                        'pos': float(c[4]), 'tot': float(c[5]),
                    })
    return cabecalho, medicoes


def carregar(entrada):
    registros = {}
    for p in sorted(Path(entrada).glob('*.csv')):
        cab, L = ler_lote(p)
        arq, prec, deleg = cab['Configuracao'].split(' · ')
        n = len(L) // 3
        registros[(arq, prec, deleg)] = {
            'inf': st.mean(x['inf'] for x in L),
            'pre': st.mean(x['pre'] for x in L),
            'pos': st.mean(x['pos'] for x in L),
            'tot': st.mean(x['tot'] for x in L),
            'tercos': (st.mean(x['inf'] for x in L[:n]),
                       st.mean(x['inf'] for x in L[n:2 * n]),
                       st.mean(x['inf'] for x in L[2 * n:])),
        }
    return registros


ARQS = ('YOLOv8n', 'YOLOv10n')
PRECS = ('FP32', 'FP16', 'INT8')


# ---------------------------------------------------------------------
# Figura 1 — latência de inferência, CPU contra GPU
# ---------------------------------------------------------------------

def figura_latencia(reg, saida):
    fig, ax = plt.subplots(figsize=(7.0, 3.4))

    rotulos, v_cpu, v_gpu = [], [], []
    for arq in ARQS:
        for prec in PRECS:
            rotulos.append(f'{arq}\n{prec}')
            v_cpu.append(reg.get((arq, prec, 'CPU'), {}).get('inf'))
            v_gpu.append(reg.get((arq, prec, 'GPU'), {}).get('inf'))

    x = range(len(rotulos))
    larg = 0.38
    desloc = larg / 2 + 0.012          # afastamento de 2 px entre as barras

    b1 = ax.bar([i - desloc for i in x], v_cpu, larg,
                color=COR_CPU, label='CPU', zorder=3)
    b2 = ax.bar([i + desloc for i in x],
                [v if v else 0 for v in v_gpu], larg,
                color=COR_GPU, label='GPU', hatch='///',
                edgecolor='white', linewidth=0, zorder=3)

    for barras, valores in ((b1, v_cpu), (b2, v_gpu)):
        for barra, valor in zip(barras, valores):
            if valor:
                ax.text(barra.get_x() + barra.get_width() / 2,
                        barra.get_height() + 9, f'{valor:.0f}',
                        ha='center', va='bottom', fontsize=8, color=TINTA)

    # A configuração YOLOv10n INT8 em GPU não é executável
    i = rotulos.index('YOLOv10n\nINT8')
    ax.text(i + desloc, 20, 'não executável', ha='center', va='bottom',
            fontsize=7.5, color=TINTA_FRACA, style='italic', rotation=90)
    ax.set_xlim(-0.6, len(rotulos) - 0.4)

    ax.axvline(2.5, color=GRADE, linewidth=1, zorder=1)
    ax.set_xticks(list(x))
    ax.set_xticklabels(rotulos)
    ax.set_ylabel('Latência de inferência (ms)')
    ax.set_ylim(0, 600)
    ax.yaxis.grid(True, color=GRADE, linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)
    for lado in ('top', 'right'):
        ax.spines[lado].set_visible(False)

    ax.legend(handles=[Patch(facecolor=COR_CPU, label='CPU'),
                       Patch(facecolor=COR_GPU, hatch='///', label='GPU')],
              frameon=False, loc='upper left', ncol=2)

    fig.tight_layout()
    for ext in ('pdf', 'png'):
        fig.savefig(Path(saida) / f'latencia_cpu_gpu.{ext}',
                    bbox_inches='tight')
    plt.close(fig)


# ---------------------------------------------------------------------
# Figura 2 — deriva da latência ao longo da execução
# ---------------------------------------------------------------------

def figura_deriva(reg, saida):
    itens = []
    for (arq, prec, deleg), d in reg.items():
        a, _, c = d['tercos']
        itens.append((f'{arq} {prec} · {deleg}', (c - a) / a * 100, deleg))
    itens.sort(key=lambda t: t[1])

    fig, ax = plt.subplots(figsize=(6.6, 3.6))
    y = range(len(itens))
    for i, (rotulo, delta, deleg) in zip(y, itens):
        cor = COR_GPU if deleg == 'GPU' else COR_CPU
        ax.barh(i, delta, 0.62, color=cor, zorder=3,
                hatch='///' if deleg == 'GPU' else None,
                edgecolor='white', linewidth=0)
        ax.text(delta + (1.6 if delta >= 0 else -1.6), i,
                f'{delta:+.0f}%', va='center',
                ha='left' if delta >= 0 else 'right',
                fontsize=8, color=TINTA)

    ax.axvline(0, color=TINTA_FRACA, linewidth=0.9, zorder=4)
    ax.set_yticks(list(y))
    ax.set_yticklabels([t[0] for t in itens], fontsize=8)
    ax.set_xlabel('Variação da latência entre o primeiro e o último terço da execução')
    ax.set_xlim(-32, 72)
    ax.xaxis.grid(True, color=GRADE, linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)
    for lado in ('top', 'right', 'left'):
        ax.spines[lado].set_visible(False)

    ax.legend(handles=[Patch(facecolor=COR_CPU, label='CPU'),
                       Patch(facecolor=COR_GPU, hatch='///', label='GPU')],
              frameon=False, loc='lower right', ncol=2)

    fig.tight_layout()
    for ext in ('pdf', 'png'):
        fig.savefig(Path(saida) / f'deriva_execucao.{ext}', bbox_inches='tight')
    plt.close(fig)


# ---------------------------------------------------------------------
# Figura 3 — composição da latência total
# ---------------------------------------------------------------------

def figura_composicao(reg, saida):
    chaves, rotulos = [], []
    for arq in ARQS:
        for prec in PRECS:
            for deleg in ('CPU', 'GPU'):
                if (arq, prec, deleg) in reg:
                    chaves.append((arq, prec, deleg))
                    rotulos.append(f'{arq} {prec} · {deleg}')

    pre = [reg[k]['pre'] for k in chaves]
    inf = [reg[k]['inf'] for k in chaves]

    fig, ax = plt.subplots(figsize=(6.6, 3.8))
    y = range(len(chaves))

    ax.barh(y, pre, 0.62, color='#c9ced6', label='Pré-processamento', zorder=3)
    ax.barh(y, inf, 0.62, left=[p + 14 for p in pre], color=COR_CPU,
            label='Inferência', zorder=3)

    for i, (p, f) in enumerate(zip(pre, inf)):
        ax.text(p + f + 60, i, f'{f / (p + f) * 100:.0f}%', va='center',
                fontsize=8, color=TINTA_FRACA)

    ax.set_yticks(list(y))
    ax.set_yticklabels(rotulos, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel('Latência média por imagem (ms)')
    ax.set_xlim(0, 2700)
    ax.xaxis.grid(True, color=GRADE, linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)
    for lado in ('top', 'right', 'left'):
        ax.spines[lado].set_visible(False)
    ax.legend(frameon=False, ncol=2, loc='upper center',
              bbox_to_anchor=(0.5, -0.17))
    ax.text(2690, -0.85, 'participação da inferência', ha='right',
            fontsize=7.5, color=TINTA_FRACA, style='italic')

    fig.tight_layout()
    for ext in ('pdf', 'png'):
        fig.savefig(Path(saida) / f'composicao_latencia.{ext}',
                    bbox_inches='tight')
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--entrada', type=str, default='metricas')
    parser.add_argument('--saida', type=str, default='figuras')
    args = parser.parse_args()

    Path(args.saida).mkdir(parents=True, exist_ok=True)
    reg = carregar(args.entrada)
    print(f'Configurações carregadas: {len(reg)}')

    figura_latencia(reg, args.saida)
    figura_deriva(reg, args.saida)
    figura_composicao(reg, args.saida)

    for p in sorted(Path(args.saida).glob('*')):
        print(f'  {p}')


if __name__ == '__main__':
    main()
