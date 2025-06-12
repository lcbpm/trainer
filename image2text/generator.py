import torch
from torchvision import models, transforms
from PIL import Image
import requests
from torchvision.models import resnet50, ResNet50_Weights

# 加载预训练模型
weights = ResNet50_Weights.DEFAULT
model = resnet50(weights=weights)
model.eval()

# 图像预处理
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],  # ImageNet 均值
        std=[0.229, 0.224, 0.225]    # ImageNet 标准差
    )
])

# 加载图像（可以替换为你本地的图片路径）
image_path = "/Users/test/traeproject/trainer/image2text/123.png"
image = Image.open(image_path).convert("RGB")
input_tensor = preprocess(image).unsqueeze(0)  # 增加 batch 维度

# 模型预测
with torch.no_grad():
    output = model(input_tensor)
    probabilities = torch.nn.functional.softmax(output[0], dim=0)

# 加载 ImageNet 的标签
labels_url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
labels = requests.get(labels_url).text.strip().split("\n")

# 输出前5个预测结果
top5_prob, top5_catid = torch.topk(probabilities, 1)
for i in range(top5_prob.size(0)):
    print(f"{labels[top5_catid[i]]}: {top5_prob[i].item():.4f}")
