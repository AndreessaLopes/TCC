# Conferência das citações

Para cada frase do `monografia/artigo.tex` ligada a uma citação, confirmar
que a obra citada sustenta o que a frase afirma. Quando a frase traz mais
de uma citação, cada uma precisa sustentar a afirmação.

## Inventário

`scripts/10_conferencia/extrair_citacoes.py` extrai as frases com citação
para `frases.json`, com identificadores f001 em diante. Estado atual: 70
frases, 81 pares de frase e obra, 26 obras.

## Classificação

- **Confirmada**: a obra diz o que a frase afirma.
- **Parcial**: sustenta parte da frase, ou há diferença de número, de
  contexto ou de nuance.
- **Não sustenta**: a obra não diz o que a frase afirma.
- **Sem acesso**: a obra não pôde ser consultada.

## Ordem de conferência

Primeiro as 22 frases que trazem afirmação numérica, por serem as que
um leitor confere com facilidade e onde o erro se esconde. Depois as
demais.

## Regra

O texto não é alterado durante a conferência. Os achados vão para
`correcoes_sugeridas.md` e a autora decide. Obras que não puderem ser
consultadas ficam registradas como tal, sem conferência de memória.
