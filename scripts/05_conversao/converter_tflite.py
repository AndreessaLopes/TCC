"""
Conversão dos modelos treinados para TensorFlow Lite.

Gera as variantes FP32, FP16 e INT8 de cada modelo, registra o tamanho dos
arquivos produzidos e organiza os resultados em uma tabela comparativa.

DEPENDÊNCIAS

    pip install onnx onnx2tf onnxslim tensorflow sng4onnx onnx_graphsurgeon

SELEÇÃO DO ARQUIVO GERADO

A exportação produz um diretório <nome>_saved_model contendo arquivos com
sufixos distintos conforme a precisão: _float32, _float16 e _int8. Como
esses arquivos se acumulam entre execuções sucessivas, a seleção é feita
pelo sufixo correspondente à precisão solicitada, e não pela data de
modificação.

CONVERSÃO DO YOLOv10

O YOLOv10 utiliza a operação TopK no cabeçalho de detecção, mecanismo que
substitui a supressão não máxima. A biblioteca onnx2tf apresenta
incompatibilidade ao converter essa operação quando o parâmetro k não é
escalar, resultando no erro:

    onnx_op_name: .../TopK
    TypeError: only 0-dimensional arrays can be converted to Python scalars

Para contornar essa limitação, o script tenta automaticamente diferentes
versões de opset do ONNX quando a exportação falha. Versões anteriores do
opset representam a operação TopK de forma distinta, o que em parte dos
casos permite a conversão. O comportamento pode ser desabilitado com
--sem_fallback.

USO

    python converter_tflite.py \\
        --modelos runs/detect/runs_final/yolov8n_final_grao/weights/best.pt \\
                  runs/detect/runs_final/yolov10n_final_grao/weights/best.pt \\
        --nomes yolov8n yolov10n \\
        --data_yaml dataset_final/data.yaml \\
        --saida_dir modelos_tflite
"""

import argparse
import csv
import shutil
import time
from pathlib import Path

from ultralytics import YOLO


PRECISOES_VALIDAS = ("fp32", "fp16", "int8")

# Sufixo do arquivo .tflite gerado para cada precisão
SUFIXO_ARQUIVO = {
    "fp32": "_float32",
    "fp16": "_float16",
    "int8": "_int8",
}

# Sequência de opsets testados quando a exportação falha
OPSETS_FALLBACK = (19, 17, 16, 15, 13)


def tamanho_mb(caminho: Path) -> float:
    return caminho.stat().st_size / (1024 * 1024)


def localizar_tflite(diretorio_base: Path, precisao: str):
    """
    Localiza o arquivo .tflite correspondente à precisão solicitada,
    identificando-o pelo sufixo no nome do arquivo.
    """
    sufixo = SUFIXO_ARQUIVO[precisao]
    candidatos = [
        p for p in Path(diretorio_base).rglob("*.tflite")
        if sufixo in p.stem
    ]

    if not candidatos:
        return None

    return max(candidatos, key=lambda p: p.stat().st_mtime)


def montar_kwargs(precisao: str, opset: int, args) -> dict:
    kwargs = {
        "format": "tflite",
        "imgsz": args.imgsz,
        "half": precisao == "fp16",
        "int8": precisao == "int8",
        "opset": opset,
    }

    if precisao == "int8":
        kwargs["data"] = args.data_yaml
        kwargs["fraction"] = args.fraction_int8

    return kwargs


def tentar_exportacao(caminho_pesos: str, precisao: str, opset: int, args):
    """Executa uma tentativa de exportação com o opset informado."""
    modelo = YOLO(caminho_pesos)
    return modelo.export(**montar_kwargs(precisao, opset, args))


def converter(caminho_pesos: str, nome_modelo: str, precisao: str, args):
    """
    Converte um modelo em uma precisão específica, testando opsets
    alternativos caso a primeira tentativa falhe.
    """
    print("\n" + "=" * 68)
    print(f"CONVERTENDO {nome_modelo}  |  precisão: {precisao.upper()}")
    print("=" * 68)

    if args.sem_fallback:
        opsets = [args.opset]
    else:
        opsets = list(OPSETS_FALLBACK)
        if args.opset in opsets:
            opsets.remove(args.opset)
        opsets.insert(0, args.opset)

    inicio = time.time()
    caminho_export = None
    opset_utilizado = None
    ultimo_erro = None

    for opset in opsets:
        try:
            print(f"\n--- Tentativa com opset {opset} ---")
            caminho_export = tentar_exportacao(caminho_pesos, precisao, opset, args)
            opset_utilizado = opset
            break
        except Exception as erro:
            ultimo_erro = erro
            print(f"[opset {opset}] falhou: {erro}")
            continue

    if caminho_export is None:
        raise RuntimeError(
            f"Todas as tentativas falharam. Ultimo erro: {ultimo_erro}"
        )

    duracao = time.time() - inicio

    origem = localizar_tflite(Path(caminho_export).parent, precisao)
    if origem is None:
        origem = localizar_tflite(Path(caminho_export), precisao)
    if origem is None:
        raise FileNotFoundError(
            f"Arquivo .tflite com sufixo '{SUFIXO_ARQUIVO[precisao]}' "
            f"nao localizado em {caminho_export}"
        )

    destino = Path(args.saida_dir) / f"{nome_modelo}_{precisao}.tflite"
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origem, destino)

    tamanho = tamanho_mb(destino)
    print(f"\nArquivo de origem: {origem.name}")
    print(f"Arquivo gerado:    {destino}")
    print(f"Tamanho: {tamanho:.2f} MB  |  opset: {opset_utilizado}  |  "
          f"tempo: {duracao:.1f} s")

    return {
        "modelo": nome_modelo,
        "precisao": precisao.upper(),
        "arquivo": destino.name,
        "tamanho_mb": round(tamanho, 2),
        "opset": opset_utilizado,
        "tempo_conversao_s": round(duracao, 1),
    }


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--modelos", type=str, nargs="+", required=True)
    parser.add_argument("--nomes", type=str, nargs="+", required=True)
    parser.add_argument("--data_yaml", type=str, required=True)
    parser.add_argument("--saida_dir", type=str, default="modelos_tflite")
    parser.add_argument("--precisoes", type=str, nargs="+",
                        default=list(PRECISOES_VALIDAS),
                        choices=PRECISOES_VALIDAS)
    parser.add_argument("--imgsz", type=int, default=960)
    parser.add_argument("--opset", type=int, default=19,
                        help="Opset ONNX da primeira tentativa.")
    parser.add_argument("--sem_fallback", action="store_true",
                        help="Desabilita a tentativa com opsets alternativos.")
    parser.add_argument("--fraction_int8", type=float, default=1.0,
                        help="Fracao do conjunto usada na calibracao INT8.")
    args = parser.parse_args()

    if len(args.modelos) != len(args.nomes):
        raise ValueError("A quantidade de --modelos deve corresponder a de --nomes.")

    for caminho in args.modelos:
        if not Path(caminho).exists():
            raise FileNotFoundError(f"Pesos nao encontrados: {caminho}")

    resultados = []
    falhas = []

    for caminho_pesos, nome_modelo in zip(args.modelos, args.nomes):
        for precisao in args.precisoes:
            try:
                resultados.append(converter(caminho_pesos, nome_modelo, precisao, args))
            except Exception as erro:
                print(f"\n[FALHA] {nome_modelo} / {precisao.upper()}: {erro}")
                falhas.append((nome_modelo, precisao, str(erro)))

    if not resultados:
        print("\nNenhuma conversao foi concluida.")
        return

    csv_path = Path(args.saida_dir) / "tamanhos_modelos_tflite.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["modelo", "precisao", "arquivo", "tamanho_mb",
                        "opset", "tempo_conversao_s"],
        )
        writer.writeheader()
        writer.writerows(resultados)

    print("\n" + "=" * 68)
    print("RESUMO DAS CONVERSOES")
    print("=" * 68)
    cabecalho = (f"{'Modelo':<12} {'Precisao':<10} {'Tamanho (MB)':>14} "
                 f"{'Opset':>7} {'Tempo (s)':>12}")
    print(cabecalho)
    print("-" * len(cabecalho))
    for r in resultados:
        print(f"{r['modelo']:<12} {r['precisao']:<10} {r['tamanho_mb']:>14.2f} "
              f"{r['opset']:>7} {r['tempo_conversao_s']:>12.1f}")

    if falhas:
        print("\nConversoes que falharam:")
        for nome, precisao, _ in falhas:
            print(f"  - {nome} / {precisao.upper()}")

    print(f"\nArquivos .tflite em: {Path(args.saida_dir).resolve()}")
    print(f"Relatorio: {csv_path}")


if __name__ == "__main__":
    main()