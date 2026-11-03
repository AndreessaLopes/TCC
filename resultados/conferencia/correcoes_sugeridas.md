# Correções sugeridas

## f001 — participação do Brasil na produção mundial

**Frase (introdução).** "O Brasil ocupa posição de destaque na produção e
exportação mundial de café, sendo responsável por aproximadamente 37% da
produção global na safra 2025."

**Obra citada.** CONAB2025, primeira estimativa para a safra 2025.

**Resultado.** Não sustenta. A publicação citada não informa a
participação do Brasil na produção mundial. Ela traz a produção
brasileira estimada, de 51,8 milhões de sacas, e a produção mundial
estimada pelo USDA para 2024/25, de 174,9 milhões de sacas, sem
relacioná-las. A razão entre as duas é de aproximadamente 30%, e não 37%.

**Resolvida em 2026-11-03.** A frase passa a declarar a produção
estimada, de 51,8 milhões de sacas, e os aproximadamente 30% que ela
representa na produção mundial reportada na mesma publicação.

## f002 — participação de Minas Gerais na produção nacional

**Frase (introdução).** "Minas Gerais concentra cerca de 52% da produção
nacional."

**Obra citada.** CONAB2025, primeira estimativa para a safra 2025.

**Resultado.** Não sustenta. A publicação citada estima 24,8 milhões de
sacas em Minas Gerais e 51,8 milhões no país, o que corresponde a 47,9%.
O 3º Levantamento, de setembro de 2025, registra 25,3 de 55,2 milhões,
ou 45,8%.

**Resolvida em 2026-11-03.** A frase passa a dizer cerca de 48%, valor
que decorre da própria publicação citada.

## f003 — receita do ano-cafeeiro

**Frase (introdução).** "A cafeicultura movimentou aproximadamente
R$ 125,7 bilhões no ano-cafeeiro de 2025 e gera milhões de empregos
diretos e indiretos."

**Obras citadas.** Cecafe2025 e MAPA2023.

**Resultado.** Pendente de conferência.

## f009 — execução local citando trabalho em nuvem

**Frase (introdução).** "Essa estratégia reduz a dependência de conexão
com a internet, diminui a latência e permite que aplicações funcionem
mesmo em regiões com infraestrutura limitada."

**Obra citada.** Thai2024Coffee.

**Resultado.** Parcial. A frase afirma benefícios da execução local, e a
obra citada propõe justamente o contrário, um sistema integrado a solução
em nuvem com tempo de resposta entre 1 e 3 segundos. A obra serve de
contraexemplo que motiva a execução local, que é como o Quadro~1 a
apresenta, mas não sustenta a afirmação da frase.

**Sugestão.** Reformular a frase para "Essa estratégia reduz a dependência
de conexão com a internet, ao contrário de soluções que processam a
inferência em nuvem e registram tempo de resposta entre 1 e 3 segundos",
mantendo a citação, ou citar obra que demonstre os benefícios da execução
local.

## f052 — processamento em nuvem afirmado além do resumo

**Frase (Quadro 1).** "Tempo de resposta entre 1 e 3 segundos; depende de
conectividade e processamento em nuvem."

**Obra citada.** Thai2024Coffee.

**Resultado.** Parcial. O tempo de 1 a 3 segundos confere. A dependência
de conectividade e de processamento em nuvem é inferência razoável a
partir da arquitetura descrita, mas o resumo afirma apenas integração com
solução em nuvem.

**Sugestão.** Trocar por "integra solução em nuvem", que é o que a obra
declara.

## Verificação pendente de acesso institucional

As obras abaixo tiveram a parte qualitativa confirmada, mas os valores
numéricos atribuídos a elas no texto não puderam ser conferidos deste
ambiente, por estarem no texto completo de periódico com acesso
restrito. Cada uma leva menos de um minuto pelo portal de periódicos.

| Obra | Valor a conferir no texto | Onde aparece |
|---|---|---|
| Gope2024Comparative | precisão 0,977; revocação 0,990; F1 0,983; mAP 0,995 do custom-YOLOv8n | f037 e Quadro 1 |
| Kazama2024Monitoring | mAP@0,95 de 45,90% | Quadro 1 |

Observação sobre a segunda: a notação "mAP@0,95" não é usual. Se o valor
for o mAP calculado sobre limiares de 0,50 a 0,95, a notação correta é
mAP@0,50--0,95, como no restante do trabalho.

## f017 — resultado atribuído a Chu e outros

**Frase (fundamentação).** "Chu e outros demonstraram que o comportamento
dos delegates varia entre diferentes SoC, indicando a necessidade de
avaliação experimental em dispositivos reais."

**Obra citada.** Chu2023nnPerf.

**Resultado.** Não sustenta. A obra propõe o nnPerf, ferramenta de
profiling de latência em nível de operador e de núcleo sobre o TFLite,
avaliada em quatro plataformas móveis em CPU e em GPU. O resumo não
apresenta variação de comportamento de delegates entre SoC como
resultado.

**Resolvida em 2026-11-03.** A frase passa a descrever o que a obra
apresenta e mantém a conclusão sobre medição em dispositivos reais, que
decorre do próprio escopo da ferramenta.

## Verificação pendente, segunda leva

| Obra | O que conferir | Onde aparece |
|---|---|---|
| Zhao2022A | se o levantamento aponta o TFLite para execução local sob restrição de conectividade, e se relaciona quantização, poda e aceleradores a consumo energético | f016, f023 |
| Hirsch2025Exploring | número de aparelhos do testbed, métricas medidas e a afirmação de que modelos com latência semelhante podem ter consumo distinto conforme delegate e aparelho | f020, f022, f042, f054 |

Ambas têm texto completo em periódico que este ambiente não alcança,
Proceedings of the IEEE e Sensors. Pelo Portal de Periódicos o acesso é
direto.
