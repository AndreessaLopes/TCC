# Parecer técnico, na perspectiva de revista A1

Escrito em 2026-11-03 sobre a versão de 81 páginas. Formatação ignorada
por solicitação. O parecer é deliberadamente severo: o objetivo é
antecipar o que levaria à recusa, não avaliar o mérito do TCC, que é
outra coisa.

## Recomendação

**Revisão maior**, com risco real de recusa em A1 por contribuição
insuficiente. O trabalho é sólido como estudo de caracterização, e o
achado sobre a incompatibilidade do YOLOv10 com o delegate de GPU tem
valor próprio. O que falta para A1 não é correção de erro: é escala
experimental e uma pergunta de pesquisa que vá além da medição.

---

## 1. Riscos eliminatórios

### 1.1 Contribuição percebida como benchmark de escopo estreito

Duas arquiteturas, ambas na variante nano, três precisões, dois
delegates, um aparelho na avaliação completa. Revisor de A1 pergunta o
que o trabalho acrescenta além de medir uma combinação específica.

A resposta existe e está no texto, mas aparece tarde e diluída: operações
não suportadas pelo acelerador forçam o particionamento do grafo e anulam
o ganho, de modo que a propriedade que torna o YOLOv10 atraente, a
eliminação da supressão não máxima, é a mesma que o inviabiliza em GPU
móvel. Esse é um resultado de mecanismo, não de medição, e é o único
elemento do trabalho que sustenta uma submissão A1.

**O que fazer.** Reescrever o artigo em torno desse mecanismo, com o
restante servindo de evidência. Título, resumo e introdução precisam
anunciá-lo. Hoje anunciam uma comparação de desempenho.

### 1.2 Treinamento em execução única, sem variação de semente

O Quadro de hiperparâmetros declara semente 0 em modo determinístico, o
que garante reprodutibilidade mas não informa variabilidade. Toda a
comparação entre arquiteturas repousa sobre um treinamento de cada.

A diferença de 0,0036 no mAP@0,50 entre YOLOv8n e YOLOv10n está dentro
da faixa que a troca de semente costuma produzir. O texto reconhece que
não houve teste de equivalência, o que é honesto, mas a consequência é
mais severa do que o texto admite: **nenhuma afirmação comparativa sobre
qualidade de detecção entre as duas arquiteturas se sustenta com n igual
a um.**

**O que fazer.** Treinar cada arquitetura com três a cinco sementes e
reportar média e intervalo. É a correção de maior impacto por unidade de
esforço em todo este parecer. Sem ela, o revisor risca todas as
comparações de mAP.

### 1.3 Latência total caracteriza a aplicação, não a plataforma

O pré-processamento responde por 77% a 96% da latência total e não foi
otimizado. Os valores de latência total e de quadros por segundo,
portanto, descrevem uma implementação em Flutter não otimizada, e não o
que a plataforma permite.

O texto declara isso nas limitações, mas o resumo e a conclusão ainda
reportam latência total e recomendam configuração com base nela. Revisor
de revista de sistemas vai apontar que o gargalo medido é de engenharia
da aplicação, não do objeto de estudo.

**O que fazer.** Separar com clareza o que é medida da plataforma, a
latência de inferência, do que é medida da aplicação, a latência total.
Reportar a segunda apenas como contexto, com a ressalva no próprio
resumo.

### 1.4 Ausência de declaração de disponibilidade de dados e código

O artigo não menciona repositório em passagem alguma. Periódicos A1 em
computação aplicada exigem declaração de disponibilidade, e a ausência
sozinha gera pedido de revisão.

**O que fazer.** Criar a seção de disponibilidade, com o endereço do
repositório e o identificador persistente. O repositório já existe e
contém código, modelos convertidos e todos os CSV de medição. Falta
publicá-lo e cita-lo.

---

## 2. Problemas metodológicos sérios

### 2.1 Revocação de 0,61 e a aplicação proposta

Aproximadamente 39% das instâncias anotadas não são detectadas. Para uma
aplicação que se propõe a apoiar a avaliação de maturação do talhão,
isso é limitante, e o trabalho não discute o efeito dessa perda sobre a
estimativa agregada.

A estratificação por tamanho, acrescentada recentemente, mostra que a
perda não se concentra nos objetos pequenos, que são 70 das 2.399
instâncias, e sim na faixa média, com 537 das 898 não detectadas. Isso
desloca a explicação para oclusão e anotação agrupada, que o texto cita
mas não quantifica.

**O que fazer.** Quantificar a oclusão, ainda que por amostragem
manual de 50 imagens, e discutir explicitamente se um detector com
revocação de 0,61 serve à estimativa de proporção de maduros. Pode
servir, se o viés for homogêneo entre estágios; é preciso argumentar.

### 2.2 Resolução de entrada não submetida a ablação

Entrada de 960 pixels, sem comparação com 640. Como o pré-processamento
domina a latência e como a revocação depende do tamanho do objeto, a
resolução é o parâmetro que governa simultaneamente os dois eixos do
trabalho, e não foi variado.

**O que fazer.** Treinar e avaliar em 640. É experimento de custo
moderado e alto retorno argumentativo.

### 2.3 Quantização consciente de treinamento ausente

O trabalho compara apenas quantização pós-treinamento. Diante da perda
de 6,1% no mAP do YOLOv8n em INT8, o revisor pergunta por que a
alternativa canônica não foi testada. A recomendação final poderia mudar.

**O que fazer.** Ou testar, ou justificar o recorte pelo cenário de quem
converte modelo já treinado, e declarar isso na metodologia.

### 2.4 Estado térmico inferido, não medido

A deriva de 42% a 57% em GPU é atribuída a limitação térmica sem medição
de temperatura. O texto já declara a limitação. Permanece que a
explicação alternativa, fragmentação de memória ou governador de
frequência, não foi descartada.

**O que fazer.** A temperatura da bateria é acessível por interface
pública e serve de aproximação. Uma coleta nova no aparelho de
referência resolve.

### 2.5 Coleta em múltiplos dispositivos de caráter exploratório

Trinta imagens por execução, número variável de sessões, um exemplar de
cada modelo, dois aparelhos com desvio de protocolo no aquecimento e um
iniciado com 54% de bateria. O texto declara tudo isso, o que é correto,
e por isso a coleta sustenta a direção do efeito e não a magnitude.

Para A1, isso basta como evidência de generalidade do mecanismo, desde
que o artigo não extraia dela mais do que direção. Hoje não extrai.

### 2.6 Versões não reportadas

Não constam a versão do TFLite ou LiteRT embarcada no aplicativo, nem a
versão do driver gráfico dos oito aparelhos. Como o achado central é uma
incompatibilidade de operações com o delegate, e como delegates mudam
entre versões, **o resultado pode ser específico de uma versão**.

**O que fazer.** Reportar as versões. Idealmente, repetir o caso do
YOLOv10 INT8 em GPU em uma versão mais recente do LiteRT e declarar se
persiste. Este é o ponto em que o artigo é mais vulnerável: um revisor
que execute em versão nova e não reproduza o erro rejeita o trabalho.

### 2.7 Causa raiz do erro não investigada

O YOLOv10 INT8 em GPU falha com erro de incompatibilidade de lote. O
texto reporta o erro e a contagem de operações delegadas, mas não
investiga se decorre de limitação do conversor, do delegate ou da forma
do grafo exportado.

---

## 3. Lacunas que o revisor vai cobrar

- Comparação com outros detectores voltados a dispositivos móveis, como
  MobileNet-SSD, NanoDet ou EfficientDet-Lite. O trabalho compara YOLO
  com YOLO.
- Ausência de YOLOv11 e YOLOv12, posteriores ao recorte, sem
  justificativa explícita do recorte.
- Sensibilidade ao limiar de confiança, fixado em 0,25, não avaliada.
- Sensibilidade ao conjunto de calibração do INT8, de 473 imagens, não
  avaliada.
- Independência entre partições verificada por pHash, o que é bom, mas
  não declarada como independência por planta ou por sessão de captura.
  Se as mesmas plantas aparecem em treino e teste, o desempenho é
  otimista. **Isto precisa ser verificado e declarado.**
- Intervalos de confiança existem para latência e não para mAP.

---

## 4. O que está acima da média e o revisor vai reconhecer

- Conjunto de dados próprio, com curadoria documentada e verificação de
  redundância por pHash.
- Procedência dos números: tabelas geradas por script a partir de CSV
  versionados, com as configurações de execução registradas.
- Tratamento estatístico da latência, com intervalo por reamostragem e
  teste de permutação corrigido para comparações múltiplas.
- Transparência sobre desvios de protocolo, medidos em vez de omitidos.
- O achado da incompatibilidade, com a contagem de operações delegadas,
  que é explicação de mecanismo e não apenas observação.
- Delimitação explícita do que não foi feito.

---

## 5. Avaliação de encaixe

Como está, com as correções de 1.2, 1.3 e 1.4, o artigo é competitivo em
periódico de estrato intermediário na área de computação aplicada à
agricultura, ou em revista de sistemas embarcados de escopo aplicado.

Para A1, é necessário acrescentar o que falta em 1.1, 2.2 e 2.6: a
reescrita em torno do mecanismo, a ablação de resolução e a verificação
da persistência do achado entre versões do delegate. Sem isso, a
probabilidade de recusa na triagem editorial é alta, não por erro, mas
por contribuição considerada incremental.
