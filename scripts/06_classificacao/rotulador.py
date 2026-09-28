"""
Ferramenta de rotulagem dos recortes quanto ao estágio de maturação.

Apresenta um recorte por vez e registra a classificação atribuída,
movendo o arquivo para o diretório correspondente. A operação por teclado
reduz substancialmente o tempo necessário em relação à organização manual
dos arquivos.

CRITÉRIO DE CLASSIFICAÇÃO

    Ideal        Fruto no estágio cereja, correspondente ao ponto adequado
                 de colheita: coloração vermelha intensa na cultivar
                 vermelha, amarela intensa na cultivar amarela. A cultivar
                 de origem é indicada no cabeçalho, uma vez que a mesma
                 tonalidade pode corresponder a estágios distintos conforme
                 a cultivar — o amarelo é cereja na cultivar amarela e
                 verde-cana na vermelha.

    Não ideal    Fruto fora do ponto de colheita, em qualquer direção:
                 verde e verde-cana, anteriores ao cereja; passa e seco,
                 posteriores, de coloração escura e superfície enrugada.

    Descartar    Recorte cuja classificação permaneça indefinida — por
                 conter frutos em estágios diversos sem predominância, por
                 apresentar nitidez insuficiente ou por não conter fruto
                 visível. A exclusão desses casos preserva a consistência
                 do conjunto, ainda que reduza seu tamanho.

PRÉ-ROTULAGEM

Quando o arquivo prerotulagem.csv está presente no diretório, a fila é
ordenada pelo escore cromático de maturação, de modo que recortes de
aparência semelhante permaneçam adjacentes, e a proposta automática é
exibida sob a imagem. A tecla Enter confirma a proposta; as demais teclas
operam normalmente e a sobrepõem.

A proposta não substitui a decisão do anotador: toda classificação
registrada resulta de um pressionamento de tecla. A concordância entre
proposta e decisão é registrada no arquivo de saída, permitindo quantificar
a contribuição da pré-rotulagem.

TECLAS

    1 ou seta esquerda   Ideal (cereja)
    2 ou seta direita    Não ideal
    3, 0 ou espaço       Descartar
    4, D ou seta cima    Adiar a decisão
    Enter                Confirmar a proposta exibida
    Z ou backspace       Desfazer a última classificação
    Q ou Esc             Encerrar

A tecla 4 encaminha o recorte ao diretório duvida, sem classificá-lo. O
procedimento preserva o ritmo da sessão: os casos difíceis são acumulados
e revisados ao final, quando o critério já está calibrado pela passagem
sobre os casos evidentes. Concluída a fila principal, basta executar a
ferramenta apontando para esse diretório.

    python rotulador.py --diretorio crops_maturacao --pendentes duvida

USO

    python prerotular.py --diretorio crops_maturacao
    python rotulador.py  --diretorio crops_maturacao

DEPENDÊNCIAS

    pip install pillow
"""

import argparse
import csv
import shutil
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import font as tkfont

from PIL import Image, ImageTk

CLASSES = {
    'ideal': 'Ideal (cereja)',
    'nao_ideal': 'Não ideal',
    'descartado': 'Descartado',
    'duvida': 'Dúvida',
}

# 'duvida' não constitui classe do conjunto: é destino provisório para os
# recortes cuja decisão foi adiada, revisados ao final da sessão.
CLASSES_FINAIS = ('ideal', 'nao_ideal', 'descartado')

CORES = {
    'fundo': '#1e1e1e',
    'painel': '#2a2a2a',
    'texto': '#e8e8e8',
    'suave': '#9a9a9a',
    'apagado': '#5a5a5a',
    'ideal': '#4caf50',
    'nao_ideal': '#e07b39',
    'descartado': '#6b6b6b',
    'duvida': '#4a7fb5',
    'amarelas': '#d4a017',
    'vermelhas': '#b03030',
}

ARQUIVO_PREROTULAGEM = 'prerotulagem.csv'
ARQUIVO_REGISTRO = 'rotulagem.csv'


class Rotulador:
    def __init__(self, raiz: tk.Tk, diretorio: Path, escala: int,
                 pendentes: str = 'nao_rotulados'):
        self.raiz = raiz
        self.diretorio = diretorio
        self.pendentes_dir = diretorio / pendentes
        self.revisando_duvidas = (pendentes == 'duvida')
        self.escala = escala

        for classe in CLASSES:
            (diretorio / classe).mkdir(parents=True, exist_ok=True)

        self.prerotulagem = self._carregar_prerotulagem()
        self.arquivos = self._montar_fila()

        self.indice = 0
        self.historico = []
        self.contagem = {classe: 0 for classe in CLASSES}
        self.concordancias = 0
        self.com_proposta = 0
        self.inicio = datetime.now()

        self._contar_existentes()
        self._montar_interface()
        self._exibir_atual()

    # ------------------------------------------------------------------
    # Preparação
    # ------------------------------------------------------------------

    def _carregar_prerotulagem(self):
        """Lê as propostas geradas por prerotular.py, se disponíveis."""
        caminho = self.diretorio / ARQUIVO_PREROTULAGEM

        if not caminho.exists():
            return {}

        registros = {}
        try:
            with open(caminho, newline='', encoding='utf-8') as f:
                for linha in csv.DictReader(f):
                    registros[linha['arquivo']] = {
                        'ordem': int(linha['ordem']),
                        'escore': float(linha['escore']),
                        'proposta': linha['proposta'],
                    }
        except (KeyError, ValueError):
            return {}

        return registros

    def _montar_fila(self):
        """Ordena os pendentes pelo escore, quando a pré-rotulagem existe."""
        arquivos = [
            p for p in self.pendentes_dir.glob('*')
            if p.suffix.lower() in {'.jpg', '.jpeg', '.png'}
        ]

        if not self.prerotulagem:
            return sorted(arquivos)

        # Recortes ausentes do registro vão ao final, em ordem alfabética
        ausente = len(self.prerotulagem) + 1
        return sorted(
            arquivos,
            key=lambda p: (
                self.prerotulagem.get(p.name, {}).get('ordem', ausente),
                p.name,
            ),
        )

    def _contar_existentes(self):
        """Contabiliza classificações realizadas em sessões anteriores."""
        for classe in CLASSES:
            self.contagem[classe] = len(
                list((self.diretorio / classe).glob('*'))
            )

    def _info_atual(self):
        if self.indice >= len(self.arquivos):
            return None
        return self.prerotulagem.get(self.arquivos[self.indice].name)

    # ------------------------------------------------------------------
    # Interface
    # ------------------------------------------------------------------

    def _montar_interface(self):
        self.raiz.title(
            'Revisão das dúvidas' if self.revisando_duvidas
            else 'Rotulagem de maturação'
        )
        self.raiz.configure(bg=CORES['fundo'])
        self.raiz.resizable(False, False)

        fonte_titulo = tkfont.Font(family='Segoe UI', size=13, weight='bold')
        fonte_normal = tkfont.Font(family='Segoe UI', size=10)
        fonte_pequena = tkfont.Font(family='Segoe UI', size=9)

        # Cabeçalho: cultivar e progresso
        topo = tk.Frame(self.raiz, bg=CORES['fundo'])
        topo.pack(fill='x', padx=16, pady=(14, 8))

        self.rotulo_cultivar = tk.Label(
            topo, text='', font=fonte_titulo,
            bg=CORES['fundo'], fg=CORES['texto'],
        )
        self.rotulo_cultivar.pack(side='left')

        self.rotulo_progresso = tk.Label(
            topo, text='', font=fonte_normal,
            bg=CORES['fundo'], fg=CORES['suave'],
        )
        self.rotulo_progresso.pack(side='right')

        # Imagem
        self.painel_imagem = tk.Label(self.raiz, bg=CORES['painel'])
        self.painel_imagem.pack(padx=16)

        # Proposta da pré-rotulagem
        self.rotulo_proposta = tk.Label(
            self.raiz, text='', font=fonte_normal,
            bg=CORES['fundo'], fg=CORES['suave'],
        )
        self.rotulo_proposta.pack(pady=(8, 0))

        self.rotulo_arquivo = tk.Label(
            self.raiz, text='', font=fonte_pequena,
            bg=CORES['fundo'], fg=CORES['apagado'],
        )
        self.rotulo_arquivo.pack(pady=(4, 0))

        # Instruções
        instrucoes = tk.Frame(self.raiz, bg=CORES['fundo'])
        instrucoes.pack(pady=(12, 6))

        teclas = [
            ('1', 'Ideal', CORES['ideal']),
            ('2', 'Não ideal', CORES['nao_ideal']),
            ('3', 'Descartar', CORES['descartado']),
        ]
        if not self.revisando_duvidas:
            teclas.append(('4', 'Dúvida', CORES['duvida']))

        for tecla, texto, cor in teclas:
            bloco = tk.Frame(instrucoes, bg=CORES['fundo'])
            bloco.pack(side='left', padx=14)

            tk.Label(
                bloco, text=tecla, font=fonte_titulo,
                bg=cor, fg='white', width=3,
            ).pack()

            tk.Label(
                bloco, text=texto, font=fonte_pequena,
                bg=CORES['fundo'], fg=CORES['suave'],
            ).pack(pady=(3, 0))

        # Rodapé: contagem e atalhos
        self.rotulo_contagem = tk.Label(
            self.raiz, text='', font=fonte_normal,
            bg=CORES['fundo'], fg=CORES['texto'],
        )
        self.rotulo_contagem.pack(pady=(8, 2))

        partes_atalho = []
        if self.prerotulagem and not self.revisando_duvidas:
            partes_atalho.append('Enter confirma a proposta')
        if not self.revisando_duvidas:
            partes_atalho.append('4 adia')
        partes_atalho += ['Z desfaz', 'Q encerra']
        atalhos = '  ·  '.join(partes_atalho)

        tk.Label(
            self.raiz, text=atalhos, font=fonte_pequena,
            bg=CORES['fundo'], fg=CORES['suave'],
        ).pack(pady=(0, 14))

        # Teclado
        self.raiz.bind('<Key>', self._ao_pressionar)
        self.raiz.bind('<Left>', lambda e: self._classificar('ideal'))
        self.raiz.bind('<Right>', lambda e: self._classificar('nao_ideal'))
        self.raiz.bind('<Down>', lambda e: self._classificar('descartado'))
        if not self.revisando_duvidas:
            self.raiz.bind('<Up>', lambda e: self._classificar('duvida'))

    def _ao_pressionar(self, evento):
        tecla = evento.keysym.lower()

        if tecla == '1':
            self._classificar('ideal')
        elif tecla == '2':
            self._classificar('nao_ideal')
        elif tecla in ('3', '0', 'space'):
            self._classificar('descartado')
        elif tecla in ('4', 'd') and not self.revisando_duvidas:
            self._classificar('duvida')
        elif tecla in ('return', 'kp_enter'):
            self._confirmar_proposta()
        elif tecla in ('z', 'backspace'):
            self._desfazer()
        elif tecla in ('q', 'escape'):
            self._encerrar()

    # ------------------------------------------------------------------
    # Exibição
    # ------------------------------------------------------------------

    def _exibir_atual(self):
        if self.indice >= len(self.arquivos):
            self._exibir_conclusao()
            return

        caminho = self.arquivos[self.indice]

        imagem = Image.open(caminho)
        imagem = imagem.resize((self.escala, self.escala), Image.LANCZOS)
        self.imagem_tk = ImageTk.PhotoImage(imagem)
        self.painel_imagem.configure(image=self.imagem_tk)

        cultivar = caminho.name.split('_')[0]
        cor = CORES.get(cultivar, CORES['texto'])

        self.rotulo_cultivar.configure(text=f'Cultivar {cultivar}', fg=cor)

        restantes = len(self.arquivos) - self.indice
        self.rotulo_progresso.configure(
            text=f'{self.indice + 1} de {len(self.arquivos)}  '
                 f'({restantes} restantes)'
        )

        self._exibir_proposta()
        self.rotulo_arquivo.configure(text=caminho.name)
        self._atualizar_contagem()

    def _exibir_proposta(self):
        info = self._info_atual()

        if not info:
            self.rotulo_proposta.configure(text='', fg=CORES['suave'])
            return

        escore = info['escore']
        escore_texto = 'indefinido' if escore <= -9 else f'{escore:+.2f}'

        if info['proposta']:
            self.rotulo_proposta.configure(
                text=f'Proposta: {CLASSES[info["proposta"]]}   '
                     f'(escore {escore_texto})',
                fg=CORES[info['proposta']],
            )
        else:
            self.rotulo_proposta.configure(
                text=f'Sem proposta   (escore {escore_texto})',
                fg=CORES['apagado'],
            )

    def _atualizar_contagem(self):
        exibidas = CLASSES_FINAIS if self.revisando_duvidas else CLASSES
        partes = [
            f'{CLASSES[classe]}: {self.contagem[classe]}'
            for classe in exibidas
        ]

        decorrido = (datetime.now() - self.inicio).total_seconds()
        total = len(self.historico)

        if total > 0 and decorrido > 0:
            partes.append(f'{total / (decorrido / 60):.0f}/min')

        if self.com_proposta > 0:
            taxa = self.concordancias / self.com_proposta * 100
            partes.append(f'concordância: {taxa:.0f}%')

        self.rotulo_contagem.configure(text='     '.join(partes))

    def _exibir_conclusao(self):
        self.painel_imagem.configure(image='')
        self.rotulo_cultivar.configure(
            text='Rotulagem concluída', fg=CORES['ideal']
        )
        self.rotulo_progresso.configure(text='')
        self.rotulo_proposta.configure(text='')
        self.rotulo_arquivo.configure(
            text='Não há recortes pendentes neste diretório.'
        )
        self._atualizar_contagem()

    # ------------------------------------------------------------------
    # Ações
    # ------------------------------------------------------------------

    def _confirmar_proposta(self):
        info = self._info_atual()
        if info and info['proposta']:
            self._classificar(info['proposta'])

    def _classificar(self, classe: str):
        if self.indice >= len(self.arquivos):
            return

        origem = self.arquivos[self.indice]
        destino = self.diretorio / classe / origem.name

        try:
            shutil.move(str(origem), str(destino))
        except Exception as erro:
            self.rotulo_arquivo.configure(text=f'Falha ao mover: {erro}')
            return

        info = self._info_atual()
        proposta = info['proposta'] if info else ''
        escore = info['escore'] if info else None

        if proposta:
            self.com_proposta += 1
            if proposta == classe:
                self.concordancias += 1

        self.historico.append({
            'origem': origem,
            'destino': destino,
            'classe': classe,
            'proposta': proposta,
            'escore': escore,
        })

        self.contagem[classe] += 1
        self.indice += 1

        self._exibir_atual()

    def _desfazer(self):
        if not self.historico:
            return

        ultimo = self.historico.pop()

        try:
            shutil.move(str(ultimo['destino']), str(ultimo['origem']))
        except Exception:
            self.historico.append(ultimo)
            return

        if ultimo['proposta']:
            self.com_proposta -= 1
            if ultimo['proposta'] == ultimo['classe']:
                self.concordancias -= 1

        self.contagem[ultimo['classe']] -= 1
        self.indice -= 1

        self._exibir_atual()

    def _encerrar(self):
        self._gravar_registro()
        self.raiz.quit()
        self.raiz.destroy()

    def _gravar_registro(self):
        """Registra as classificações realizadas nesta sessão."""
        if not self.historico:
            return

        caminho = self.diretorio / ARQUIVO_REGISTRO
        existe = caminho.exists()

        with open(caminho, 'a', newline='', encoding='utf-8') as f:
            escritor = csv.writer(f)

            if not existe:
                escritor.writerow([
                    'arquivo', 'cultivar', 'classe', 'proposta',
                    'concordou', 'escore', 'momento',
                ])

            momento = datetime.now().isoformat(timespec='seconds')

            for item in self.historico:
                origem = item['origem']
                proposta = item['proposta']

                if proposta:
                    concordou = 'sim' if proposta == item['classe'] else 'nao'
                else:
                    concordou = ''

                escore = '' if item['escore'] is None \
                    else f"{item['escore']:.4f}"

                escritor.writerow([
                    origem.name, origem.name.split('_')[0], item['classe'],
                    proposta, concordou, escore, momento,
                ])


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--diretorio', type=str, default='crops_maturacao',
                        help='Diretório contendo a subpasta nao_rotulados.')
    parser.add_argument('--escala', type=int, default=420,
                        help='Dimensão de exibição dos recortes, em pixels.')
    parser.add_argument('--pendentes', type=str, default='nao_rotulados',
                        choices=['nao_rotulados', 'duvida'],
                        help='Subpasta a percorrer. Use duvida para revisar '
                             'os recortes adiados.')
    args = parser.parse_args()

    diretorio = Path(args.diretorio)
    pendentes = diretorio / args.pendentes

    if not pendentes.exists():
        raise SystemExit(
            f'Diretório não encontrado: {pendentes}\n'
            'Execute extrair_crops.py antes da rotulagem.'
        )

    raiz = tk.Tk()
    rotulador = Rotulador(raiz, diretorio, args.escala, args.pendentes)

    raiz.protocol('WM_DELETE_WINDOW', rotulador._encerrar)

    raiz.mainloop()


if __name__ == '__main__':
    main()