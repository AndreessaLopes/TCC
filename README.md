# Detecção de Frutos de Café em Dispositivos Móveis

Repositório do Trabalho de Conclusão de Curso **"Desempenho e Estabilidade de Modelos YOLO para Detecção da Maturação de Frutos de Café em Smartphones: comparação entre delegates TFLite"**.

**Autora:** Andressa Caroline Lopes de Assis
**Orientador:** Prof. Dr. Bruno Alberto Soares Oliveira
**Instituição:** IFMG — Campus Bambuí — Bacharelado em Engenharia de Computação

---

## Sobre o trabalho

A pesquisa compara configurações dos modelos YOLOv8n e YOLOv10n convertidos para TensorFlow Lite, avaliando o impacto de estratégias de quantização (FP32, FP16 e INT8) e de mecanismos de aceleração por hardware (delegates de CPU e GPU) sobre latência, estabilidade de execução, consumo energético e tamanho dos arquivos gerados em smartphones Android.

O conjunto de dados foi construído no âmbito de projeto de Iniciação Científica financiado pelo CNPq, a partir de imagens coletadas em lavouras cafeeiras de Bambuí, Minas Gerais, entre novembro de 2023 e fevereiro de 2024.

---

## Organização do repositório

```
TCC/
├── monografia/          texto do trabalho em LaTeX e suas figuras
├── scripts/             código, numerado conforme a ordem de execução
├── resultados/          saídas das execuções: CSVs e figuras
├── modelos_tflite/      os seis modelos convertidos
├── cafescan/            aplicativo Android em Flutter usado nas medições
└── obsoletos/           material substituído, preservado para histórico
```

O conjunto de imagens, os pesos `.pt` e o diretório `runs/` não são
versionados aqui, pelo volume dos arquivos. O `.gitignore` os exclui.

---

## A monografia

```
monografia/
├── artigo.tex           documento principal
├── referencias.bib      base bibliográfica (biblatex/biber)
├── iftex2024.cls        classe do IFMG
├── biblatexfix.sty
└── figuras/             tudo que o artigo.tex referencia
    └── mapa/            imagens compostas pela Figura 8
```

Compilação, com o diretório `monografia/` como atual:

```bash
pdflatex artigo.tex
biber artigo
pdflatex artigo.tex
pdflatex artigo.tex
```

Três figuras são desenhadas em TikZ e compiladas junto com o texto
(`fig_pipeline_referencial.tex`, `fig_rede_tematica.tex`,
`fig_mapa_bambui.tex`). As demais são arquivos `.pdf` ou `.png` gerados
pelos scripts de `scripts/figuras/`.

---

## Conjunto de dados

| Etapa | Imagens |
|---|---|
| Conjunto bruto coletado | ~5.000 |
| Anotadas e validadas | 2.511 |
| Removidas por pHash | 343 |
| Conjunto final | 2.168 |

Divisão utilizada nos experimentos:

| Subconjunto | Imagens | Instâncias |
|---|---|---|
| Treinamento | 1.410 | — |
| Validação | 473 | 3.972 |
| Teste | 285 | 2.399 |

Classe única: `frutos`. Formato de anotação: YOLO.

O termo *grão* designa a semente beneficiada e é empregado neste trabalho
apenas nesse sentido, ao tratar dos estudos de inspeção de defeitos. O que
os modelos detectam é o fruto no cafeeiro, e a classe recebe esse nome.

Estrutura esperada pelos scripts:

```
dataset_final/
├── train/
│   ├── images/
│   └── labels/
├── val/
│   ├── images/
│   └── labels/
├── test/
│   ├── images/
│   └── labels/
└── data.yaml
```

---

## Instalação

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS

pip install -r requirements.txt
```

Para a etapa de conversão para TensorFlow Lite, descomente as dependências
correspondentes no `requirements.txt` e instale-as separadamente.

---

## Organização dos scripts

Os scripts estão numerados conforme a ordem de execução no fluxo
metodológico.

### 01 — Pré-processamento e validação

| Script | Função |
|---|---|
| `check_dataset.py` | Verifica integridade das anotações e contabiliza caixas por classe |
| `check_missing_by_class.py` | Identifica imagens sem arquivo de anotação correspondente |
| `verificar_pares.py` | Compara correspondência entre imagens e rótulos |
| `clean_labels.py` | Remove linhas malformadas e normaliza coordenadas |
| `classe.py` | Converte todas as anotações para a classe única `graos` |
| `ajustar_classes.py` | Atribui índices de classe conforme a pasta de origem (etapa inicial, duas classes) |
| `labels.py` | Renomeia arquivos de rótulo para corresponder aos nomes das imagens |
| `limpar_dataset_yolo.py` | Move imagens corrompidas, rótulos vazios e órfãos para diretório de descarte |
| `auditar_dataset_final.py` | Contabiliza imagens, rótulos e caixas por subconjunto |

### 02 — Curadoria por similaridade visual (pHash)

| Script | Função |
|---|---|
| `pHash.py` | Calcula hashes perceptuais e identifica pares similares |
| `limpar_phash.py` | Remove imagens redundantes e gera conjunto limpo |
| `redistribuir_70_20_10.py` | Redistribui o conjunto entre treinamento, validação e teste |
| `verificar_vazamento.py` | Verifica vazamento de dados entre os três subconjuntos |

O `verificar_vazamento.py` percorre as três combinações possíveis entre
treinamento, validação e teste, sob o mesmo limiar de 90% adotado na
curadoria. Localiza o conjunto sozinho e grava o resultado em CSV:

```bash
python scripts/02_curadoria_phash/verificar_vazamento.py
```

Um CSV apenas com cabeçalho significa nenhum par acima do limiar, isto é,
ausência de vazamento. É o resultado reportado na Subseção 3.2.

### 03 — Revisão do critério de anotação

Etapa desenvolvida após identificar a coexistência de duas convenções de
anotação no conjunto: delimitação individual dos frutos e delimitação de
agrupamentos.

| Script | Função |
|---|---|
| `analise_bbox_grao_cacho.py` | Analisa a distribuição de tamanho das caixas delimitadoras |
| `triagem_bbox_suspeitas.py` | Separa arquivos com caixas incompatíveis com a convenção individual |
| `amostra_visual_bbox.py` | Gera amostra visual estratificada para inspeção |
| `organizar_dataset_limpo.py` | Monta subconjunto com anotações consistentes |
| `treinar_baseline.py` | Treina modelo auxiliar usado na sugestão de anotações |
| `gerar_preanotacoes_cacho.py` | Gera propostas de caixas individuais para os arquivos sinalizados |
| `visualizar_preanotacoes.py` | Gera amostra visual das pré-anotações produzidas |
| `consolidar_dataset_final.py` | Incorpora as anotações revisadas ao conjunto |
| `organizar_dataset_treino_final.py` | Organiza o conjunto consolidado para treinamento |

### 04 — Treinamento

| Script | Função |
|---|---|
| `treinar_final.py` | Treina YOLOv8n e YOLOv10n conforme o protocolo experimental |

### 05 — Conversão para TensorFlow Lite

| Script | Função |
|---|---|
| `converter_tflite.py` | Exporta os modelos nas precisões FP32, FP16 e INT8 |
| `validar_tflite.py` | Compara as saídas dos arquivos convertidos às do modelo em PyTorch |

### 06 — Classificação do estágio de maturação

Etapa subsequente à detecção: cada fruto detectado é recortado e
classificado quanto ao ponto de colheita.

| Script | Função |
|---|---|
| `mapear_cultivares.py` | Recupera a cultivar de origem de cada imagem, por nome e por hash perceptual |
| `extrair_crops.py` | Recorta os frutos anotados e organiza os recortes para rotulagem |
| `prerotular.py` | Atribui escore cromático de maturação e propõe classe aos recortes inequívocos |
| `rotulador.py` | Interface de rotulagem manual, sem exibir proposta automática |
| `validar.py` | Mede a concordância dos rótulos por reinspeção às cegas de amostra estratificada |
| `reiniciar.py` | Devolve os recortes à fila de pendentes, preservando o registro anterior |

A cultivar precisa ser identificada porque a mesma tonalidade corresponde a
estágios distintos conforme a cultivar: o amarelo é cereja na cultivar
amarela e verde-cana na vermelha.

### Figuras

| Script | Gera |
|---|---|
| `gerar_fig_bibliometria.py` | Figuras 2, 3 e 4, caracterização bibliométrica |
| `gerar_fig_anotacao.py` | Figura 9, exemplo de imagem anotada |
| `gerar_fig_distribuicao.py` | Figura 11, distribuição entre os subconjuntos |
| `gerar_fig_redundancia.py` | Figura 13, redundância detectada pelo pHash |
| `gerar_fig_treinamento.py` | Figura 15, curvas de perda e métricas do treinamento |
| `gerar_fig_curvas_pr.py` | Figura 16, curvas de precisão e revocação |
| `gerar_figuras.py` | Figuras 17, 18 e 19, desempenho em dispositivo |
| `exportar_curvas_pr_v2.py` | extrai do Ultralytics os pontos das curvas |

```bash
python scripts/figuras/gerar_fig_bibliometria.py \
    resultados/csv/bibliometria \
    monografia/figuras

python scripts/figuras/gerar_fig_anotacao.py \
    <dataset_final>/train/images/train_1048.jpg \
    <dataset_final>/train/labels/train_1048.txt \
    monografia/figuras/exemplo_anotacao.jpg

python scripts/figuras/gerar_fig_distribuicao.py monografia/figuras/distribuicao_particoes.pdf

python scripts/figuras/gerar_fig_redundancia.py \
    resultados/csv/duplicadas_phash.csv \
    monografia/figuras/redundancia_phash.pdf

python scripts/figuras/gerar_fig_treinamento.py \
    resultados/csv/results_yolov8n.csv \
    resultados/csv/results_yolov10n.csv \
    monografia/figuras/curvas_treinamento.pdf

python scripts/figuras/gerar_figuras.py \
    --entrada resultados/csv/medicoes_dispositivo \
    --saida monografia/figuras
```

---

## Reprodução dos experimentos

```bash
# Treinamento dos modelos
python scripts/04_treinamento/treinar_final.py \
    --data_yaml dataset_final/data.yaml \
    --modelos yolov8n yolov10n \
    --batch 8

# Conversão para TensorFlow Lite
python scripts/05_conversao/converter_tflite.py \
    --modelos runs/detect/runs_final/yolov8n_final_grao/weights/best.pt \
              runs/detect/runs_final/yolov10n_final_grao/weights/best.pt \
    --nomes yolov8n yolov10n \
    --data_yaml dataset_final/data.yaml
```

---

## Configuração de treinamento

| Parâmetro | Valor |
|---|---|
| Tamanho de entrada | 960 × 960 |
| Otimizador | AdamW |
| Taxa de aprendizado inicial | 0,003 |
| Tamanho do lote | 8 |
| Épocas (YOLOv10n) | 80 |
| Épocas (YOLOv8n) | 74 |
| Pesos iniciais | Pré-treinados em COCO |
| Critério de seleção | mAP@0,50 (validação) |

O tamanho de lote foi reduzido em relação ao previsto inicialmente (16)
devido à capacidade de memória da placa gráfica utilizada.

---

## Resultados obtidos

Métricas no conjunto de teste (285 imagens, 2.399 instâncias):

| Indicador | YOLOv8n | YOLOv10n |
|---|---|---|
| mAP@0,50 | 0,650 | 0,644 |
| mAP@0,50–0,95 | 0,360 | 0,375 |
| Precisão | 0,619 | 0,633 |
| Revocação | 0,626 | 0,625 |
| Parâmetros (milhões) | 3,01 | 2,27 |
| GFLOPs | 8,1 | 6,5 |
| Inferência (ms) | 9,2 | 8,7 |
| Pós-processamento (ms) | 1,9 | 0,3 |

As medições em dispositivo estão em `resultados/csv/medicoes_dispositivo/`,
um arquivo por configuração, nomeado `lote_<modelo>_<precisão>_<delegate>_<timestamp>.csv`.
São onze arquivos: o YOLOv10n em INT8 sobre GPU não executa, pelo
particionamento do grafo descrito no texto.

---

## Rastreabilidade

Cada figura e cada tabela do texto deve ter aqui o arquivo que a sustenta.

| No texto | Sustentado por |
|---|---|
| Figuras 2, 3 e 4 | `resultados/csv/bibliometria/` |
| Figura 9 | imagem `train_1048` do `dataset_final` e seu `.txt` |
| Figura 11 | `gerar_fig_distribuicao.py` |
| Figura 13 e Tabela 2 | `resultados/csv/duplicadas_phash.csv` |
| Figura 15 | `results_yolov8n.csv` e `results_yolov10n.csv` |
| Figura 16 | `resultados/csv/curva_pr_yolov8n.csv` e `curva_pr_yolov10n.csv` |
| Figuras 17, 18 e 19 | `resultados/csv/medicoes_dispositivo/` |
| Tabela 3, coluna *Antes* | `analise_bbox_grao_cacho.py` sobre `dataset_limpo` |
| Tabela 3, coluna *Depois* | `analise_bbox_grao_cacho.py` sobre `dataset_final` |
| Subseção 3.3.1 | `resultados/csv/relatorio_bboxes_suspeitas.csv` |
| Tabela 6 | `resultados/csv/tamanhos_modelos_tflite.csv` |
| Tabelas 7 e 8 | `resultados/csv/validacao_tflite.csv` |
| Tabelas 9 a 12 | `resultados/csv/medicoes_dispositivo/` |
| Subseção 3.2, vazamento | `resultados/csv/vazamento_entre_particoes.csv` |

Sobre `resultados/csv/bibliometria/`: as Figuras 2, 3 e 4 são construídas
a partir dos cinco exports da Scopus, um por tópico de busca. Os outros
dois arquivos da pasta, `coffee_yolo.csv` e `mobile_yolo.csv`, vêm da
base Dimensions e trazem exatamente 500 registros cada, o que indica
truncamento do export. Por isso não sustentam contagem de volume e não
são usados em nenhuma figura; ficam guardados como registro das buscas
realizadas.

A Tabela 3 é reproduzida pelo `analise_bbox_grao_cacho.py`, executado
duas vezes, uma por coluna:

```bash
python scripts/03_reanotacao/analise_bbox_grao_cacho.py --labels_dir <dataset_limpo>
python scripts/03_reanotacao/analise_bbox_grao_cacho.py --labels_dir <dataset_final>
```

Os cinco indicadores de cada coluna conferem com os publicados. O
percentil 99 da coluna *Antes* sai 0,5935 contra os 0,5931 da tabela,
diferença que decorre da convenção de interpolação do percentil.

Nenhum item do texto permanece sem origem rastreável no repositório.

---

## Ambiente utilizado

| Componente | Especificação |
|---|---|
| Processador | AMD Ryzen 5 5500 |
| Memória RAM | 16 GB DDR4 |
| Placa gráfica | NVIDIA GeForce RTX 3060 (8 GB) |
| Sistema operacional | Windows 11 Pro |
| CUDA | 12.x |
| PyTorch | 2.5.1 |
| Ultralytics | 8.4.36 |
| Python | 3.11 |

Dispositivo das medições: Samsung Galaxy S24 (SM-S921B), Exynos 2400,
GPU Xclipse 940, 8 GB de memória, Android 16.

---

## Etapas em andamento

- Rotulagem e validação dos recortes para a classificação do estágio de maturação
- Publicação do conjunto de imagens e dos pesos em repositório com DOI
