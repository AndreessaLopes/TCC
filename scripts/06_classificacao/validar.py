"""
Validação por amostra dos rótulos atribuídos automaticamente.

Sorteia uma amostra estratificada dos recortes já classificados e os
reapresenta ao anotador SEM exibir a classe registrada, de modo que a
decisão seja tomada às cegas. Ao final, compara as duas atribuições e
informa a taxa de concordância por classe e por cultivar.

FUNDAMENTO

Quando os rótulos de um conjunto são produzidos por procedimento
automático, sua qualidade precisa ser estimada por inspeção humana
independente. A inspeção às cegas é necessária: ao conhecer o rótulo
prévio, o anotador tende a confirmá-lo, e a concordância observada deixa
de medir a qualidade dos rótulos.

A amostragem é estratificada por classe, e não aleatória simples, para
que cada classe receba número suficiente de observações. A taxa global é
recalculada ao final pelos pesos reais das classes no conjunto.

Esta validação não altera os rótulos. Ela produz um número — a taxa de
concordância — que deve ser reportado junto ao conjunto.

TECLAS

    1 ou seta esquerda   Ideal (cereja)
    2 ou seta direita    Não ideal
    3, 0 ou espaço       Descartar
    Z ou backspace       Desfazer
    Q ou Esc             Encerrar e apurar

USO

    python validar.py --diretorio crops_maturacao

    Opcional:
      --por_classe 50     Recortes sorteados por classe (padrão 50).
      --semente 42        Semente do sorteio, para reprodutibilidade.

SAÍDA

    crops_maturacao/validacao.csv

DEPENDÊNCIAS

    pip install pillow
"""

import argparse
import csv
import random
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
}


class Validador:
    def __init__(self, raiz, diretorio, amostra, escala):
        self.raiz = raiz
        self.diretorio = diretorio
        self.amostra = amostra          # lista de (caminho, cultivar, registrada)
        self.escala = escala

        self.indice = 0
        self.respostas = []             # (caminho, cultivar, registrada, informada)
        self.inicio = datetime.now()

        self._montar_interface()
        self._exibir_atual()

    # ------------------------------------------------------------------
    # Interface
    # ------------------------------------------------------------------

    def _montar_interface(self):
        self.raiz.title('Validação por amostra')
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

        tk.Label(
            self.raiz,
            text='A classe registrada não é exibida. Decida pela imagem.',
            font=f_pequena, bg=CORES['fundo'], fg=CORES['apagado'],
        ).pack(pady=(8, 0))

        self.rotulo_arquivo = tk.Label(
            self.raiz, text='', font=f_pequena,
            bg=CORES['fundo'], fg=CORES['apagado'])
        self.rotulo_arquivo.pack(pady=(4, 0))

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
            self.raiz, text='Z desfaz  ·  Q encerra e apura',
            font=f_pequena, bg=CORES['fundo'], fg=CORES['suave'],
        ).pack(pady=(0, 14))

        self.raiz.bind('<Key>', self._ao_pressionar)
        self.raiz.bind('<Left>', lambda e: self._responder('ideal'))
        self.raiz.bind('<Right>', lambda e: self._responder('nao_ideal'))
        self.raiz.bind('<Down>', lambda e: self._responder('descartado'))

    def _ao_pressionar(self, evento):
        tecla = evento.keysym.lower()
        if tecla == '1':
            self._responder('ideal')
        elif tecla == '2':
            self._responder('nao_ideal')
        elif tecla in ('3', '0', 'space'):
            self._responder('descartado')
        elif tecla in ('z', 'backspace'):
            self._desfazer()
        elif tecla in ('q', 'escape'):
            self._encerrar()

    # ------------------------------------------------------------------
    # Fluxo
    # ------------------------------------------------------------------

    def _exibir_atual(self):
        if self.indice >= len(self.amostra):
            self._exibir_conclusao()
            return

        caminho, cultivar, _ = self.amostra[self.indice]

        imagem = Image.open(caminho).resize(
            (self.escala, self.escala), Image.LANCZOS)
        self.imagem_tk = ImageTk.PhotoImage(imagem)
        self.painel_imagem.configure(image=self.imagem_tk)

        self.rotulo_cultivar.configure(
            text=f'Cultivar {cultivar}',
            fg=CORES.get(cultivar, CORES['texto']))
        self.rotulo_progresso.configure(
            text=f'{self.indice + 1} de {len(self.amostra)}')
        self.rotulo_arquivo.configure(text=caminho.name)

        decorrido = (datetime.now() - self.inicio).total_seconds()
        if self.respostas and decorrido > 0:
            ritmo = len(self.respostas) / (decorrido / 60)
            self.rotulo_rodape.configure(
                text=f'{len(self.respostas)} respondidos   ·   {ritmo:.0f}/min')
        else:
            self.rotulo_rodape.configure(text='')

    def _responder(self, classe):
        if self.indice >= len(self.amostra):
            return
        caminho, cultivar, registrada = self.amostra[self.indice]
        self.respostas.append((caminho, cultivar, registrada, classe))
        self.indice += 1
        self._exibir_atual()

    def _desfazer(self):
        if not self.respostas:
            return
        self.respostas.pop()
        self.indice -= 1
        self._exibir_atual()

    def _exibir_conclusao(self):
        self.painel_imagem.configure(image='')
        self.rotulo_cultivar.configure(
            text='Amostra concluída', fg=CORES['ideal'])
        self.rotulo_progresso.configure(text='')
        self.rotulo_arquivo.configure(text='Pressione Q para apurar.')

    def _encerrar(self):
        self._gravar()
        self.raiz.quit()
        self.raiz.destroy()

    def _gravar(self):
        if not self.respostas:
            return
        caminho = self.diretorio / 'validacao.csv'
        with open(caminho, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['arquivo', 'cultivar', 'classe_registrada',
                        'classe_informada', 'concorda', 'momento'])
            momento = datetime.now().isoformat(timespec='seconds')
            for p, cult, reg, inf in self.respostas:
                w.writerow([p.name, cult, reg, inf,
                            'sim' if reg == inf else 'nao', momento])


# ----------------------------------------------------------------------
# Apuração
# ----------------------------------------------------------------------

def apurar(respostas, pesos):
    """Imprime a concordância observada e a taxa global ponderada."""
    from collections import Counter

    print('\n' + '=' * 58)
    print('CONCORDÂNCIA POR CLASSE REGISTRADA')
    print('=' * 58)

    taxas = {}
    for classe in CLASSES:
        sub = [r for r in respostas if r[2] == classe]
        if not sub:
            continue
        ok = sum(1 for r in sub if r[2] == r[3])
        taxas[classe] = ok / len(sub)
        print(f'  {CLASSES[classe]:16s} {ok:4d}/{len(sub):<4d}  {ok/len(sub)*100:5.1f}%')

        for cult in ('amarelas', 'vermelhas'):
            s = [r for r in sub if r[1] == cult]
            if not s:
                continue
            k = sum(1 for r in s if r[2] == r[3])
            print(f'      {cult:12s} {k:4d}/{len(s):<4d}  {k/len(s)*100:5.1f}%')

    # Taxa global ponderada pelos tamanhos reais das classes
    total = sum(pesos.values())
    global_ = sum(taxas.get(c, 0) * pesos.get(c, 0) for c in taxas) / total
    print('-' * 58)
    print(f'  Taxa global ponderada            {global_*100:5.1f}%')

    print('\n' + '=' * 58)
    print('PARA ONDE FORAM AS DISCORDÂNCIAS')
    print('=' * 58)
    m = Counter((r[2], r[3]) for r in respostas if r[2] != r[3])
    if not m:
        print('  Nenhuma.')
    else:
        for (reg, inf), n in sorted(m.items(), key=lambda x: -x[1]):
            print(f'  {CLASSES[reg]:16s} -> {CLASSES[inf]:16s} {n:4d}')


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--diretorio', type=str, default='crops_maturacao')
    parser.add_argument('--por_classe', type=int, default=50)
    parser.add_argument('--semente', type=int, default=42)
    parser.add_argument('--escala', type=int, default=420)
    args = parser.parse_args()

    diretorio = Path(args.diretorio)
    registro = diretorio / 'rotulagem.csv'

    if not registro.exists():
        raise SystemExit(f'Arquivo não encontrado: {registro}')

    linhas = list(csv.DictReader(open(registro, encoding='utf-8')))

    # Agrupa por classe, mantendo apenas recortes localizáveis em disco
    por_classe = {c: [] for c in CLASSES}
    ausentes = 0
    for l in linhas:
        classe = l['classe']
        if classe not in por_classe:
            continue
        caminho = diretorio / classe / l['arquivo']
        if caminho.exists():
            por_classe[classe].append((caminho, l['cultivar'], classe))
        else:
            ausentes += 1

    if ausentes:
        print(f'Aviso: {ausentes} recortes do registro não foram encontrados.')

    pesos = {c: len(v) for c, v in por_classe.items()}
    print('Conjunto:', '  '.join(f'{c}={n}' for c, n in pesos.items()))

    rng = random.Random(args.semente)
    amostra = []
    for classe, itens in por_classe.items():
        n = min(args.por_classe, len(itens))
        amostra.extend(rng.sample(itens, n))
    rng.shuffle(amostra)      # classes intercaladas, para não induzir padrão

    print(f'Amostra sorteada: {len(amostra)} recortes (semente {args.semente})')
    print('A classe registrada não será exibida durante a validação.\n')

    raiz = tk.Tk()
    validador = Validador(raiz, diretorio, amostra, args.escala)
    raiz.protocol('WM_DELETE_WINDOW', validador._encerrar)
    raiz.mainloop()

    if validador.respostas:
        apurar(validador.respostas, pesos)
        print(f'\nRegistro em {diretorio / "validacao.csv"}')
    else:
        print('Nenhuma resposta registrada.')


if __name__ == '__main__':
    main()