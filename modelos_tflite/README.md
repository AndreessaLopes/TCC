# Detecção de Frutos de Café em Dispositivos Móveis

Repositório de código do Trabalho de Conclusão de Curso **"Desempenho e Estabilidade de Modelos YOLO para Detecção da Maturação de Frutos de Café em Smartphones: comparação entre delegates TFLite"**.

**Autora:** Andressa Caroline Lopes de Assis
**Orientador:** Prof. Dr. Bruno Alberto Soares Oliveira
**Instituição:** IFMG — Campus Bambuí — Bacharelado em Engenharia de Computação

---

## Sobre o trabalho

A pesquisa compara configurações dos modelos YOLOv8n e YOLOv10n convertidos para TensorFlow Lite, avaliando o impacto de estratégias de quantização (FP32, FP16 e INT8) e de mecanismos de aceleração por hardware (delegates de CPU e GPU) sobre latência, estabilidade de execução, consumo energético e tamanho dos arquivos gerados em smartphones Android.

O conjunto de dados foi construído no âmbito de projeto de Iniciação Científica financiado pelo CNPq, a partir de imagens coletadas em lavouras cafeeiras de Bambuí, Minas Gerais, entre novembro de 2023 e fevereiro de 2024.

---

## Conjunto de dados

O conjunto de dados **não está versionado neste repositório** devido ao volume de arquivos.

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

Classe única: `graos`. Formato de anotação: YOLO.

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

Para a etapa de conversão para TensorFlow Lite, descomente as dependências correspondentes no `requirements.txt` e instale-as separadamente.

---

## Organização dos scripts

Os scripts estão numerados conforme a ordem de execução no fluxo metodológico.

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
| `phash_train_val.py` | Verifica vazamento de dados entre subconjuntos |
| `limpar_phash.py` | Remove imagens redundantes e gera conjunto limpo |
| `gerar_matriz_phash.py` | Gera a matriz de similaridade visual |
| `redistribuir_70_20_10.py` | Redistribui o conjunto entre treinamento, validação e teste |

### 03 — Revisão do critério de anotação

Etapa desenvolvida após identificar a coexistência de duas convenções de anotação no conjunto: delimitação individual dos frutos e delimitação de agrupamentos.

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

### Figuras

| Script | Função |
|---|---|
| `grafico_distribuicao_dataset.py` | Gera o gráfico de distribuição do conjunto de dados |

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

O tamanho de lote foi reduzido em relação ao previsto inicialmente (16) devido à capacidade de memória da placa gráfica utilizada.

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

---

## Etapas em andamento

- Conversão dos modelos para TensorFlow Lite
- Desenvolvimento da aplicação Android em Flutter
- Coleta de métricas de latência, estabilidade, consumo energético e temperatura
- Classificação do estágio de maturação dos frutos detectados

---

# Modelos TensorFlow Lite

Modelos de detecção convertidos para execução em dispositivos móveis, gerados a partir dos pesos treinados por meio do script `scripts/05_conversao/converter_tflite.py`.

## Arquivos

| Arquivo | Modelo | Precisão | Tamanho (MB) |
|---|---|---|---|
| `yolov8n_fp32.tflite` | YOLOv8n | FP32 | 11,96 |
| `yolov8n_fp16.tflite` | YOLOv8n | FP16 | 6,02 |
| `yolov8n_int8.tflite` | YOLOv8n | INT8 | 3,18 |
| `yolov10n_fp32.tflite` | YOLOv10n | FP32 | 9,17 |
| `yolov10n_fp16.tflite` | YOLOv10n | FP16 | 4,65 |
| `yolov10n_int8.tflite` | YOLOv10n | INT8 | 2,82 |

Para referência, os pesos originais em PyTorch ocupam 6,0 MB (YOLOv8n) e 5,5 MB (YOLOv10n).

## Especificações de entrada e saída

| Característica | YOLOv8n | YOLOv10n |
|---|---|---|
| Entrada | (1, 960, 960, 3) | (1, 960, 960, 3) |
| Saída | (1, 5, 18900) | (1, 300, 6) |
| Pós-processamento | Requer supressão não máxima | Não requer |

A diferença no formato de saída decorre da arquitetura. O YOLOv8n produz 18.900 candidatos que precisam ser filtrados por supressão não máxima na aplicação. O YOLOv10n, por ser NMS-free, entrega diretamente até 300 detecções já ordenadas, no formato `[x1, y1, x2, y2, confiança, classe]`.

## Parâmetros de conversão

| Parâmetro | Valor |
|---|---|
| Resolução de entrada | 960 × 960 |
| Opset ONNX | 19 |
| Classe | `graos` (classe única) |
| Calibração INT8 | Conjunto de validação (473 imagens) |

## Custo de conversão

| Variante | Tempo |
|---|---|
| YOLOv8n FP32 | 154 s |
| YOLOv8n FP16 | 13 s |
| YOLOv8n INT8 | 2.265 s |
| YOLOv10n FP32 | 35 s |
| YOLOv10n FP16 | 25 s |
| YOLOv10n INT8 | 3.567 s |

O custo elevado das variantes INT8 decorre da etapa de calibração, na qual as imagens do conjunto de validação são processadas para determinar as faixas de valores das ativações em cada camada. Trata-se de custo pago uma única vez, em ambiente de desenvolvimento.

## Validação

As métricas de detecção de cada variante no conjunto de teste estão registradas em `resultados/csv/validacao_tflite.csv`, geradas por `scripts/05_conversao/validar_tflite.py`.

## Reprodução

```bash
python scripts/05_conversao/converter_tflite.py \
    --modelos runs/detect/runs_final/yolov8n_final_grao/weights/best.pt \
              runs/detect/runs_final/yolov10n_final_grao/weights/best.pt \
    --nomes yolov8n yolov10n \
    --data_yaml dataset_final/data.yaml \
    --saida_dir modelos_tflite
```

Dependências adicionais necessárias para a conversão:

```bash
pip install onnx onnx2tf onnxslim tensorflow sng4onnx onnx_graphsurgeon
```

## Observação sobre versões

A biblioteca Ultralytics realiza atualização automática de dependências durante a primeira exportação, o que pode alterar a versão do TensorFlow em uso. Caso a conversão apresente erro relacionado à operação TopK do YOLOv10, execute o comando novamente em um novo processo, para que as versões atualizadas sejam carregadas corretamente.
