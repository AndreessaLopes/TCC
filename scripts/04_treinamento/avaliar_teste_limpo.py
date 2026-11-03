"""Reavalia os dois modelos apenas nas imagens de teste cuja anotacao nao
passou pelo modelo auxiliar.

Motivo. A reanotacao semi-automatica incidiu sobre 836 arquivos, dos quais
91 pertencem a particao de teste. Nesses arquivos as caixas foram propostas
por um YOLOv8n auxiliar e revisadas apenas por amostragem. Como um dos
modelos avaliados e da mesma familia, parte da referencia carrega o vies
dessa familia. Este script mede quanto disso afeta o resultado publicado.

O que faz. Monta um conjunto de teste reduzido, com as 194 imagens nao
afetadas, e roda a mesma avaliacao do avaliar_teste.py sobre ele. Depois
imprime lado a lado o valor das 285 e o das 194.

Se os numeros se mantiverem, a objecao fica respondida com evidencia e
basta um paragrafo no texto. Se divergirem, o numero honesto passa a ser
o das 194 e a tabela precisa ser refeita.

Nada e apagado. O conjunto reduzido vai para dataset_teste_limpo, ao lado
do dataset_final, e pode ser removido a mao depois.

Uso, a partir da pasta ProjetoCafe:

    python avaliar_teste_limpo.py

Leva por volta de cinco minutos. Grava resultados/csv/metricas_teste_limpo.csv
"""
import csv
import os
import shutil
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
ORIGEM = os.path.join(RAIZ, "dataset_final")
DESTINO = os.path.join(RAIZ, "dataset_teste_limpo")
SUSPEITAS = os.path.join(RAIZ, "relatorio_bboxes_suspeitas.csv")

MODELOS = {
    "YOLOv8n": os.path.join(RAIZ, "runs", "detect", "runs_final",
                            "yolov8n_final_grao", "weights", "best.pt"),
    "YOLOv10n": os.path.join(RAIZ, "runs", "detect", "runs_final",
                             "yolov10n_final_grao", "weights", "best.pt"),
}

# Identicos aos do avaliar_teste.py, para que a comparacao seja legitima.
AJUSTES = dict(imgsz=960, batch=8, conf=0.001, iou=0.7, rect=False,
               split="test", workers=0, plots=False, verbose=False)


def nomes_afetados():
    afetados = set()
    with open(SUSPEITAS, encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            afetados.add(os.path.splitext(linha["arquivo"])[0])
    return afetados


def montar_conjunto():
    """Copia para DESTINO apenas as imagens de teste nao afetadas."""
    afetados = nomes_afetados()
    rotulos_origem = os.path.join(ORIGEM, "test", "labels")
    imagens_origem = os.path.join(ORIGEM, "test", "images")

    rotulos_destino = os.path.join(DESTINO, "test", "labels")
    imagens_destino = os.path.join(DESTINO, "test", "images")
    for pasta in (rotulos_destino, imagens_destino):
        if os.path.isdir(pasta):
            shutil.rmtree(pasta)
        os.makedirs(pasta)

    copiadas = excluidas = 0
    for arquivo in sorted(os.listdir(rotulos_origem)):
        base = os.path.splitext(arquivo)[0]
        if base in afetados:
            excluidas += 1
            continue
        imagem = None
        for ext in (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"):
            candidato = os.path.join(imagens_origem, base + ext)
            if os.path.exists(candidato):
                imagem = candidato
                break
        if imagem is None:
            print("  aviso: sem imagem para %s" % base)
            continue
        shutil.copy2(os.path.join(rotulos_origem, arquivo), rotulos_destino)
        shutil.copy2(imagem, imagens_destino)
        copiadas += 1

    # O data.yaml aponta o mesmo caminho para treino, validacao e teste.
    # Nada sera treinado aqui, e a biblioteca exige as tres chaves.
    caminho = os.path.join(DESTINO, "data.yaml").replace("\\", "/")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("path: %s\n" % DESTINO.replace("\\", "/"))
        f.write("train: test/images\n")
        f.write("val: test/images\n")
        f.write("test: test/images\n")
        f.write("nc: 1\n")
        f.write("names: ['grao']\n")
    return copiadas, excluidas, caminho


def instancias(pasta):
    total = 0
    for arquivo in os.listdir(pasta):
        if not arquivo.endswith(".txt"):
            continue
        with open(os.path.join(pasta, arquivo), encoding="utf-8") as f:
            total += sum(1 for linha in f if linha.strip())
    return total


def medir(dados):
    from ultralytics import YOLO
    linhas = []
    for nome, peso in MODELOS.items():
        if not os.path.exists(peso):
            sys.exit("Nao encontrei o peso de %s em %s" % (nome, peso))
        print("  medindo %s" % nome)
        r = YOLO(peso).val(data=dados, **AJUSTES)
        linhas.append({
            "modelo": nome,
            "mAP50": round(float(r.box.map50), 4),
            "mAP50_95": round(float(r.box.map), 4),
            "precisao": round(float(r.box.mp), 4),
            "revocacao": round(float(r.box.mr), 4),
        })
    return linhas


def main():
    if not os.path.exists(SUSPEITAS):
        sys.exit("Nao encontrei %s. Execute a partir da pasta ProjetoCafe."
                 % SUSPEITAS)

    print("Montando o conjunto reduzido")
    copiadas, excluidas, dados = montar_conjunto()
    n_inst = instancias(os.path.join(DESTINO, "test", "labels"))
    n_inst_tot = instancias(os.path.join(ORIGEM, "test", "labels"))
    print("  mantidas  %d imagens, %d instancias" % (copiadas, n_inst))
    print("  excluidas %d imagens, %d instancias" % (excluidas,
                                                     n_inst_tot - n_inst))
    print()

    print("Avaliando sobre as %d imagens nao afetadas" % copiadas)
    limpo = medir(dados)

    print()
    print("Avaliando sobre as %d imagens do conjunto completo" % (copiadas +
                                                                  excluidas))
    completo = medir(os.path.join(ORIGEM, "data.yaml"))

    saida = os.path.join(RAIZ, "resultados", "csv", "metricas_teste_limpo.csv")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    with open(saida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["conjunto", "n_imagens", "modelo",
                                          "mAP50", "mAP50_95", "precisao",
                                          "revocacao"])
        w.writeheader()
        for linha in completo:
            w.writerow(dict(conjunto="completo",
                            n_imagens=copiadas + excluidas, **linha))
        for linha in limpo:
            w.writerow(dict(conjunto="nao_afetado", n_imagens=copiadas,
                            **linha))

    print()
    print("=" * 66)
    print("%-10s %-10s %8s %9s %9s %10s" % ("modelo", "conjunto", "mAP50",
                                            "mAP50-95", "precisao",
                                            "revocacao"))
    print("-" * 66)
    for nome in MODELOS:
        a = [x for x in completo if x["modelo"] == nome][0]
        b = [x for x in limpo if x["modelo"] == nome][0]
        print("%-10s %-10s %8.4f %9.4f %9.4f %10.4f" % (
            nome, "285 img", a["mAP50"], a["mAP50_95"], a["precisao"],
            a["revocacao"]))
        print("%-10s %-10s %8.4f %9.4f %9.4f %10.4f" % (
            "", "%d img" % copiadas, b["mAP50"], b["mAP50_95"], b["precisao"],
            b["revocacao"]))
        print("%-10s %-10s %+8.4f %+9.4f %+9.4f %+10.4f" % (
            "", "diferenca", b["mAP50"] - a["mAP50"],
            b["mAP50_95"] - a["mAP50_95"], b["precisao"] - a["precisao"],
            b["revocacao"] - a["revocacao"]))
        print("-" * 66)
    print()
    print("Gravado em %s" % saida)
    print()
    print("Leitura. Diferenca pequena nas duas arquiteturas indica que a")
    print("anotacao assistida nao distorceu o resultado publicado. Diferenca")
    print("maior no YOLOv8n do que no YOLOv10n indica o vies de familia, e")
    print("nesse caso o numero das %d imagens passa a ser o reportavel." % copiadas)


if __name__ == "__main__":
    main()
