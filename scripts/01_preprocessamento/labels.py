import os

img_dir = "dataset_final/images/train"
lbl_dir = "dataset_final/labels/train"

imgs = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
lbls = [f for f in os.listdir(lbl_dir) if f.endswith('.txt')]

imgs.sort()
lbls.sort()

print(f"Imagens: {len(imgs)}")
print(f"Labels: {len(lbls)}")

for i in range(min(len(imgs), len(lbls))):
    img_name = os.path.splitext(imgs[i])[0]
    old_lbl_path = os.path.join(lbl_dir, lbls[i])
    new_lbl_path = os.path.join(lbl_dir, img_name + ".txt")

    print(f"Renomeando: {lbls[i]} → {img_name}.txt")

    os.rename(old_lbl_path, new_lbl_path)

print("✔️ Labels renomeados!")