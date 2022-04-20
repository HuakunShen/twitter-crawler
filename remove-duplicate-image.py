import os
import numpy as np
from tqdm import tqdm
from PIL import Image
from imagededup.methods import PHash


def run(root: str):
    phasher = PHash()
    img = Image.open("/home/huakun/datasets/meinv/anime/IMG_0903.PNG")
    size = np.asarray(img.size)
    scale = 0.1
    new_size = (size * scale).astype(int)
    img.resize(new_size).resize(size).save("/home/huakun/datasets/meinv/anime/IMG_0903-to-remove.PNG")
    encodings = phasher.encode_images(image_dir=root)
    duplicates = phasher.find_duplicates(encoding_map=encodings)
    removed = set()
    file_removed = []
    for key, value in tqdm(duplicates.items()):
        if len(value):
            if key in removed:
                continue
            else:
                for v in value:
                    file_2_remove = f"{root}/{v}"
                    file_removed.append(file_2_remove)
                    os.remove(file_2_remove)
                    removed.add(v)


if __name__ == '__main__':
    import fire
    fire.Fire(run)
