import torch
from .model import get_model
from .preprocessing import load_and_preprocess

class InferenceEngine:
    def __init__(self, model_path, class_names):
        self.device='cuda' if torch.cuda.is_available() else 'cpu'
        self.model=get_model(num_classes=len(class_names))
        self.model.load_state_dict(torch.load(model_path,map_location=self.device))
        self.model.eval()
        self.class_names=class_names
    def predict(self, img_path):
        img=load_and_preprocess(img_path).unsqueeze(0).to(self.device)
        with torch.no_grad():
            out=self.model(img); prob=torch.softmax(out,1)[0]
            idx=prob.argmax().item()
            return self.class_names[idx], {self.class_names[i]:float(prob[i]) for i in range(len(prob))}
