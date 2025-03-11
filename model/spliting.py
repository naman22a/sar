import os
import shutil

data_dir = "data"
opt_dir = os.path.join(data_dir, "opt")
sar_dir = os.path.join(data_dir, "sar")
train_dir = os.path.join(data_dir, "train")
test_dir = os.path.join(data_dir, "test")

for split in ["train", "test"]:
    os.makedirs(os.path.join(train_dir, "opt"), exist_ok=True)
    os.makedirs(os.path.join(train_dir, "sar"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "opt"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "sar"), exist_ok=True)

def split_images(source_dir, train_dest, test_dest, split_ratio=0.8):
    images = sorted(os.listdir(source_dir)) 
    total_images = len(images)
    train_count = int(total_images * split_ratio)

    for img in images[:train_count]:
        shutil.move(os.path.join(source_dir, img), os.path.join(train_dest, img))

    for img in images[train_count:]:
        shutil.move(os.path.join(source_dir, img), os.path.join(test_dest, img))

split_images(opt_dir, os.path.join(train_dir, "opt"), os.path.join(test_dir, "opt"))
split_images(sar_dir, os.path.join(train_dir, "sar"), os.path.join(test_dir, "sar"))

print("Dataset split completed.")
