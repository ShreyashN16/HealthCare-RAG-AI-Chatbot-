import os
from torch.utils.data import Dataset
from PIL import Image
import torchvision.transforms as T

class FingerprintDataset(Dataset):
    def __init__(self, root_dir, img_size=224):
        self.root_dir = root_dir
        self.classes = sorted([d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir,d))])
        self.files=[]
        self.transform = T.Compose([
            T.Grayscale(),
            T.Resize((img_size,img_size)),
            T.ToTensor(),
            T.Normalize(mean=[0.5], std=[0.5])
        ])
        for c in self.classes:
            p=os.path.join(root_dir,c)
            for f in os.listdir(p):
                if f.lower().endswith(('.png','.jpg','.jpeg','.bmp')):
                    self.files.append((os.path.join(p,f), c))
        self.label_to_idx={c:i for i,c in enumerate(self.classes)}
    def __len__(self):
        return len(self.files)
    def __getitem__(self, idx):
        fp, lab = self.files[idx]
        img = Image.open(fp)
        img = self.transform(img).repeat(3,1,1)
        return img, self.label_to_idx[lab]
