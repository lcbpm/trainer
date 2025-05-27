
from huggingface_hub import InferenceClient

proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}

client = InferenceClient(
    provider="fal-ai",
    api_key="3b67c7f7-706e-4c91-8102-fafcb434c3d5:2dd0c2dd0157152f1d898166e0652468",
    proxies=proxies
)

video = client.text_to_video(
    "A young man walking on the street",
    model="tencent/HunyuanVideo",
)