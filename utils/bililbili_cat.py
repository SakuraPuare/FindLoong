import os
import random
from pathlib import Path

import imagehash
from PIL import Image

src_path = '~/Pictures/Bilibili'
dst_path = './data/other'

# glob all files in src_path
src_path = Path(src_path).expanduser()
dst_path = Path(dst_path).expanduser()

count = 0

# os walk
walk = list(os.walk(src_path))
random.shuffle(walk)

for root, dirs, files in walk:
    for file in files:
        src_file = Path(root) / file

        # read image
        img = Image.open(src_file)

        # compute hash
        hash_ = imagehash.phash(img)

        # save image
        dst_file = dst_path / f"{hash_}.png"
        img.save(dst_file, "PNG")

        if count % 100 == 0:
            print(f"Processed {count} images")

        count += 1

    if count > 200:
        break
