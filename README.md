# Detecção de frutos de café em smartphones Android

Repositório de código, modelos convertidos e dados de medição do Trabalho
de Conclusão de Curso *Desempenho e Estabilidade de Modelos YOLO para
Detecção de Frutos de Café em Smartphones: comparação entre delegates
TFLite*.

| | |
|---|---|
| Autora | Andressa Caroline Lopes de Assis |
| Orientador | Prof. Dr. Bruno Alberto Soares Oliveira |
| Instituição | Instituto Federal de Minas Gerais, *Campus* Bambuí |
| Curso | Bacharelado em Engenharia de Computação |
| Licença | AGPL-3.0-or-later para o código, CC BY 4.0 para o conteúdo textual |

## Objeto do trabalho

O trabalho compara configurações dos modelos YOLOv8n e YOLOv10n
convertidos para TensorFlow Lite quanto à latência de inferência, à
estabilidade de execução ao longo da sessão e ao pico de memória do
processo, em smartphones Android. As configurações combinam duas
arquiteturas, três precisões numéricas, FP32, FP16 e INT8, e dois
mecanismos de aceleração, os *delegates* de processador e de processador
gráfico, o que perfaz doze combinações, das quais onze são executáveis.

O resultado central é que o ganho do *delegate* de processador gráfico
depende da cobertura de operações do acelerador, e não do custo
computacional do modelo. O YOLOv8n é acelerado por fator entre 3,58 e
4,72 conforme a precisão, enquanto o YOLOv10n não obtém ganho algum, pois
as operações que implementam sua arquitetura sem supressão não máxima não
são suportadas pelo *delegate*, o que força o particionamento do grafo e
inviabiliza por completo a execução na precisão INT8.

A avaliação principal foi conduzida sobre as 285 imagens da partição de
teste em um aparelho de referência. A verificação de alcance foi estendida
a oito aparelhos de três fornecedores de *System on Chip*, da faixa de
entrada ao segmento superior, sobre um subconjunto de 30 imagens.

## O que este repositório contém

| Diretório | Conteúdo |
|---|---|
| `scripts/` | Oitenta e nove scripts, organizados por etapa do trabalho, do pré-processamento à geração das tabelas e figuras |
| `modelos_tflite/` | As seis variantes convertidas, nas três precisões, para as duas arquiteturas |
| `cafescan/` | Aplicação Android em Flutter empregada na medição em dispositivo |
| `resultados/` | Dezessete arquivos CSV com as medições, além das figuras geradas |
| `monografia/` | Fontes LaTeX do documento, tabelas geradas por script e figuras |

## O que este repositório não contém

O conjunto de imagens de lavoura não integra o depósito. As imagens foram
adquiridas em propriedades privadas no município de Bambuí, Minas Gerais,
e sua divulgação depende de autorização específica dos proprietários, ainda
não obtida. O repositório traz, em contrapartida, os arquivos de medição
que sustentam cada número publicado, de modo que as tabelas e as figuras do
documento podem ser regeradas sem acesso às imagens.

Os pesos em formato PyTorch também não são versionados, por volume. As
variantes convertidas para TensorFlow Lite, que são as efetivamente
avaliadas no dispositivo, estão disponíveis em `modelos_tflite/`.

## Procedência dos resultados

Cada tabela do documento é gerada por script a partir de um arquivo de
medição versionado, e não digitada à mão. A correspondência é a seguinte.

| Medição | Arquivo | Gerador |
|---|---|---|
| Indicadores de detecção | `resultados/csv/metricas_teste.csv` | `scripts/04_treinamento/avaliar_teste.py` |
| Sensibilidade à anotação assistida | `resultados/csv/metricas_teste_limpo.csv` | `scripts/04_treinamento/avaliar_teste_limpo.py` |
| Latência em dispositivo | `resultados/csv/medicoes_dispositivo/` | Aplicação `cafescan` |
| Coleta em oito aparelhos | `resultados/csv/multidispositivo/` | `scripts/07_multidispositivo/` |
| Intervalos de confiança e testes | `resultados/csv/intervalos_bootstrap*.csv` | `scripts/09_estatistica/intervalos_bootstrap.py` |
| Revocação por faixa de tamanho | `resultados/csv/deteccoes_por_tamanho.csv` | `scripts/09_estatistica/gerar_tabela_tamanho.py` |

## Reprodução

O ambiente de treinamento e de conversão exige Python 3.11 e os pacotes
relacionados em `requirements.txt`.

```
python -m venv venv
venv/Scripts/activate        # Windows
pip install -r requirements.txt
```

As etapas, na ordem em que foram executadas, correspondem à numeração dos
diretórios em `scripts/`. O treinamento e a avaliação dependem do conjunto
de imagens, ausente pelo motivo exposto acima. As etapas estatísticas e de
geração de tabelas operam apenas sobre os arquivos CSV versionados e podem
ser executadas de imediato.

```
python scripts/09_estatistica/intervalos_bootstrap.py
python scripts/09_estatistica/gerar_tabelas_bootstrap.py
```

A compilação do documento exige uma distribuição TeX com `biber`, o pacote
`biblatex` e os arquivos de idioma português.

```
cd monografia
pdflatex artigo.tex && biber artigo && pdflatex artigo.tex && pdflatex artigo.tex
```

## Delimitação

Os valores de latência total reportados caracterizam a aplicação
desenvolvida, e não o limite da plataforma, uma vez que o
pré-processamento responde pela maior parte do tempo e não foi objeto de
otimização. A comparação entre *delegates*, que é o objeto do trabalho,
incide sobre a etapa de inferência. As limitações de protocolo, de medida,
de conjunto de dados e de escopo estão declaradas na seção própria do
documento.

## Como citar

Os campos de citação estão em `CITATION.cff`, em formato legível por
máquina. O depósito no Zenodo possui identificador persistente próprio,
informado na página do repositório após a publicação da primeira versão.

## Financiamento

O conjunto de imagens foi construído no âmbito de projeto de Iniciação
Científica financiado pelo Conselho Nacional de Desenvolvimento Científico
e Tecnológico, CNPq, e desenvolvido no Instituto Federal de Minas Gerais,
*Campus* Bambuí.

## Licença

O código é distribuído sob a licença AGPL-3.0-or-later, cujo texto integral
consta em `LICENSE`. O conteúdo textual e as figuras seguem a licença
Creative Commons Atribuição 4.0 Internacional, conforme `LICENSE-CONTEUDO.md`.
