"""
Consolidação final: mescla as anotações geradas/revisadas (preanotacoes_cacho_v2)
de volta no dataset original (dataset_24_06), substituindo apenas os arquivos
que haviam sido sinalizados como cacho/erro. As anotações "limpas" originais
(grão individual) permanecem intocadas.

Antes de sobrescrever, faz um backup dos arquivos originais sinalizados em
uma pasta separada, por segurança (caso precise reverter ou comparar depois).

Uso:
    python consolidar_dataset_final.py \
        --dataset_labels_dir dataset_24_06/labels \
        --preanotacoes_dir preanotacoes_cacho_v2 \
        --backup_dir dataset_24_06/labels_backup_pre_correcao
"""

import argparse
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset_labels_dir", type=str, required=True,
                        help="Pasta de labels do dataset original (dataset_24_06/labels).")
    parser.add_argument("--preanotacoes_dir", type=str, required=True,
                        help="Pasta gerada na Etapa 3 (contém labels/ com as versões corrigidas).")
    parser.add_argument("--backup_dir", type=str, default="labels_backup_pre_correcao",
                        help="Pasta onde os arquivos originais (antes da correção) serão salvos.")
    args = parser.parse_args()

    dataset_labels_dir = Path(args.dataset_labels_dir)
    preanotacoes_labels_dir = Path(args.preanotacoes_dir) / "labels"
    backup_dir = Path(args.backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)

    novos_arquivos = sorted(preanotacoes_labels_dir.glob("*.txt"))
    if not novos_arquivos:
        raise FileNotFoundError(f"Nenhum .txt encontrado em {preanotacoes_labels_dir}")

    substituidos = 0
    nao_encontrados = 0

    for novo_txt in novos_arquivos:
        candidatos = list(dataset_labels_dir.rglob(novo_txt.name))
        if not candidatos:
            print(f"  [aviso] {novo_txt.name} não existe no dataset original, pulando.")
            nao_encontrados += 1
            continue

        original_txt = candidatos[0]

        # Backup do arquivo original antes de sobrescrever
        shutil.copy2(original_txt, backup_dir / original_txt.name)

        # Sobrescreve com a versão corrigida
        shutil.copy2(novo_txt, original_txt)
        substituidos += 1

    print("\n=== Resumo da consolidação ===")
    print(f"Arquivos substituídos (versão corrigida aplicada): {substituidos}")
    print(f"Arquivos não encontrados no dataset original:       {nao_encontrados}")
    print(f"Backup dos originais salvo em: {backup_dir.resolve()}")
    print(f"\nDataset {dataset_labels_dir.resolve()} agora contém a versão consolidada.")
    print("Recomenda-se rodar novamente analise_bbox_grao_cacho.py para confirmar "
          "que a distribuição de tamanho das bounding boxes melhorou.")


if __name__ == "__main__":
    main()