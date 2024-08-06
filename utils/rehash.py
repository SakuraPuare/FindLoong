from pathlib import Path

import imagehash
from PIL import Image

data_path = Path('./data/')


for folder in data_path.iterdir():
    if not folder.is_dir():
        continue
    print(folder)
    for file in folder.iterdir():
        if not file.is_file():
            continue
        img = Image.open(file)
        hash_ = imagehash.phash(img)
        if str(hash_) == file.stem:
            continue
        img.save(data_path / f"{hash_}.png", "PNG")
        file.unlink()
        print(f"Rehashed {file.stem} to {hash_}")