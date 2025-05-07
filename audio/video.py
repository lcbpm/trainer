from huggingface_hub import snapshot_download
from stable_audio_tools import get_pretrained_model


# 把模型结构整理为 Hugging Face 缓存格式
local_dir = "/Users/test/traeproject/trainer/audio/models/models--stabilityai-stable-audio-open-1.0"

# snapshot_download 不会重新下载，如果已经存在就会使用本地缓存
# local_dir_use_symlinks=False 是为了让你看到完整文件
local_model_path = snapshot_download(
    repo_id="stabilityai/stable-audio-open-1.0",
    local_dir=local_dir,
    local_dir_use_symlinks=False,
    ignore_patterns=["*.md", "*.txt"]  # 忽略文档
)

model, model_config = get_pretrained_model(local_model_path)
