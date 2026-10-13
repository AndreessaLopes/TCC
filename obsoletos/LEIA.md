# Material obsoleto

Nada aqui é usado pela monografia na versão atual. Os arquivos foram
preservados para registro do percurso, não para reuso. Se algum voltar a
ser necessário, convém verificar antes sobre qual conjunto de dados ele
rodou, porque o particionamento mudou ao longo do trabalho.

---

## scripts/02_curadoria_phash/

### `phash_train_val.py`

Substituído por `scripts/02_curadoria_phash/verificar_vazamento.py`.

Dois motivos. Primeiro, rodou sobre o `dataset_24_06`, que é uma divisão
anterior (1.517 / 433 / 218) e não a divisão reportada no trabalho
(1.410 / 473 / 285). Segundo, apesar do nome, comparava validação contra
teste: as variáveis que recebem os dois diretórios estão trocadas em
relação aos rótulos. O par treinamento × validação, que é o caso crítico
para vazamento, não era verificado.

O substituto percorre as três combinações possíveis, localiza o conjunto
sozinho e grava o resultado em `resultados/csv/vazamento_entre_particoes.csv`.

### `gerar_matriz_phash.py`

Substituído por `scripts/figuras/gerar_fig_redundancia.py`.

A matriz que ele gerava exibia os 30 pares de maior similaridade. Como
412 dos 426 pares detectados empatam em 100%, esse corte selecionava
pares inteiramente dentro do empate, e a matriz aparecia preenchida com
um único valor, ocupando página inteira sem informar nada além disso. As
células vazias, por sua vez, liam-se como similaridade nula, quando na
verdade indicavam apenas ausência de par acima do limiar.

A Figura 13 passou a mostrar o que a Subseção 3.4 de fato afirma: quantos
grupos de redundância existem e quantos deles atravessam partições
distintas.

---

## scripts/figuras/

### `grafico_distribuicao_dataset.py`

Substituído por `scripts/figuras/gerar_fig_distribuicao.py`.

Gerava gráfico de setores com os percentuais em ponto decimal, fora da
convenção de separador decimal do português, e com rótulos sobrepostos no
setor menor. A versão atual usa barras horizontais com os valores
absolutos e os percentuais rotulados diretamente.

---

## resultados/csv/

### `phash_train_val.csv`

Saída do script homônimo, descrita acima. Registra comparações entre
validação e teste sobre o `dataset_24_06`. Não sustenta nenhuma afirmação
do texto.

O arquivo correspondente em uso é
`resultados/csv/vazamento_entre_particoes.csv`.

---

## resultados/figuras/

### `matriz_similaridade_phash.png`

Figura gerada pelo `gerar_matriz_phash.py`. Ver acima.

### `distribuicao_dataset.png`

Figura gerada pelo `grafico_distribuicao_dataset.py`. Ver acima.

---

## monografia/figuras/

### `grafico_1_crescimento_temporal_sem_margem.png`, `grafico_2_topicos_sem_margem.png` e `grafico_3_keywords_sem_margem.png`

Substituídos por `crescimento_temporal.pdf`, `topicos_busca.pdf` e
`termos_titulos.pdf`, gerados por
`scripts/figuras/gerar_fig_bibliometria.py` a partir dos exports em
`resultados/csv/bibliometria/`.

Nos três, os rótulos traziam valores arredondados à mão sobre barras
desenhadas com os valores reais. Onde o gráfico escrevia 1250, 450 e 70,
os conjuntos têm 1.256, 448 e 73 registros. O gráfico de termos exibia
ainda a preposição "with" entre os termos de conteúdo e não respeitava
ordem decrescente: os três últimos rótulos liam-se 96, 96 e 98.

### `BoxPR_curve_yolov8.png` e `BoxPR_curve_yolov10.png`

Substituídas por `curvas_pr.pdf`, gerado por
`scripts/figuras/gerar_fig_curvas_pr.py` a partir dos pontos extraídos
pelo `exportar_curvas_pr_v2.py`.

Eram a saída crua do Ultralytics, com eixos em inglês e ponto decimal, e
ocupavam uma página cada. Reunidas em um gráfico só, a proximidade entre
as curvas, que o texto afirma, passou a ser visível. O parágrafo também
estava impreciso: dizia precisão acima de 0,85 até revocação de
aproximadamente 0,40, quando esse patamar se mantém até 0,28 no YOLOv8n e
0,32 no YOLOv10n.

### `makesense_anotacao.png`

Substituído por `exemplo_anotacao.jpg`, gerado por
`scripts/figuras/gerar_fig_anotacao.py`.

Tinha 648 px de largura, o que o deixava borrado na página, e sua legenda
o descrevia como captura da plataforma de anotação, embora mostrasse
apenas a imagem com as caixas. A versão atual tem 1.600 px, sai do
conjunto final e identifica na legenda a imagem de origem.

---

## COMO_ORGANIZAR.md

Instruções de organização da pasta, já aplicadas. O que descreviam está
refletido na estrutura atual e documentado no `README.md` da raiz.
