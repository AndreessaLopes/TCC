import os

labels_dir = "dataset_final/labels"  # pasta principal

for split in ["train", "val", "test"]:
    split_path = os.path.join(labels_dir, split)

    for file in os.listdir(split_path):
        if file.endswith(".txt"):
            file_path = os.path.join(split_path, file)

            new_lines = []

            with open(file_path, "r") as f:
                lines = f.readlines()

            for line in lines:
                parts = line.strip().split()

                if len(parts) >= 5:
                    # força classe 0
                    parts[0] = "0"
                    new_lines.append(" ".join(parts))

            with open(file_path, "w") as f:
                f.write("\n".join(new_lines))

print("✔ Todas as classes convertidas para 'graos'")