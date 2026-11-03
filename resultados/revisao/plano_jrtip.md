# Dos três pareceres ao artigo para a JRTIP

Escrito em 2026-11-03. Consolida o parecer próprio, o relatório do
DeepSeek e o relatório do GPT, separando o que foi verificado no
`artigo.tex` e nos dados do que é artefato de leitura do PDF.

---

## 1. Triagem dos três relatórios

### 1.1 O relatório do DeepSeek: a maior parte é artefato

Os pontos que ele classifica como eliminatórios foram conferidos no
código-fonte e **não existem**:

| Alegação | Verificação |
|---|---|
| Tabela 14 com linha duplicada "YOLOv10n INT8 CPU" (2.309 e 2.325) | Falso. As linhas são FP16 CPU 2.309, FP16 GPU 2.309 e INT8 CPU 2.325. Não há duplicata |
| Seções 4.7.4, 5.1, 5.2 e 5.3 com texto corrompido ou vazio | Falso. Todas existem com conteúdo, nas linhas 2191, 2270, 2284 e 2324 |
| Quadro 1 truncado, Tabelas 17 a 19 e Tabela 2 com cabeçalhos fundidos | Falso. Artefato da extração de texto do PDF |
| `<tr>` no Quadro 3 | Falso. Zero ocorrências de marcação HTML no documento |
| Tabela 6 com 702, 1.276 e 1.053 instâncias, somando 126% | Falso. Os valores são 70, 1.276 e 1.053. O percentual foi inventado |

É a quarta vez que um revisor externo reporta corrupção inexistente. A
causa é a extração de texto do PDF na ponta dele, não o documento.

**Aproveitável do DeepSeek:** a ausência de QAT sem justificativa, a
sugestão de reportar mAP estratificado por faixa além da revocação, a
nota ética sobre autorização dos proprietários, e a observação de que
`ANDROID DEVELOPERS. NNAPI Migration Guide` consta nas referências. Esse
último é verificável e precisa ser conferido.

### 1.2 O relatório do GPT: o mais forte dos três

Levanta cinco pontos reais que nem eu nem o DeepSeek havíamos
identificado. Todos foram confirmados no fonte.

### 1.3 O meu parecer

Continua válido no essencial. O GPT me supera em dois pontos: a
circularidade do *ground truth* e a assimetria do treinamento, que eu
não havia visto.

---

## 2. Os cinco achados novos, verificados e quantificados

### 2.1 Circularidade do *ground truth*, agora medida

É o achado mais grave de todos os três relatórios, e o único capaz de
sozinho justificar uma recusa.

O procedimento está descrito nas linhas 896 a 955. A triagem
automatizada sinalizou 836 arquivos com caixas fora da convenção
individual. Um YOLOv8n auxiliar, treinado apenas com a partição de
treino dos arquivos limpos, propôs 4.231 caixas nesses 836 arquivos. As
anotações resultantes foram submetidas a inspeção visual **por
amostragem**, não integral.

Cruzei `relatorio_bboxes_suspeitas.csv` com `dataset_final/test/labels`:

| Medida | Valor |
|---|---|
| Arquivos sinalizados | 836 |
| Deles, na partição de treino | 569 |
| **Deles, na partição de teste** | **91 de 285, ou 31,9%** |
| Instâncias de teste em imagens afetadas | **789 de 2.399, ou 32,9%** |

Cerca de um terço do padrão-ouro contra o qual o YOLOv8n é avaliado foi
proposto por um YOLOv8n, sem revisão manual completa. Isso tende a
inflar o mAP de ambos os modelos e a favorecer sistematicamente a mesma
família de arquitetura, o que compromete justamente a comparação entre
YOLOv8n e YOLOv10n.

O texto não declara essa sobreposição. Um revisor que a descubra sozinho
recusa o artigo.

**Correção barata, a fazer antes de qualquer outra.** Reavaliar os dois
modelos apenas nas 194 imagens de teste não afetadas e comparar com o
resultado sobre as 285. Se o mAP se mantiver, a objeção fica neutralizada
com evidência, e basta um parágrafo. Se divergir, o número honesto passa
a ser o das 194. Custa algumas horas, e o script `avaliar_teste.py` já
faz tudo menos o recorte.

**Correção definitiva, para o artigo.** Reanotar manualmente as 91
imagens afetadas, de preferência com um segundo avaliador e registro de
concordância.

### 2.2 Treinamento assimétrico entre as duas arquiteturas

Linhas 1052, 1053 e 1612. O YOLOv8n foi configurado para 120 épocas e
parou por paciência na época 74, portanto convergiu. O YOLOv10n foi
configurado para 80 épocas, executou as 80, e **seu melhor desempenho
ocorreu na época 79**, isto é, ainda estava melhorando quando o
treinamento terminou.

A comparação de acurácia entre as arquiteturas, e toda a análise de
quantização que dela deriva, repousa sobre um modelo convergido e outro
truncado. O YOLOv10n pode estar subtreinado.

**Correção.** Retreinar o YOLOv10n com 120 épocas e paciência de 30, o
mesmo critério do YOLOv8n. É um treinamento, não um redesenho.

### 2.3 Contradição entre o resumo e a Tabela 18

O corpo do texto contradiz a si mesmo em dois parágrafos consecutivos:

- Linha 2061: "O YOLOv8n é acelerado em todas as plataformas, por fator entre 1,07 e 7,28"
- Linha 2074: "A única exceção ao ganho do YOLOv8n ocorre no moto~g15 na precisão INT8, com razão de 0,87"

O resumo (linha 69) e a conclusão (linha 2293) repetem a primeira
formulação e omitem a exceção. A alegação central do artigo, no lugar
mais visível dele, está em desacordo com a própria tabela.

**Correção.** Redação, custo baixo, prioridade máxima. A formulação
proposta pelo GPT serve: em 23 das 24 combinações aparelho e precisão do
YOLOv8n o delegate reduziu a latência, com razões de 1,07 a 7,28; a
exceção foi INT8 no moto g15, com 0,87.

### 2.4 Limiar de confiança justificado pelo conjunto de teste

Linha 1634: "O maior valor de F1 ocorre em limiar de 0,24 no YOLOv8n e
de 0,27 no YOLOv10n, o que respalda o limiar de 0,25 adotado na
aplicação." As curvas são explicitamente do conjunto de teste
(linha 1624).

Usar o teste para respaldar uma escolha operacional contamina a
estimativa final.

**Correção.** O limiar de 0,25 é o padrão do framework, adotado a
priori. Basta declarar isso e apresentar a coincidência com o F1 máximo
como verificação posterior, não como justificativa. Uma frase resolve, e
a objeção desaparece.

### 2.5 Número desigual de medições sem regra declarada

Linhas 1791 a 1795. As execuções em GPU registram 284, 283 e 281
medições em vez de 285. O descarte existe e é mencionado, mas a regra
que o governa não está declarada no texto, e as causas não são
listadas.

**Correção.** Declarar a regra e listar as falhas por configuração.

---

## 3. Encaixe com o Journal of Real-Time Image Processing

### 3.1 O que a revista é

Springer, fator de impacto 4,9 em 2025, cinco anos 3,3. Dedicada
exclusivamente aos aspectos de tempo real do processamento de imagem e
vídeo. Cobre complexidade computacional, taxa de quadros, implementação
em hardware e otimização de software em tempo real. A página da revista
afirma que uma submissão precisa tratar e discutir questões de tempo
real para ser enviada à revisão. Artigos recentes incluem comparação de
modelos YOLO e implantação em NPU de borda.

O assunto do trabalho cabe. O problema é outro.

### 3.2 O obstáculo específico desta revista

A aplicação opera entre 0,44 e 0,62 quadros por segundo. Submeter a uma
revista de tempo real uma aplicação a meio quadro por segundo é um
convite à recusa editorial antes da revisão.

A inferência, isolada, é outra história: 64,5~ms no YOLOv8n FP32 em GPU,
cerca de 15 quadros por segundo. A distância entre 15 e 0,5 é o
pré-processamento em Dart, que responde por 77% a 96% do tempo total.

### 3.3 O que isso sugere, e é favorável

Essa distância não é um defeito a esconder. É a contribuição que a
revista procura. A pergunta "por que acelerar a inferência em 4,7 vezes
não produz ganho algum na aplicação" é exatamente uma questão de
sistemas de tempo real, e a resposta do trabalho tem duas partes
mensuradas: o pré-processamento domina o orçamento de tempo, e a
compatibilidade de operadores governa se o acelerador serve.

Para sustentar esse enquadramento é preciso otimizar o
pré-processamento e medir de novo. Sem isso, o revisor responde que o
gargalo é de engenharia da aplicação e devolve o artigo. Com isso, o
artigo mostra o antes e o depois, e o achado passa a ser quantitativo.

### 3.4 Alternativas, caso o caminho acima não caiba no tempo

Sem a otimização do pré-processamento, o trabalho continua publicável,
em revista de computação aplicada à agricultura ou de sistemas
embarcados de escopo aplicado, onde a taxa de quadros não é o critério
de admissão. A escolha entre os dois caminhos é de prazo, não de mérito.

---

## 4. Plano

### 4.1 Até 09/11, para o TCC

O TCC não precisa do artigo resolvido. Precisa de consistência interna.
São quatro itens, todos de redação ou de reprocessamento leve.

1. Corrigir a contradição do resumo e da conclusão sobre o moto g15 (2.3)
2. Declarar o limiar de 0,25 como escolha a priori (2.4)
3. Declarar a sobreposição entre os 836 arquivos reanotados e a partição
   de teste, com os números apurados, na seção de limitações (2.1)
4. Declarar a assimetria do critério de parada entre as arquiteturas
   (2.2) e a regra de descarte das medições (2.5)

Se houver folga, acrescentar a reavaliação nas 194 imagens não afetadas.
É o item de maior retorno e custa algumas horas.

### 4.2 Depois da defesa, para a JRTIP

Por ordem de dependência, não de preferência.

| Etapa | O que envolve | Ordem de grandeza |
|---|---|---|
| Reanotar as 91 imagens de teste afetadas | Trabalho manual, de preferência com segundo avaliador | 1 semana |
| Retreinar o YOLOv10n com critério simétrico | Um treinamento | 2 dias |
| Treinar com 3 a 5 sementes por arquitetura | Repetições, reportar média e intervalo | 1 semana |
| Otimizar o pré-processamento e medir de novo | A condição de admissão da JRTIP | 2 semanas |
| Reportar versões de LiteRT, driver e opções do delegate | Documentação, e repetir o caso do YOLOv10n INT8 em versão recente | 3 dias |
| Ablação de resolução, 640 contra 960 | Treino e avaliação | 1 semana |
| Publicar repositório, DOI e declaração de disponibilidade | Zenodo, licença, README | 2 dias |
| Reescrever em torno do mecanismo e comprimir | A narrativa de tempo real | 2 semanas |

Trabalhando em paralelo onde é possível, é da ordem de dois a três
meses. Não é um artigo para submeter em novembro.

### 4.3 O que não fazer

Não refazer tabelas, quadros ou seções por causa do relatório do
DeepSeek. Nada do que ele classificou como eliminatório existe no
documento.
