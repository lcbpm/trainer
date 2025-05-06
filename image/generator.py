import torch
from diffusers import StableDiffusionPipeline
from PIL import Image

# 使用 MPS 后端（Mac Apple Silicon）
torch_device = "mps" if torch.backends.mps.is_available() else "cpu"

# 加载预训练的稳定扩散模型
# model_id = "runwayml/stable-diffusion-v1-5"
model_id = "black-forest-labs/FLUX.1-dev"
pipe = StableDiffusionPipeline.from_pretrained(model_id,safety_checker=None)
pipe = pipe.to(torch_device)

# 文本提示词
# prompt = "a beautiful woman, ultra realistic, soft lighting, portrait, 4K, masterpiece, looking at the camera"
prompt = "a beautiful woman, ultra realistic, soft lighting, portrait, 4K, masterpiece, having sex"

# Set custom image dimensions (width and height)
width = 512  # Default is 512
height = 512  # Default is 512

# Generate image with specified dimensions
image = pipe(prompt, width=width, height=height).images[0]

# 保存或展示图像
image.save("output.png")
image.show()
