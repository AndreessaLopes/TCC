import os
from collections import defaultdict

base = "dataset_final/labels"

stats = defaultdict(int)
empty = 0
invalid = 0
total = 0

for root, _, files in os.walk(base):
    for f in files:
        if not f.endswith(".txt"):
            continue

        path = os.path.join(root, f)

        with open(path, "r") as file:
            lines = file.readlines()

        if len(lines) == 0:
            empty += 1
            continue

        for line in lines:
            parts = line.strip().split()
            total += 1

            if len(parts) != 5:
                invalid += 1
                continue

            try:
                cls = int(parts[0])
                stats[cls] += 1
            except:
                invalid += 1

print("\n=== DATASET CHECK ===")
print("Arquivos vazios:", empty)
print("Linhas inválidas:", invalid)
print("Total de boxes:", total)

print("\n=== CLASSES ===")
for k, v in sorted(stats.items()):
    print(f"Classe {k}: {v}")