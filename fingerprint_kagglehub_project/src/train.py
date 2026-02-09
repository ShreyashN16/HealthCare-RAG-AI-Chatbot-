import kagglehub, os, torch
from torch.utils.data import DataLoader, random_split
import torch.nn as nn
from torch.optim import Adam
from dataset import FingerprintDataset
from model import get_model

def train_model():
    base_path = kagglehub.dataset_download('rajumavinmar/finger-print-based-blood-group-dataset')
    candidate = os.path.join(base_path, 'dataset_blood_group')
    data_path = candidate if os.path.isdir(candidate) else base_path
    print('Using dataset path:', data_path)
    ds = FingerprintDataset(data_path)
    tr=int(0.7*len(ds)); va=int(0.15*len(ds)); te=len(ds)-tr-va
    train_ds, val_ds, _ = random_split(ds,[tr,va,te])
    trl=DataLoader(train_ds,batch_size=8,shuffle=True)
    vall=DataLoader(val_ds,batch_size=8)
    dev='cuda' if torch.cuda.is_available() else 'cpu'
    model=get_model(num_classes=len(ds.classes)).to(dev)
    crit=nn.CrossEntropyLoss(); opt=Adam(model.parameters(),lr=1e-3)
    best=0
    for ep in range(3):
        model.train(); tl=0
        for x,y in trl:
            x,y=x.to(dev),y.to(dev)
            opt.zero_grad(); o=model(x); loss=crit(o,y); loss.backward(); opt.step(); tl+=loss.item()
        model.eval(); corr=tot=0
        with torch.no_grad():
            for x,y in vall:
                x,y=x.to(dev),y.to(dev)
                o=model(x); _,p=o.max(1)
                corr+=(p==y).sum().item(); tot+=y.size(0)
        acc=corr/tot; print('Ep',ep+1,'loss',tl/len(trl),'val',acc)
        if acc>best:
            best=acc; os.makedirs('../model_checkpoints',exist_ok=True)
            torch.save(model.state_dict(),'../model_checkpoints/model.pth')
if __name__=='__main__': train_model()
