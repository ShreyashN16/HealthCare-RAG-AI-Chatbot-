from PIL import Image, ImageOps
import numpy as np
import torch

def load_and_preprocess(img_path, img_size=224):
    img = Image.open(img_path)
    img = ImageOps.grayscale(img)
    img = img.resize((img_size, img_size))
    arr = np.array(img).astype('float32')/255.0
    arr = np.expand_dims(arr, 0)
    arr = np.repeat(arr, 3, 0)
    return torch.tensor(arr).float()
