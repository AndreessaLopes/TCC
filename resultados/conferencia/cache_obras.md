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
