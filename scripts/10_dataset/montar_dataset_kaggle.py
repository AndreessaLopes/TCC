# -*- coding: utf-8 -*-
"""Monta a copia publicavel do conjunto de imagens para o Kaggle.

A copia e gerada a partir de dataset_final, sem alterar os arquivos de
origem. Tres operacoes sao aplicadas.

1. Remocao dos segmentos de metadado APP1 e APP13 de cada JPEG, que
   carregam EXIF, XMP e IPTC. A remocao ocorre no nivel dos marcadores do
   arquivo, de modo que os dados comprimidos da imagem permanecem
   identicos aos do original. O segmento APP2, que guarda o perfil de
   cor, e preservado.
2. Normalizacao dos rotulos, com quebra de linha final garantida e
   recorte das caixas que ultrapassam a borda da imagem.
3. Geracao do manifesto, com dimensao, numero de instancias e soma de
   verificacao de cada arquivo publicado.

A execucao e retomavel. O manifesto e gravado linha a linha, e cada nova
chamada ignora o que ja consta nele, de modo que o trabalho pode ser
dividido em etapas curtas pelo terceiro argumento, que limita a duracao
de cada chamada em segundos.

Uso: python3 montar_dataset_kaggle.py <origem> <destino> [segundos]
"""

import csv
import hashlib
import io
import os
import struct
import sys
import time

from PIL import Image

PARTICOES = ("train", "val", "test")

# Segmentos removidos. APP1 traz EXIF e XMP, APP13 traz o bloco IPTC.
APP_REMOVER = {0xE1, 0xED}

# Marcadores sem carga util, que ocupam apenas dois bytes.
SEM_CARGA = set(range(0xD0, 0xDA)) | {0xD8, 0x01}


def limpar_jpeg(bruto):
    """Devolve o JPEG sem os segmentos de metadado, sem recomprimir."""
    if bruto[0:2] != b"\xff\xd8":
        raise ValueError("arquivo nao comeca com o marcador de inicio de imagem")
    saida = [b"\xff\xd8"]
    i = 2
    n = len(bruto)
    while i < n:
        if bruto[i] != 0xFF:
            raise ValueError("marcador esperado na posicao %d" % i)
        j = i + 1
        while j < n and bruto[j] == 0xFF:
            j += 1
        if j >= n:
            raise ValueError("fim inesperado do arquivo")
        marcador = bruto[j]
        if marcador == 0xDA:
            # Inicio da varredura. O restante do arquivo segue intacto.
            saida.append(bruto[i:])
            break
        if marcador in SEM_CARGA:
            saida.append(bruto[i:j + 1])
            i = j + 1
            continue
        if j + 3 > n:
            raise ValueError("segmento truncado")
        tamanho = struct.unpack(">H", bruto[j + 1:j + 3])[0]
        fim = j + 1 + tamanho
        if fim > n:
            raise ValueError("segmento ultrapassa o fim do arquivo")
        if marcador not in APP_REMOVER:
            saida.append(bruto[i:fim])
        i = fim
    else:
        raise ValueError("marcador de varredura nao encontrado")
    return b"".join(saida)


def normalizar_rotulo(texto):
    """Recorta as caixas a area da imagem e padroniza o arquivo."""
    linhas = []
    recortadas = 0
    for linha in texto.splitlines():
        partes = linha.split()
        if not partes:
            continue
        if len(partes) != 5:
            raise ValueError("linha com %d campos" % len(partes))
        classe = int(partes[0])
        cx, cy, w, h = (float(p) for p in partes[1:])
        x1, y1 = cx - w / 2.0, cy - h / 2.0
        x2, y2 = cx + w / 2.0, cy + h / 2.0
        a1, b1 = max(0.0, x1), max(0.0, y1)
        a2, b2 = min(1.0, x2), min(1.0, y2)
        if (a1, b1, a2, b2) != (x1, y1, x2, y2):
            recortadas += 1
        cx, cy = (a1 + a2) / 2.0, (b1 + b2) / 2.0
        w, h = a2 - a1, b2 - b1
        linhas.append("%d %.6f %.6f %.6f %.6f" % (classe, cx, cy, w, h))
    return "\n".join(linhas) + "\n", len(linhas), recortadas


CAMPOS = ["arquivo", "particao", "largura", "altura",
          "instancias", "bytes", "sha256"]


def carregar_manifesto(caminho):
    """Le o manifesto parcial de uma execucao anterior."""
    if not os.path.exists(caminho):
        return []
    with open(caminho, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit("uso: montar_dataset_kaggle.py <origem> <destino> [segundos]")
    origem, destino = sys.argv[1], sys.argv[2]
    limite = float(sys.argv[3]) if len(sys.argv) == 4 else None
    inicio = time.time()

    caminho_man = os.path.join(destino, "manifesto.csv")
    registros = carregar_manifesto(caminho_man)
    feitos = {r["arquivo"] for r in registros}
    if (os.path.exists(destino) and os.listdir(destino)
            and not os.path.exists(caminho_man)):
        sys.exit("FALHOU: o destino %s ja existe e nao esta vazio" % destino)
    os.makedirs(destino, exist_ok=True)
    novo_manifesto = not os.path.exists(caminho_man)
    saida_man = open(caminho_man, "a", encoding="utf-8", newline="")
    escritor = csv.DictWriter(saida_man, fieldnames=CAMPOS)
    if novo_manifesto:
        escritor.writeheader()
        saida_man.flush()

    total_recortadas = 0
    total_limpas = 0
    esgotou = False
    for particao in PARTICOES:
        if esgotou:
            break
        dir_img = os.path.join(origem, particao, "images")
        dir_rot = os.path.join(origem, particao, "labels")
        if not os.path.isdir(dir_img):
            sys.exit("FALHOU: nao encontrei %s" % dir_img)
        os.makedirs(os.path.join(destino, particao, "images"), exist_ok=True)
        os.makedirs(os.path.join(destino, particao, "labels"), exist_ok=True)

        nomes = sorted(n for n in os.listdir(dir_img) if n.lower().endswith(".jpg"))
        for k, nome in enumerate(nomes, 1):
            if "%s/images/%s" % (particao, nome) in feitos:
                continue
            if limite is not None and time.time() - inicio > limite:
                esgotou = True
                break
            base = nome[:-4]
            ent_img = os.path.join(dir_img, nome)
            ent_rot = os.path.join(dir_rot, base + ".txt")
            if not os.path.exists(ent_rot):
                sys.exit("FALHOU: %s sem rotulo correspondente" % ent_img)

            with open(ent_img, "rb") as f:
                bruto = f.read()
            try:
                limpo = limpar_jpeg(bruto)
            except ValueError as erro:
                sys.exit("FALHOU em %s: %s" % (ent_img, erro))
            if len(limpo) != len(bruto):
                total_limpas += 1
            sai_img = os.path.join(destino, particao, "images", nome)
            with open(sai_img, "wb") as f:
                f.write(limpo)

            with open(ent_rot, "r", encoding="utf-8") as f:
                texto = f.read()
            try:
                novo, n_inst, recortadas = normalizar_rotulo(texto)
            except ValueError as erro:
                sys.exit("FALHOU em %s: %s" % (ent_rot, erro))
            total_recortadas += recortadas
            sai_rot = os.path.join(destino, particao, "labels", base + ".txt")
            with open(sai_rot, "w", encoding="utf-8", newline="\n") as f:
                f.write(novo)

            # Dimensao e soma de verificacao saem dos bytes ja em memoria,
            # o que evita reler do disco o arquivo recem-gravado.
            with Image.open(io.BytesIO(limpo)) as im:
                largura, altura = im.size
            linha = {
                "arquivo": "%s/images/%s" % (particao, nome),
                "particao": particao,
                "largura": largura,
                "altura": altura,
                "instancias": n_inst,
                "bytes": len(limpo),
                "sha256": hashlib.sha256(limpo).hexdigest(),
            }
            registros.append(linha)
            escritor.writerow(linha)
            saida_man.flush()
            if k % 200 == 0:
                print("  %s: %d de %d" % (particao, k, len(nomes)), flush=True)
        if not esgotou:
            print("%s concluida: %d imagens" % (particao, len(nomes)), flush=True)

    saida_man.close()
    esperado = sum(len([n for n in os.listdir(os.path.join(origem, p, "images"))
                        if n.lower().endswith(".jpg")]) for p in PARTICOES)
    print("")
    print("imagens publicadas: %d de %d" % (len(registros), esperado))
    print("imagens com metadado removido nesta chamada: %d" % total_limpas)
    print("caixas recortadas nesta chamada: %d" % total_recortadas)
    print("instancias: %d" % sum(int(r["instancias"]) for r in registros))
    for particao in PARTICOES:
        sub = [r for r in registros if r["particao"] == particao]
        print("  %-5s %4d imagens, %6d instancias"
              % (particao, len(sub), sum(int(r["instancias"]) for r in sub)))
    if len(registros) < esperado:
        print("")
        print("INCOMPLETO. Rode o mesmo comando de novo para continuar.")
    else:
        print("")
        print("COMPLETO. Manifesto em %s" % caminho_man)


if __name__ == "__main__":
    main()
