import os
import torch
import time
from huggingface_hub import snapshot_download, login
from requests.exceptions import RequestException

# 设置模型保存路径
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models')
os.makedirs(MODEL_PATH, exist_ok=True)

# 检查环境变量中是否存在Hugging Face token
token = os.getenv("HF_TOKEN")
if not token:
    print("错误：环境变量HF_TOKEN未设置")
    print("请按照以下步骤操作：")
    print("1. 访问 https://huggingface.co/settings/tokens 获取你的token")
    print("2. 设置环境变量 HF_TOKEN，例如：")
    print("   - Linux/Mac: export HF_TOKEN='你的token'")
    print("   - Windows: set HF_TOKEN=你的token")
    exit(1)

# 验证token格式
if not token.startswith('hf_'):
    print("错误：无效的Hugging Face token格式")
    print("Token应该以'hf_'开头，请检查是否正确复制了完整的token")
    exit(1)

# 尝试登录Hugging Face
print("正在验证Hugging Face token...")
try:
    login(token=token)
    print("Token验证成功！")
except Exception as e:
    print("错误：Token验证失败")
    print("可能的原因：")
    print("1. Token已过期或被撤销")
    print("2. Token没有正确的访问权限")
    print(f"具体错误信息：{str(e)}")
    exit(1)

# 设置代理（如果需要）
proxy = "127.0.0.1:7890"
if proxy:
    print(f"使用代理: {proxy}")

# 下载模型
model_id = "stabilityai/stable-audio-open-1.0"
print(f"正在下载模型 {model_id} 到 {MODEL_PATH}...")

# 定义最大重试次数和重试间隔
MAX_RETRIES = 3
RETRY_DELAY = 5  # 秒

# 使用snapshot_download下载整个模型仓库
for attempt in range(MAX_RETRIES):
    try:
        if attempt > 0:
            print(f"第 {attempt + 1} 次重试下载...")
            time.sleep(RETRY_DELAY)

        snapshot_download(
            repo_id=model_id,
            local_dir=MODEL_PATH,
            local_dir_use_symlinks=False,  # 不使用符号链接，直接复制文件
            token=token,  # 使用token进行认证
            proxies={'http': proxy, 'https': proxy} if proxy else None,
            resume_download=True  # 支持断点续传
        )
        print("模型下载完成！")
        break
    except RequestException as e:
        if attempt < MAX_RETRIES - 1:
            print(f"下载失败: {str(e)}")
            print("正在准备重试...")
        else:
            print(f"下载失败，已达到最大重试次数: {str(e)}")
            print("请检查网络连接或代理设置后重试")
            exit(1)
    except Exception as e:
        print(f"发生未预期的错误: {str(e)}")
        print("请检查错误信息并解决问题后重试")
        exit(1)