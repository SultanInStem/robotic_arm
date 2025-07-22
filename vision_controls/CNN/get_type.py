import torch 
model = torch.load('yolo/train/weights/best.pt', map_location='cuda' if torch.cuda.is_available() else 'cpu')
model.eval()
print(type(model))