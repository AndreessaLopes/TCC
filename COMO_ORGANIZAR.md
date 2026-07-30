# Instruções para montar o repositório

Este arquivo orienta a organização dos scripts existentes na pasta
`ProjetoCafe` para a estrutura deste repositório. Pode ser removido
após a conclusão da organização.

## 1. Estrutura a ser criada

```
projeto-cafe-tcc/
├── README.md
├── requirements.txt
├── .gitignore
├── scripts/
│   ├── 01_preprocessamento/
│   ├── 02_curadoria_phash/
│   ├── 03_reanotacao/
│   ├── 04_treinamento/
│   ├── 05_conversao/
│   └── figuras/
└── resultados/
    ├── csv/
    └── figuras/
```

## 2. Distribuição dos scripts

### scripts/01_preprocessamento/
- check_dataset.py
- check_missing_by_class.py
- verificar_pares.py
- clean_labels.py
- classe.py
- ajustar_classes.py
- labels.py
- limpar_dataset_yolo.py
- auditar_dataset_final.py

### scripts/02_curadoria_phash/
- pHash.py
- phash_train_val.py
- limpar_phash.py
- gerar_matriz_phash.py
- redistribuir_70_20_10.py

### scripts/03_reanotacao/
- analise_bbox_grao_cacho.py
- triagem_bbox_suspeitas.py
- amostra_visual_bbox.py
- organizar_dataset_limpo.py
- treinar_baseline.py
- gerar_preanotacoes_cacho.py
- visualizar_preanotacoes.py
- consolidar_dataset_final.py
- organizar_dataset_treino_final.py

### scripts/04_treinamento/
- treinar_final.py

### scripts/05_conversao/
- converter_tflite.py

### scripts/figuras/
- grafico_distribuicao_dataset.py  (usar a versão corrigida deste repositório)

## 3. Arquivos de resultado

### resultados/csv/
- relatorio_bboxes_suspeitas.csv
- duplicadas_phash.csv
- imagens_mantidas.csv
- phash_train_val.csv
- results.csv de cada treinamento (renomear: results_yolov8n.csv, results_yolov10n.csv)

### resultados/figuras/
- histograma_bboxes.png
- matriz_similaridade_phash.png
- contact_sheet_preanotacoes.jpg
- contact_sheet_v2.jpg
- results_yolov8.png
- results_yolov10.png
- BoxPR_curve_yolov8.png
- BoxPR_curve_yolov10.png
- distribuicao_dataset.png  (regerar com os valores corrigidos)

## 4. Arquivos a descartar ou revisar

- teste.py  — verificar se é rascunho
- opencv.py — verificar se é rascunho
- cafe.png  — verificar se é utilizada em alguma etapa
- augment.py — manter apenas como registro; não foi usado no fluxo final
- limpar_dataset_yolo.py — o arquivo aparece vazio; recuperar ou remover

## 5. Arquivos que não devem ser versionados

Já contemplados pelo .gitignore:
- venv/, __pycache__/, .vscode/
- dataset*/ (todas as variações)
- runs/
- *.pt, *.tflite, *.onnx
- preanotacoes_cacho*/, amostra_visual/

## 6. Comandos para inicializar o repositório

```bash
cd projeto-cafe-tcc

git init
git add .
git commit -m "Estrutura inicial do projeto"

git branch -M main
git remote add origin https://github.com/SEU_USUARIO/projeto-cafe-tcc.git
git push -u origin main
```

## 7. Verificação antes do primeiro commit

Confirme que nenhum arquivo pesado foi incluído:

```bash
git status
git ls-files | xargs du -h 2>/dev/null | sort -rh | head -20
```

Se algum arquivo grande aparecer, ajuste o .gitignore antes de commitar.
