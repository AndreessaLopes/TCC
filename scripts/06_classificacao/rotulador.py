"""
Rotulagem do estágio de maturação, sem proposta automática.

Apresenta um recorte por vez e registra a classificação atribuída. Nenhuma
sugestão é exibida: a decisão é integralmente do anotador. O conjunto
apresentado foi previamente restrito aos recortes em que há fruto
identificável, de modo que toda imagem exibida comporte uma decisão.

CRITÉRIO

    Ideal        Fruto no estágio cereja, correspondente ao ponto adequado
                 de colheita: vermelho intenso na cultivar vermelha,
                 amarelo intenso na cultivar amarela. A cultivar é
                 indicada no cabeçalho, pois a mesma tonalidade
                 corresponde a estágios distintos conforme a cultivar: o
                 amarelo é cereja na cultivar amarela e verde-cana na
                 vermelha.

    Não ideal    Fruto fora do ponto de colheita, em qualquer direção:
                 verde e verde-cana, anteriores ao cereja; passa e seco,
                 posteriores, escuros e de superfície enrugada.

    Descartar    Recorte sem fruto identificável, sem nitidez suficiente,
                 ou com frutos em estágios diversos sem predominância.

SESSÕES

A rotulagem é dividida em sessões de extensão limitada. A ferramenta
encerra automaticamente ao atingir o limite e retoma do ponto de parada na
execução seguinte. A divisão é deliberada: sessões longas degradam a
consistência das decisões.

REGISTRO DE TEMPO

O intervalo entre a exibição e a decisão é registrado para cada recorte.
A mediana desse intervalo documenta o regime sob o qual a rotulagem foi
conduzida e deve ser reportada junto ao conjunto. Pressionamentos
ocorridos antes de 400 ms da exibição são ignorados, por corresponderem a
repetição automática de tecla e não a decisão.

TECLAS

    1 ou seta esquerda   Ideal (cereja)
    2 ou seta direita    Não ideal
    3, 0 ou espaço       Descartar
    Z ou backspace       Desfazer
    Q ou Esc             Encerrar

USO

    python rotular.py --diretorio crops_maturacao

    Opcional:
      --limite 150    Recortes por sessão (padrão 150).
      --escala 420    Dimensão de exibição, em pixels.

ENTRADA

    crops_maturacao/candidatos.csv     lista dos recortes a rotular
    crops_maturacao/nao_rotulados/     os arquivos

SAÍDA

    crops_maturacao/rotulos.csv        acumulado entre sessões

DEPENDÊNCIAS

    pip install pillow
"""

import argparse
import csv
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import font as tkfont

from PIL import Image, ImageTk

CLASSES = {
    'ideal': 'Ideal (cereja)',
    'nao_ideal': 'Não ideal',
    'descartado': 'Descartado',
}

CORES = {
    'fundo': '#1e1e1e',
    'painel': '#2a2a2a',
    'texto': '#e8e8e8',
    'suave': '#9a9a9a',
    'apagado': '#5a5a5a',
    'ideal': '#4caf50',
    'nao_ideal': '#e07b39',
    'descartado': '#6b6b6b',
    'amarelas': '#d4a017',
    'vermelhas': '#b03030',
    'barra': '#3a3a3a',
    'barra_ativa': '#4a7fb5',
}

ENTRADA = 'candidatos.csv'
SAIDA = 'rotulos.csv'

# Intervalo abaixo do qual o pressionamento é atribuído a repetição
# automática de tecla, e não a uma decisão.
INTERVALO_MINIMO = 0.40


class Rotulador:
    def __init__(self, raiz, diretorio, fila, limite, escala):
        self.raiz = raiz
        self.diretorio = diretorio
        self.fila = fila              # [(ordem, caminho, cultivar), ...]
        self.limite = limite
        self.escala = escala

        self.indice = 0
        self.registros = []           # (ordem, caminho, cultivar, classe, seg)
        self.exibido_em = None
        self.ignorados = 0

        self._montar_interface()
        self._exibir_atual()

    # ------------------------------------------------------------------
    # Interface
    # ------------------------------------------------------------------

    def _montar_interface(self):
        self.raiz.title('Rotulagem de maturação')
        self.raiz.configure(bg=CORES['fundo'])
        self.raiz.resizable(False, False)

        f_titulo = tkfont.Font(family='Segoe UI', size=13, weight='bold')
        f_normal = tkfont.Font(family='Segoe UI', size=10)
        f_pequena = tkfont.Font(family='Segoe UI', size=9)

        topo = tk.Frame(self.raiz, bg=CORES['fundo'])
        topo.pack(fill='x', padx=16, pady=(14, 8))

        self.rotulo_cultivar = tk.Label(
            topo, text='', font=f_titulo, bg=CORES['fundo'], fg=CORES['texto'])
        self.rotulo_cultivar.pack(side='left')

        self.rotulo_progresso = tk.Label(
            topo, text='', font=f_normal, bg=CORES['fundo'], fg=CORES['suave'])
        self.rotulo_progresso.pack(side='right')

        self.painel_imagem = tk.Label(self.raiz, bg=CORES['painel'])
        self.painel_imagem.pack(padx=16)

        # Barra de progresso da sessão
        self.barra = tk.Canvas(
            self.raiz, width=self.escala, height=4,
            bg=CORES['barra'], highlightthickness=0)
        self.barra.pack(pady=(6, 0))
        self.barra_preenchida = self.barra.create_rectangle(
            0, 0, 0, 4, fill=CORES['barra_ativa'], width=0)

        self.rotulo_arquivo = tk.Label(
            self.raiz, text='', font=f_pequena,
            bg=CORES['fundo'], fg=CORES['apagado'])
        self.rotulo_arquivo.pack(pady=(6, 0))

        instrucoes = tk.Frame(self.raiz, bg=CORES['fundo'])
        instrucoes.pack(pady=(12, 6))

        for tecla, texto, cor in (
            ('1', 'Ideal', CORES['ideal']),
            ('2', 'Não ideal', CORES['nao_ideal']),
            ('3', 'Descartar', CORES['descartado']),
        ):
            bloco = tk.Frame(instrucoes, bg=CORES['fundo'])
            bloco.pack(side='left', padx=14)
            tk.Label(bloco, text=tecla, font=f_titulo,
                     bg=cor, fg='white', width=3).pack()
            tk.Label(bloco, text=texto, font=f_pequena,
                     bg=CORES['fundo'], fg=CORES['suave']).pack(pady=(3, 0))

        self.rotulo_rodape = tk.Label(
            self.raiz, text='', font=f_normal,
            bg=CORES['fundo'], fg=CORES['texto'])
        self.rotulo_rodape.pack(pady=(8, 2))

        tk.Label(
            self.raiz, text='Z desfaz  ·  Q encerra',
            font=f_pequena, bg=CORES['fundo'], fg=CORES['suave'],
        ).pack(pady=(0, 14))

        self.raiz.bind('<Key>', self._ao_pressionar)
        self.raiz.bind('<Left>', lambda e: self._classificar('ideal'))
        self.raiz.bind('<Right>', lambda e: self._classificar('nao_ideal'))
        self.raiz.bind('<Down>', lambda e: self._classificar('descartado'))

    def _ao_pressionar(self, evento):
        tecla = evento.keysym.lower()
        if tecla == '1':
            self._classificar('ideal')
        elif tecla == '2':
            self._classificar('nao_ideal')
        elif tecla in ('3', '0', 'space'):
            self._classificar('descartado')
        elif tecla in ('z', 'backspace'):
            self._desfazer()
        elif tecla in ('q', 'escape'):
            self._encerrar()

    # ------------------------------------------------------------------
    # Exibição
    # ------------------------------------------------------------------

    def _exibir_atual(self):
        if self.indice >= len(self.fila) or len(self.registros) >= self.limite:
            self._exibir_conclusao()
            return

        _, caminho, cultivar = self.fila[self.indice]

        imagem = Image.open(caminho).resize(
            (self.escala, self.escala), Image.LANCZOS)
        self.imagem_tk = ImageTk.PhotoImage(imagem)
        self.painel_imagem.configure(image=self.imagem_tk)

        self.rotulo_cultivar.configure(
            text=f'Cultivar {cultivar}',
            fg=CORES.get(cultivar, CORES['texto']))

        feito = len(self.registros)
        self.rotulo_progresso.configure(
            text=f'{feito + 1} de {min(self.limite, len(self.fila))} nesta sessão')

        largura = self.escala * feito / self.limite
        self.barra.coords(self.barra_preenchida, 0, 0, largura, 4)

        self.rotulo_arquivo.configure(text=caminho.name)
        self._atualizar_rodape()

        self.exibido_em = time.monotonic()

    def _atualizar_rodape(self):
        from collections import Counter
        c = Counter(r[3] for r in self.registros)
        partes = [f'{CLASSES[k]}: {c[k]}' for k in CLASSES]

        tempos = sorted(r[4] for r in self.registros)
        if tempos:
            mediana = tempos[len(tempos) // 2]
            partes.append(f'mediana {mediana:.1f}s')

        self.rotulo_rodape.configure(text='     '.join(partes))

    def _exibir_conclusao(self):
        self.painel_imagem.configure(image='')
        restantes = len(self.fila) - self.indice
        self.rotulo_cultivar.configure(
            text='Sessão concluída', fg=CORES['ideal'])
        self.rotulo_progresso.configure(text='')
        self.rotulo_arquivo.configure(
            text=f'{restantes} recortes restantes. Pressione Q para gravar.')
        self.barra.coords(self.barra_preenchida, 0, 0, self.escala, 4)
        self._atualizar_rodape()

    # ------------------------------------------------------------------
    # Ações
    # ------------------------------------------------------------------

    def _classificar(self, classe):
        if self.indice >= len(self.fila) or len(self.registros) >= self.limite:
            return

        decorrido = time.monotonic() - (self.exibido_em or 0)

        if decorrido < INTERVALO_MINIMO:
            self.ignorados += 1
            return

        ordem, caminho, cultivar = self.fila[self.indice]
        self.registros.append((ordem, caminho, cultivar, classe, decorrido))
        self.indice += 1
        self._exibir_atual()

    def _desfazer(self):
        if not self.registros:
            return
        self.registros.pop()
        self.indice -= 1
        self._exibir_atual()

    def _encerrar(self):
        self._gravar()
        self.raiz.quit()
        self.raiz.destroy()

    def _gravar(self):
        if not self.registros:
            return

        caminho = self.diretorio / SAIDA
        existe = caminho.exists()
        sessao = datetime.now().isoformat(timespec='seconds')

        with open(caminho, 'a', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            if not existe:
                w.writerow(['ordem', 'arquivo', 'cultivar', 'classe',
                            'segundos', 'sessao'])
            for ordem, p, cult, classe, seg in self.registros:
                w.writerow([ordem, p.name, cult, classe, f'{seg:.2f}', sessao])


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--diretorio', type=str, default='crops_maturacao')
    parser.add_argument('--limite', type=int, default=150)
    parser.add_argument('--escala', type=int, default=420)
    args = parser.parse_args()

    diretorio = Path(args.diretorio)
    entrada = diretorio / ENTRADA
    pendentes = diretorio / 'nao_rotulados'

    if not entrada.exists():
        raise SystemExit(f'Arquivo não encontrado: {entrada}')
    if not pendentes.exists():
        raise SystemExit(f'Diretório não encontrado: {pendentes}')

    candidatos = list(csv.DictReader(open(entrada, encoding='utf-8')))

    # Retoma de onde parou
    feitos = set()
    saida = diretorio / SAIDA
    if saida.exists():
        feitos = {l['arquivo'] for l in csv.DictReader(
            open(saida, encoding='utf-8'))}

    fila, ausentes = [], 0
    for c in candidatos:
        if c['arquivo'] in feitos:
            continue
        caminho = pendentes / c['arquivo']
        if caminho.exists():
            fila.append((int(c['ordem']), caminho, c['cultivar']))
        else:
            ausentes += 1

    fila.sort(key=lambda x: x[0])

    print(f'Candidatos: {len(candidatos)}')
    print(f'Já rotulados: {len(feitos)}')
    if ausentes:
        print(f'Não encontrados em nao_rotulados: {ausentes}')
    print(f'Pendentes: {len(fila)}')

    if not fila:
        print('\nNada a rotular. Conjunto completo.')
        return

    limite = min(args.limite, len(fila))
    print(f'Esta sessão: {limite} recortes.\n')

    raiz = tk.Tk()
    rotulador = Rotulador(raiz, diretorio, fila, limite, args.escala)
    raiz.protocol('WM_DELETE_WINDOW', rotulador._encerrar)
    raiz.mainloop()

    n = len(rotulador.registros)
    if not n:
        print('Nenhum recorte rotulado.')
        return

    from collections import Counter
    c = Counter(r[3] for r in rotulador.registros)
    tempos = sorted(r[4] for r in rotulador.registros)

    print(f'\nRotulados nesta sessão: {n}')
    for k in CLASSES:
        print(f'  {CLASSES[k]:16s} {c[k]:4d}')
    print(f'\nTempo por recorte: mediana {tempos[len(tempos)//2]:.1f}s  '
          f'(mín {tempos[0]:.1f}s, máx {tempos[-1]:.1f}s)')
    if rotulador.ignorados:
        print(f'Pressionamentos ignorados por repetição de tecla: '
              f'{rotulador.ignorados}')
    print(f'\nAcumulado em {diretorio / SAIDA}')
    print(f'Faltam {len(fila) - n} recortes. Execute novamente para continuar.')


if __name__ == '__main__':
    main()