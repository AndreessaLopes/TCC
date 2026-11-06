# Envio do conjunto de imagens ao Kaggle

A pasta `C:\Users\andressa\Downloads\ProjetoCafe\kaggle_cafe_frutos` já
está pronta, com as imagens sem metadado, os rótulos normalizados, o
manifesto, o `data.yaml`, a licença, o cartão do dataset e o
`dataset-metadata.json`. Faltam cinco passos, todos na sua máquina,
porque o envio exige a sua credencial.

## 1. Instalar a ferramenta

```
pip install kaggle
```

## 2. Gerar o token

Entre em <https://www.kaggle.com/settings>, seção **API**, e clique em
**Create New Token**. O navegador baixa um `kaggle.json`. Mova esse
arquivo para

```
C:\Users\andressa\.kaggle\kaggle.json
```

Crie a pasta `.kaggle` se ela não existir. O arquivo guarda a sua
credencial, então não entre com ele em nenhum repositório.

## 3. Preencher o usuário

Abra `kaggle_cafe_frutos\dataset-metadata.json` e troque
`SEU_USUARIO_KAGGLE` pelo seu nome de usuário do Kaggle, que é o que
aparece no endereço do seu perfil. O campo fica assim.

```
"id": "andressalopes/coffee-fruit-detection-yolo",
```

## 4. Enviar

```
cd C:\Users\andressa\Downloads\ProjetoCafe
kaggle datasets create -p kaggle_cafe_frutos --dir-mode zip
```

O `--dir-mode zip` é obrigatório aqui. Sem ele a ferramenta ignora as
subpastas e envia apenas os arquivos soltos da raiz. Com ele, cada
subpasta vira um arquivo compactado antes do envio, de modo que sobem
`train.zip`, `val.zip` e `test.zip` mais os quatro arquivos de raiz.

São 11 GB. Conte com várias horas e deixe o computador ligado. Se a
conexão cair, repita o mesmo comando.

O conjunto nasce privado. Confira a página do dataset antes de abrir ao
público, em especial se o Kaggle descompactou os três arquivos e mostra
as pastas na árvore. Se tiver ficado como arquivo compactado, o conjunto
continua utilizável, e me avise que ajustamos a forma do envio.

## 5. Publicar

Com a página conferida, use o botão de tornar público na própria
interface do Kaggle.

## Versões posteriores

Para enviar uma correção depois, sem criar outro dataset.

```
kaggle datasets version -p kaggle_cafe_frutos -m "descricao da mudanca" --dir-mode zip
```

## Depois de publicar

Três coisas ficam pendentes e dependem do endereço final do dataset.

1. A Subseção de disponibilidade dos dados da monografia afirma hoje que
   a divulgação das imagens depende de autorização ainda não obtida. A
   frase precisa ser reescrita, e uma entrada nova de referência passa a
   apontar o conjunto.
2. O registro do Zenodo ganha um trabalho relacionado, com a relação
   `Is supplement to` apontando o dataset do Kaggle.
3. O `README.md` do repositório público ganha a linha do conjunto de
   imagens, que hoje consta da seção sobre o que o repositório não
   contém.

## Observação sobre arquivamento

O Kaggle não emite DOI nem garante permanência. Se o conjunto for citado
na monografia e no artigo futuro, vale depositar a mesma pasta também no
Zenodo, que aceita 50 GB por registro e devolve um DOI de conceito. O
Kaggle permanece como vitrine, e a citação aponta para o DOI.
