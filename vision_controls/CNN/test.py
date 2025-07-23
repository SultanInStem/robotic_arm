import torch
model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolo/train/weights/best.pt')

# Inference on an image path
results = model('test.jpg')

# Print detected results
results.print()

# Show image with detections
results.show()

# Save results to runs/detect/exp by default
results.save()
