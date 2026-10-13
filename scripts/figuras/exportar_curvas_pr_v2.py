"""Exporta os dados das curvas de precisao e revocacao para CSV.

As Figuras 16 e 17 da monografia vinham da saida crua do Ultralytics, com
eixos em ingles e ponto decimal. O Ultralytics desenha o grafico mas nao
grava os pontos, de modo que refazer a figura exige executar a validacao
novamente e extrair as series do objeto de metricas.

Este script roda a validacao dos dois modelos no subconjunto de teste e
grava, para cada um, um CSV com a curva. Nao altera nenhum arquivo do
treinamento nem gera figuras.

A raiz do projeto e localizada sozinha: o script procura, a partir do
diretorio atual e subindo, e tambem nos locais usuais, a pasta que
contenha dataset_final/data.yaml e runs/detect. Pode-se informa-la
explicitamente com --raiz.

Com o venv ativo:

    python exportar_curvas_pr.py
    python exportar_curvas_pr.py --raiz C:\\Users\\andressa\\Downloads\\ProjetoCafe

Saida: curva_pr_yolov8n.csv e curva_pr_yolov10n.csv, gravados na raiz.
"""
import argparse
import csv
import sys
from pathlib import Path

IMGSZ = 960

MODELOS = [
    ("yolov8n", "runs/detect/runs_final/yolov8n_final_grao/weights/best.pt"),
    ("yolov10n", "runs/detect/runs_final/yolov10n_final_grao/weights/best.pt"),
]


def parece_raiz(p):
    return (p / "dataset_final" / "data.yaml").exists() and \
           (p / "runs" / "detect").is_dir()


def achar_raiz(informada):
    if informada:
        p = Path(informada).expanduser().resolve()
        if not parece_raiz(p):
            sys.exit("Em %s nao ha dataset_final/data.yaml e runs/detect." % p)
        return p

    candidatos = [Path.cwd(), *Path.cwd().parents]
    candidatos += [Path.home() / "Downloads" / "ProjetoCafe",
                   Path.home() / "Documents" / "ProjetoCafe"]
    for p in candidatos:
        try:
            if parece_raiz(p):
                return p.resolve()
        except OSError:
            continue
    sys.exit(
        "Nao encontrei a raiz do projeto a partir de %s.\n"
        "Informe com --raiz, por exemplo:\n"
        "    python exportar_curvas_pr.py --raiz "
        "C:\\\\Users\\\\andressa\\\\Downloads\\\\ProjetoCafe" % Path.cwd()
    )


def serie(objeto, *nomes):
    """Devolve o primeiro atributo existente, achatado para uma classe."""
    for nome in nomes:
        v = getattr(objeto, nome, None)
        if v is None:
            continue
        v = v.tolist() if hasattr(v, "tolist") else list(v)
        # As curvas vem como (n_classes, n_pontos); aqui ha classe unica.
        if v and isinstance(v[0], list):
            v = v[0]
        return v
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", help="pasta raiz do ProjetoCafe")
    args = ap.parse_args()

    raiz = achar_raiz(args.raiz)
    print("raiz do projeto: %s\n" % raiz)

    from ultralytics import YOLO

    dados = str(raiz / "dataset_final" / "data.yaml")

    for nome, relativo in MODELOS:
        pesos = raiz / relativo
        if not pesos.exists():
            sys.exit("Pesos nao encontrados: %s" % pesos)

        print("validando %s ..." % nome)
        metricas = YOLO(str(pesos)).val(data=dados, split="test", imgsz=IMGSZ,
                                        plots=False, verbose=False)
        caixa = metricas.box

        limiar = serie(caixa, "px")
        precisao = serie(caixa, "p_curve", "prec_values")
        revocacao = serie(caixa, "r_curve")
        f1 = serie(caixa, "f1_curve")

        if limiar is None or precisao is None:
            sys.exit("Esta versao do Ultralytics nao expos as curvas. "
                     "Atributos disponiveis: %s"
                     % [a for a in dir(caixa) if "curve" in a or a == "px"])

        saida = raiz / ("curva_pr_%s.csv" % nome)
        with open(saida, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["limiar_confianca", "precisao", "revocacao", "f1"])
            for i in range(len(limiar)):
                w.writerow([
                    limiar[i],
                    precisao[i] if i < len(precisao) else "",
                    revocacao[i] if revocacao and i < len(revocacao) else "",
                    f1[i] if f1 and i < len(f1) else "",
                ])

        print("  gravado %s  (%d pontos)" % (saida, len(limiar)))
        print("  mAP@0,50 = %.4f   mAP@0,50-0,95 = %.4f"
              % (caixa.map50, caixa.map))


if __name__ == "__main__":
    main()
