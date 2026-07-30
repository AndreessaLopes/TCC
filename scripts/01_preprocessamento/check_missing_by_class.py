import os

base_images = "dataset/images"
base_labels = "dataset/labels"

classes = ["amarelas", "vermelhas"]

for cls in classes:
    img_dir = os.path.join(base_images, cls)
    label_dir = os.path.join(base_labels, cls)

    missing = []

    if not os.path.exists(img_dir):
        print(f"Pasta de imagens não encontrada: {img_dir}")
        continue

    for img in os.listdir(img_dir):
        if not img.endswith(".jpg"):
            continue

        label_file = img.replace(".jpg", ".txt")
        label_path = os.path.join(label_dir, label_file)

        if not os.path.exists(label_path):
            missing.append(img)

    print(f"\n=== CLASSE: {cls} ===")
    print("Sem anotação:", len(missing))

    for m in missing[:50]:  # mostra só os primeiros 50
        print(" -", m)