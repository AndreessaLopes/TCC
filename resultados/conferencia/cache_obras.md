# O que cada obra sustenta

Registro do que foi conferido na fonte, para não reabrir a obra quando
ela reaparecer dizendo o mesmo. Conferido em 2026-11-03.

## CONAB2025 — primeira estimativa da safra 2025
Produção brasileira estimada em 51,8 milhões de sacas; Minas Gerais com
24,8 milhões, equivalente a 47,9%. Traz a produção mundial estimada pelo
USDA para 2024/25, de 174,9 milhões de sacas, **sem** relacionar as duas
em percentual. Não afirma participação do Brasil na produção mundial.

## Bazame2021Detection — Computers and Electronics in Agriculture 183, 106066
YOLOv3-Tiny no Darknet, transferência de aprendizado a partir de pesos do
COCO. Três classes de maturação: verde, cereja e passa. 400 quadros
extraídos de vídeos de colheita, 280 para treino e 120 para validação.
Melhor resultado com entrada de 800~×~800. mAP 84%, precisão 83%,
revocação 82%, F1 82%. AP por classe: 86% verde, 85% maduro, 80% passa.
Observação: a conclusão do próprio artigo traz precisão 82% e revocação
83%, divergindo do resumo e dos resultados; o TCC usa os valores do
resumo, que são os corretos.

## Kazama2024Monitoring — Scientia Horticulturae 328, 112957
YOLOv8 com RFCAConv, comparado ao YOLOv8n padrão. Quatro classes: verde,
semimaduro, maduro e sobremaduro. mAP@0,50 de 74,20%, 1,90 ponto
percentual acima do padrão. AP por classe: 73,40%, 67,10%, 74,40% e
71,90%. Compara iluminação natural e artificial e enquadramentos de
planta inteira, ramos e ramos sobre fundo controlado; o melhor
enquadramento rendeu 72,70%.

## Eron2024Computer — Scientia Horticulturae 331, 112847
YOLOv7 para detecção e classificação de frutos de café por estágio, com
estimativa de maturação como proporção de maduros. Aplicativo CoffeApp em
Flutter com processamento no servidor. Não avalia desempenho em
smartphone, não reporta latência nem consumo no aparelho.

## Thai2024Coffee — IEEE Access 12, 126503--126517
YOLOv8 e OpenCV para classificação de defeitos em grãos de café verdes,
segundo o padrão da Specialty Coffee Association, testado em nove
variedades. Aplicativo em React Native com NodeJS e Python, integrado a
solução em nuvem. Tempo necessário entre 1 e 3 segundos. O resumo não
afirma que a inferência ocorre na nuvem nem descreve requisitos de
conexão.

## Gope2024Comparative — Scientific Reports 14
Compara YOLOv3, YOLOv4, YOLOv5, YOLOv7, YOLOv8 e modelos personalizados
para detecção de grãos de café verdes e classificação de defeitos. O
custom-YOLOv8n apresentou o melhor desempenho. Conjunto de 4.032 imagens
de treino e 506 de teste. Não avalia execução em smartphones. **Os
valores de precisão, revocação, F1 e mAP não puderam ser conferidos**,
por o texto completo não estar acessível deste ambiente.

## Ye2025ASD — Frontiers in Plant Science 16
ASD-YOLO sobre YOLOv7, com atenção L-Norm, SPD-Conv e DySample.
Revocação 78,4%, precisão 69,8%, mAP 80,1%, ganho de 2,1 pontos sobre o
YOLOv7. Não avalia execução em smartphones. O resumo não informa o limiar
de IoU do mAP relatado.

## Li2024Benchmark — EdgeSys '24, DOI 10.1145/3642968.3654818
Protocolos de avaliação de inferência móvel com fixação de frequências e
resfriamento ativo para conter degradação térmica.

## Tan2018TransferLearning — arXiv 1808.01974
Levantamento sobre transferência de aprendizado profundo. Preprint de
2018, sem registro de publicação em periódico na página do repositório.

## Mumuni2022DataAugmentation — Array 16, 100258
Levantamento sobre aumento de dados.

## Android2026NNAPI e GoogleAIEdge2026GPU
Depreciação da NNAPI a partir do Android~15 com recomendação de migração
para o TFLite; operações não suportadas pelo delegate de GPU levam a
particionamento do grafo, cujo custo de sincronização torna o resultado
com frequência mais lento do que a execução integral em CPU.

## Wang2024YOLOv10 — arXiv 2405.14458
Treinamento sem supressão não máxima por atribuição dupla consistente,
voltado à implantação de ponta a ponta. No COCO com entrada de 640, o
YOLOv10-N apresenta AP de 38,5%, 2,3 milhões de parâmetros, 6,7 bilhões
de operações e latência de 1,84~ms; o YOLOv10-X apresenta AP de 54,4%,
29,5 milhões de parâmetros e latência de 10,70~ms. Confere com o texto.

## Menghani2023Efficient — ACM Computing Surveys 55, arXiv 2106.08962
Levantamento sobre compressão, aprendizado, automação, arquiteturas
eficientes e infraestrutura, cobrindo poda, quantização pós-treinamento e
consciente de treinamento, fatoração de baixo posto e destilação.
Defende escolher o modelo pelos compromissos que importam à aplicação.
Observação útil: no exemplo do próprio levantamento, a quantização
pós-treinamento do MobileNet~v2 reduz o arquivo de 14~MB para 3,6~MB mas
**aumenta** a latência, de 89 para 98~ms, ao passo que a quantização
consciente de treinamento a reduz para 54~ms. O ganho de latência em
INT8, portanto, não é automático, o que coincide com o medido neste TCC.

## Chu2023nnPerf — SenSys '23, DOI 10.1145/3625687.3625797
Ferramenta de profiling em tempo real, executada no próprio aparelho,
implementada sobre o TFLite, que mede latência de ponta a ponta, por
operador e por núcleo, avaliada em quatro plataformas móveis em CPU e em
GPU. O resumo **não** apresenta variação de comportamento de delegates
entre SoC como resultado.

## Alzubaidi2021Review — Journal of Big Data 8, 53
Revisão ampla de aprendizado profundo, com conceitos, categorias de
aprendizado, evolução das arquiteturas de CNN da AlexNet à HRNetV2 e
aplicações. Trata a CNN como a rede mais usada e adequada a dados
bidimensionais. Lista como desafios a falta de dados de treinamento, o
sobreajuste, o desbalanceamento, a interpretabilidade e a compressão de
modelos; o custo computacional aparece de forma indireta.

## Cecafe2025 — Agrolink, reproduzindo dado do Cecafé
Faturamento bruto da cadeia produtiva do café estimado em R$ 125,7
bilhões no ano-cafeeiro de 2025, calculado sobre os preços médios
recebidos pelos produtores entre janeiro e março. A notícia **não**
menciona empregos. Observação: o valor foi revisto em divulgações
posteriores, que trazem R$ 123,28 bilhões e R$ 127,88 bilhões, de modo
que convém manter a referência à publicação citada.

## Bochkovskiy2020YOLOv4 — arXiv 2004.10934
Apresenta o Mosaic como novo método de aumento de dados, que combina
quatro imagens de treinamento e mistura quatro contextos, com o objetivo
declarado de detectar objetos fora do contexto habitual e reduzir a
necessidade de minilotes grandes. Confere com o texto.

## Obras conferidas pelo próprio objeto
Flutter2024, documentação do framework Flutter; Makesense2024, a
ferramenta de anotação MakeSense.ai; Redmon2016YOLO, proposição do
detector de estágio único; Zauner2010ImplementationAB, implementação e
avaliação de funções de hash perceptual; Shorten2019, levantamento sobre
aumento de dados para aprendizado profundo. Em todas, a afirmação do
texto corresponde ao objeto declarado da obra.
