import torch 
model = torch.load('yolo/my_model.pt', map_location='cuda' if torch.cuda.is_available() else 'cpu')
model.eval()
print(type(model))