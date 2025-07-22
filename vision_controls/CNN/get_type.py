import torch 
model = torch.load('yolov5m.pt', map_location='cuda' if torch.cuda.is_available() else 'cpu')
model.eval()
print(type(model))