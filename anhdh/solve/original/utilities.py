import os
from PIL import Image
import numpy as np
import json

def get_id_by_path(path):
    name = os.path.basename(path)
    name = name.replace(".png", "")
    name = name.split("-")[2]
    return int(name)

def crop_img(folder_process, name, position):
    path = os.path.join(folder_process, f"m-{name}.png")
    x, y, x1, y1 = position
    img = Image.open(path).convert("RGBA")
    img_cropped = img.crop((x, y, x1, y1))
    img_width, img_height = img_cropped.size
    
    for i in range(img_width):
        for j in range(img_height):
            current_color = img_cropped.getpixel((i,j))
            if(current_color != (0, 0, 0, 0)):
                img_cropped.putpixel( (i,j), (0, 0, 255, 255))
    img_cropped = img_cropped.convert("RGB")
    img_arr = np.asarray(img_cropped)
    return img_arr[:, :, ::-1].copy()


def read_data_to_obj(folder_process, path):
    with open(os.path.join(folder_process, path)) as f:
        data = f.read()
    return json.loads(data)