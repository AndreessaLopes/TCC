# -*- coding: utf-8 -*-
"""Acrescenta a verificacao de sensibilidade da anotacao assistida."""
import re
import sys

ARQ = sys.argv[1]
t = open(ARQ, encoding="utf-8").read()


def trocar(rotulo, antigo, novo):
    global t
    padrao = r"\s+".join(re.escape(p) for p in antigo.split())
    n = len(re.findall(padrao, t))
    if n != 1:
        sys.exit("FALHOU em %s: %d ocorrencias" % (rotulo, n))
    t = re.sub(padrao, lambda _: novo, t, count=1)
    print("ok  %s" % rotulo)


trocar(
    "sensibilidade da anotacao assistida",
    "O modelo auxiliar foi treinado exclusivamente com arquivos da partição "
    "de treinamento, de modo que não houve exposição prévia às imagens de "
    "teste, porém essa separação não elimina o viés descrito.",

    "O modelo auxiliar foi treinado exclusivamente com arquivos da partição "
    "de treinamento, de modo que não houve exposição prévia às imagens de "
    "teste, porém essa separação não elimina o viés descrito. O efeito sobre "
    "os indicadores foi verificado por reavaliação das duas arquiteturas "
    "apenas nas 194 imagens não afetadas, apresentada na "
    "Tabela~\\ref{tab:anotacao_assistida}. O \\ac{mAP}@0,50 não diminui no "
    "subconjunto não afetado, e sim aumenta em 0,0102 no YOLOv8n e em 0,0022 "
    "no YOLOv10n, de modo que o indicador principal não decorre da anotação "
    "assistida. O \\ac{mAP}@0,50:0,95 recua nas duas arquiteturas, 0,0177 no "
    "YOLOv8n e 0,0221 no YOLOv10n, recuo compatível com caixas mais próximas "
    "da convenção do detector nas imagens afetadas e de magnitude semelhante "
    "nos dois modelos, de modo que esse indicador, no conjunto completo, "
    "encontra-se possivelmente otimista, sem que isso altere a comparação "
    "entre as arquiteturas. Quanto ao viés de família, a retirada das "
    "imagens anotadas pelo modelo auxiliar deveria desfavorecer o YOLOv8n, e "
    "o observado é o contrário. A diferença no \\ac{mAP}@0,50 amplia-se de "
    "0,0036 para 0,0116 em favor do YOLOv8n, e a vantagem do YOLOv10n no "
    "\\ac{mAP}@0,50:0,95 reduz-se de 0,0126 para 0,0082. A verificação "
    "confronta conjuntos de imagens distintos, uma vez que os arquivos "
    "afetados foram sinalizados por apresentarem anotação agrupada e "
    "correspondem a cenas mais densas, de modo que parte da variação "
    "observada decorre dessa diferença de composição e não da forma de "
    "anotação.\n\n"
    "\\input{tabelas/anotacao_assistida.tex}\n",
)

open(ARQ, "w", encoding="utf-8").write(t)
print("arquivo gravado")
