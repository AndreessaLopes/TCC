"""Corrige entradas do arquivo de referencias.

Duas entradas traziam periodico e ano incorretos. A de Tan e outros, "A
Survey on Deep Transfer Learning", constava como artigo de 2023 na
Artificial Intelligence Review; o trabalho e de 2018 e esta disponivel
como preprint no arXiv, conferido na propria pagina do repositorio, que
nao registra publicacao em periodico. A de Mumuni e Mumuni constava na
mesma Artificial Intelligence Review; o artigo saiu na Array, volume 16,
de 2022, conferido no registro do DOAJ.

Quatro entradas tinham endereco sem data de acesso, exigida pela norma
para fonte consultada em linha.

Uso: python3 -I corrigir_referencias.py <referencias.bib> <artigo.tex>
"""
import io
import sys

bib, tex = sys.argv[1], sys.argv[2]
t = io.open(bib, encoding="utf-8").read()
feito = []


def trocar(rotulo, antigo, novo, alvo=None):
    global t
    if t.count(antigo) != 1:
        sys.exit("FALHOU em %s: %d ocorrencias\n  %r"
                 % (rotulo, t.count(antigo), antigo[:80]))
    t = t.replace(antigo, novo)
    feito.append(rotulo)


# ----------------------------------------------- Tan e outros
trocar(
    "Tan e outros, ano e veiculo",
    """@article{Tan2023TransferLearning,
  author  = {Tan, Chuanqi and Sun, Fuchun and Kong, Tao and others},
  title   = {A Survey on Deep Transfer Learning},
  journal = {Artificial Intelligence Review},
  year    = {2023},
  volume  = {56},
  pages   = {1--39}
}""",
    """@misc{Tan2018TransferLearning,
  author        = {Tan, Chuanqi and Sun, Fuchun and Kong, Tao and Zhang,
                   Wenchang and Yang, Chao and Liu, Chunfang},
  title         = {A Survey on Deep Transfer Learning},
  year          = {2018},
  eprint        = {1808.01974},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG},
  url           = {https://arxiv.org/abs/1808.01974},
  urldate       = {2026-10-26}
}""",
)

# ----------------------------------------------- Mumuni e Mumuni
trocar(
    "Mumuni e Mumuni, veiculo e localizacao",
    """@article{Mumuni2022DataAugmentation,
  author  = {Mumuni, Alhassan and Mumuni, Fuseini},
  title   = {Data Augmentation: A Comprehensive Survey of Modern Approaches},
  journal = {Artificial Intelligence Review},
  year    = {2022}
}""",
    """@article{Mumuni2022DataAugmentation,
  author  = {Mumuni, Alhassan and Mumuni, Fuseini},
  title   = {Data Augmentation: A Comprehensive Survey of Modern Approaches},
  journal = {Array},
  year    = {2022},
  volume  = {16},
  pages   = {100258},
  url     = {https://doaj.org/article/06579df9a3974ed5b06ef40a946cf282},
  urldate = {2026-10-26}
}""",
)

# ----------------------------------------------- datas de acesso
for rotulo, ancora in (
    ("Zauner", "  url    = {https://api.semanticscholar.org/CorpusID:17075066}"),
    ("MakeSense", "  url    = {https://www.makesense.ai}"),
    ("Flutter", "  url    = {https://flutter.dev}"),
):
    trocar("data de acesso, %s" % rotulo, ancora + "\n",
           ancora + ",\n  urldate = {2026-10-26}\n")

trocar(
    "data de acesso, Bochkovskiy",
    "  url           = {https://arxiv.org/abs/2004.10934}\n",
    "  url           = {https://arxiv.org/abs/2004.10934},\n"
    "  urldate       = {2026-10-26}\n",
)

io.open(bib, "w", encoding="utf-8").write(t)

# ----------------------------------------------- citacoes no texto
a = io.open(tex, encoding="utf-8").read()
if a.count("Tan2023TransferLearning") != 2:
    sys.exit("FALHOU: %d citacoes de Tan2023TransferLearning, esperava 2"
             % a.count("Tan2023TransferLearning"))
io.open(tex, "w", encoding="utf-8").write(
    a.replace("Tan2023TransferLearning", "Tan2018TransferLearning"))
feito.append("citacoes de Tan renomeadas no texto")

for f in feito:
    print("ok  %s" % f)
