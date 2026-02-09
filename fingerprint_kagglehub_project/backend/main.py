from fastapi import FastAPI,UploadFile,File
import shutil, os, kagglehub
from src.dataset import FingerprintDataset
from src.inference import InferenceEngine

app=FastAPI()
base_path=kagglehub.dataset_download('rajumavinmar/finger-print-based-blood-group-dataset')
cand=os.path.join(base_path,'dataset_blood_group')
data_path=cand if os.path.isdir(cand) else base_path
classes=FingerprintDataset(data_path).classes
engine=InferenceEngine('./model_checkpoints/model.pth', classes)

@app.get('/health')
def health(): return {'status':'ok'}

@app.post('/predict')
async def predict(file:UploadFile=File(...)):
    tp='temp_'+file.filename
    with open(tp,'wb') as bf: shutil.copyfileobj(file.file,bf)
    label,prob=engine.predict(tp); os.remove(tp)
    return {'label':label,'probabilities':prob}
