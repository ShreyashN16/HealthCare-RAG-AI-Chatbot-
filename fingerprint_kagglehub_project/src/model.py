import torch.nn as nn
from torchvision.models import mobilenet_v3_small

def get_model(num_classes=8, pretrained=True):
    if pretrained:
        model = mobilenet_v3_small(weights='IMAGENET1K_V1')
    else:
        model = mobilenet_v3_small(weights=None)
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, num_classes)
    return model
