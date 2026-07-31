"""
Validação dos modelos convertidos para TensorFlow Lite.

Executa cada variante gerada na etapa de conversão sobre o conjunto de
teste e reporta as métricas de detecção, permitindo quantificar o impacto
das estratégias de quantização sobre a qualidade das predições.

FINALIDADE

A conversão para TFLite e, em especial, a quantização INT8 podem alterar
as predições em relação ao modelo original em PyTorch. Esta verificação
corresponde à etapa de teste de integridade funcional prevista na
metodologia, comparando os resultados produzidos pelas versões originais
e convertidas.

OBSERVAÇÕES

- A inferência de modelos TFLite ocorre em CPU neste ambiente. O tempo
  reportado não corresponde ao desempenho esperado em dispositivos
  móveis, medido posteriormente na aplicação Android.
- A validação de cada variante processa as 285 imagens do conjunto de
  teste e pode levar vários minutos, especialmente nas versões INT8.

USO

    # validar todas as variantes encontradas no diretório
    python validar_tflite.py \\
        --modelos_dir modelos_tflite \\
        --data_yaml dataset_final/data.yaml

    # validar apenas variantes específicas
    python validar_tflite.py \\
        --modelos_dir modelos_tflite \\
        --data_yaml dataset_final/data.yaml \\
        --arquivos yolov8n_fp32.tflite yolov8n_int8.tflite
"""

import argparse
import csv
import time
from pathlib import Path

from ultralytics import YOLO


# Métricas dos modelos originais em PyTorch, para comparação
REFERENCIA_PYTORCH = {
    "yolov8n": {"map50": 0.650, "map50_95": 0.360, "precisao": 0.619, "revocacao": 0.626},
    "yolov10n": {"map50": 0.644, "map50_95": 0.375, "precisao": 0.633, "revocacao": 0.625},
}


def identificar_modelo(nome_arquivo: str):
    """Extrai o nome do modelo a partir do nome do arquivo."""
    for chave in REFERENCIA_PYTORCH:
        if nome_arquivo.startswith(chave):
            return chave
    return None


def identificar_precisao(nome_arquivo: str):
    for precisao in ("fp32", "fp16", "int8"):
        if precisao in nome_arquivo:
            return precisao.upper()
    return "?"


def validar(caminho_tflite: Path, args):
    nome = caminho_tflite.stem
    modelo_base = identificar_modelo(nome)
    precisao = identificar_precisao(nome)

    print("\n" + "=" * 68)
    print(f"VALIDANDO {caminho_tflite.name}")
    print("=" * 68)

    modelo = YOLO(str(caminho_tflite))
    inicio = time.time()

    metricas = modelo.val(
        data=args.data_yaml,
        split="test",
        imgsz=args.imgsz,
        batch=1,
        workers=0,
        verbose=False,
    )

    duracao = time.time() - inicio

    resultado = {
        "arquivo": caminho_tflite.name,
        "modelo": modelo_base or "?",
        "precisao": precisao,
        "map50": round(float(metricas.box.map50), 4),
        "map50_95": round(float(metricas.box.map), 4),
        "precisao_deteccao": round(float(metricas.box.mp), 4),
        "revocacao": round(float(metricas.box.mr), 4),
        "tempo_validacao_s": round(duracao, 1),
    }

    # Comparação com o modelo original, quando disponível
    if modelo_base:
        ref = REFERENCIA_PYTORCH[modelo_base]
        resultado["delta_map50"] = round(resultado["map50"] - ref["map50"], 4)
        resultado["delta_map50_95"] = round(resultado["map50_95"] - ref["map50_95"], 4)
    else:
        resultado["delta_map50"] = None
        resultado["delta_map50_95"] = None

    print(f"\nmAP@0,50:      {resultado['map50']:.4f}")
    print(f"mAP@0,50-0,95: {resultado['map50_95']:.4f}")
    print(f"Precisão:      {resultado['precisao_deteccao']:.4f}")
    print(f"Revocação:     {resultado['revocacao']:.4f}")

    if modelo_base:
        print(f"\nVariação em relação ao modelo original (PyTorch):")
        print(f"  mAP@0,50:      {resultado['delta_map50']:+.4f}")
        print(f"  mAP@0,50-0,95: {resultado['delta_map50_95']:+.4f}")

    print(f"\nTempo de validação: {duracao:.1f} s")

    return resultado


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--modelos_dir", type=str, default="modelos_tflite")
    parser.add_argument("--data_yaml", type=str, required=True)
    parser.add_argument("--arquivos", type=str, nargs="+", default=None,
                        help="Nomes específicos a validar. Sem este argumento, "
                             "valida todos os .tflite do diretório.")
    parser.add_argument("--imgsz", type=int, default=960)
    parser.add_argument("--saida_csv", type=str, default=None,
                        help="Caminho do CSV de saída. Padrão: "
                             "<modelos_dir>/validacao_tflite.csv")
    args = parser.parse_args()

    modelos_dir = Path(args.modelos_dir)
    if not modelos_dir.exists():
        raise FileNotFoundError(f"Diretório não encontrado: {modelos_dir}")

    if args.arquivos:
        caminhos = [modelos_dir / nome for nome in args.arquivos]
        faltando = [c for c in caminhos if not c.exists()]
        if faltando:
            raise FileNotFoundError(
                "Arquivos não encontrados: " + ", ".join(str(c) for c in faltando)
            )
    else:
        caminhos = sorted(modelos_dir.glob("*.tflite"))

    if not caminhos:
        raise FileNotFoundError(f"Nenhum arquivo .tflite em {modelos_dir}")

    print(f"Variantes a validar: {len(caminhos)}")
    for c in caminhos:
        print(f"  - {c.name}")

    resultados = []
    falhas = []

    for caminho in caminhos:
        try:
            resultados.append(validar(caminho, args))
        except Exception as erro:
            print(f"\n[FALHA] {caminho.name}: {erro}")
            falhas.append((caminho.name, str(erro)))

    if not resultados:
        print("\nNenhuma validação foi concluída.")
        return

    saida_csv = Path(args.saida_csv) if args.saida_csv else modelos_dir / "validacao_tflite.csv"
    with open(saida_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(resultados[0].keys()))
        writer.writeheader()
        writer.writerows(resultados)

    print("\n" + "=" * 78)
    print("RESUMO DA VALIDAÇÃO NO CONJUNTO DE TESTE")
    print("=" * 78)
    cabecalho = (f"{'Modelo':<10} {'Prec.':<7} {'mAP@0,50':>10} {'Δ':>9} "
                 f"{'mAP@50-95':>11} {'Precisão':>10} {'Revocação':>11}")
    print(cabecalho)
    print("-" * len(cabecalho))

    for r in resultados:
        delta = f"{r['delta_map50']:+.4f}" if r["delta_map50"] is not None else "—"
        print(f"{r['modelo']:<10} {r['precisao']:<7} {r['map50']:>10.4f} {delta:>9} "
              f"{r['map50_95']:>11.4f} {r['precisao_deteccao']:>10.4f} "
              f"{r['revocacao']:>11.4f}")

    print("\nReferência (modelos originais em PyTorch):")
    for nome, ref in REFERENCIA_PYTORCH.items():
        print(f"  {nome:<10} mAP@0,50 = {ref['map50']:.4f}  |  "
              f"mAP@0,50-0,95 = {ref['map50_95']:.4f}")

    if falhas:
        print("\nValidações que falharam:")
        for nome, erro in falhas:
            print(f"  - {nome}: {erro}")

    print(f"\nResultados salvos em: {saida_csv}")


if __name__ == "__main__":
    main()